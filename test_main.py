from mininet.net import Mininet
from utils import *
from mininet.net import Intf
import pytest
from LinuxRouter import LinuxRouter

DAEMONS = ["zebra", "staticd", "bgpd"]


def pytest_namespace():
    return {
        'net': None,
        'topo': None,
        'bgp_conf': '',
        'zebra_conf': ''
    }


@pytest.fixture
def topology(request):
    return request.config.getoption("--topology")


@pytest.fixture
def source_ip(request):
    return request.config.getoption("--source_ip")


@pytest.fixture
def remote_ip(request):
    return request.config.getoption("--remote_ip")


def test_init_clean():
    clean()


def test_network_creation(topology):
    assert topology in ('server1', 'server2'), "Topology should be either server1 or server2"
    topo = get_topology(topology)
    pytest.topo = topo
    pytest.net = Mininet(topo=topo())


def test_assign_tunnel_interfaces(source_ip, remote_ip):
    print("Assigning tunnel interfaces to nodes...")
    assert remote_ip != source_ip
    create_tunnel(source_ip, remote_ip, 1000)
    for node_name in pytest.topo.TUNNELS.keys():
        for (int_name, session_id) in pytest.topo.TUNNELS[node_name]:
            create_session(int_name, session_id)
            Intf(int_name, node=pytest.net.getNodeByName(node_name))


def test_net_start():
    print("Starting the network...")
    pytest.net.start()


def test_daemons_starting():
    print("Starting all the daemons in the network...")
    for node in pytest.net.hosts:
        node.cmd(f'ip a del dev {node.name.replace("_", "")}-eth1 {node.IP()}')
        for daemon in DAEMONS:
            conf_file = os.path.join(os.getcwd(), pytest.topo.name, 'conf', daemon, f'{node.name}.conf')
            if node.name.startswith("h_") and daemon == "bgpd" or \
                    node.name.startswith("r_") and daemon == "staticd":
                continue
            assert os.path.exists(conf_file), f"{daemon} is found in {node.name} when it does not have to"
            start_daemon(node, daemon, conf_file)

        if node.name.startswith('r'):
            # Enable IP forwarding
            node.cmd("sysctl -w net.ipv4.ip_forward=1")
            node.waitOutput()


def test_set_loopback_ip(topology):
    print('Setting a loopback interface address to the router that will be migrated...')
    if topology == 'server1':
        node_name = 'r_1'
    else:
        node_name = 'r_3'
    node = pytest.net.getNodeByName(node_name)
    set_loopback_ip(node, '11.12.13.14/32')
    assert 'ip address 11.12.13.14/32' in get_running_config(node, 'zebra')


def test_internal_ping():
    print("Testing pings between nodes in each network...")
    if pytest.topo.name == 'server1':
        host_name = 'h_1'
        ip_to_test = '10.100.1.5'
    else:
        host_name = 'h_2'
        ip_to_test = '10.100.2.4'

    for i in range(5):
        if 'ms' in pytest.net.getNodeByName(host_name).cmd(f'ping {ip_to_test} -c 1')[:-10]:
            break
        time.sleep(1)
    else:
        raise AssertionError("Host cannot ping a router")


def test_external_ping():
    print("Testing pings between hosts in different networks...")
    if pytest.topo.name == 'server1':
        host_name = 'h_1'
        ip_to_test = '10.2.0.2'
    else:
        host_name = 'h_2'
        ip_to_test = '10.1.0.2'

    if not ping_test(pytest.net.getNodeByName(host_name), ip_to_test, 30):
        raise AssertionError("Host cannot ping another host")


def test_traceroute():
    print("Checking that traffic between hosts goes through the router 3...")
    if pytest.topo.name == 'server1':
        assert '10.0.13.2' in pytest.net.getNodeByName('h_1').cmd(
            'traceroute 10.2.0.2'), 'Traffic does not go through router 3'
    else:
        assert '10.0.23.2' in pytest.net.getNodeByName('h_2').cmd(
            'traceroute 10.1.0.2'), 'Traffic does not go through router 3'


def test_migrated_router_get_conf():
    if pytest.topo.name == 'server1':
        return
    print('Getting running configuration of router to be migrated...')
    pytest.bgp_conf = get_running_config(pytest.net.getNodeByName('r_3'), 'bgpd')
    pytest.zebra_conf = get_running_config(pytest.net.getNodeByName('r_3'), 'zebra')

    # Simple check whether the configuration os present at least
    assert len(pytest.bgp_conf) > 10 and len(pytest.zebra_conf) > 10


def test_socket_connection(source_ip, remote_ip):
    print('Checking socket connection between servers and synchronizing them...')
    from client_server_socket import client, server
    # IT WORKS!
    s_ip = source_ip
    if pytest.topo.name == "server1":
        res = ''
        for i in range(10):
            try:
                res = server((s_ip, 5000))
            except Exception as e:
                time.sleep(1)
                continue
            else:
                break
        else:
            raise AssertionError("Could not connect to remote server...")
        assert res == "TEST"
    elif pytest.topo.name == "server2":
        client((remote_ip, 5000), "TEST")


def test_send_config(source_ip, remote_ip):
    from client_server_socket import client, server
    if pytest.topo.name == 'server1':
        print('Receiving the config files to the other server...')
        config = server((source_ip, 5000))
        assert len(config) > 10
        assert 'ZEBRA:' in config
        pytest.bgp_conf = config[:config.index('ZEBRA')]
        pytest.zebra_conf = config[config.index('ZEBRA:') + 6:]
    else:
        print('Sending the config files to the other server...')
        time.sleep(3)
        client((remote_ip, 5000), f'{pytest.bgp_conf}\n\nZEBRA:\n{pytest.zebra_conf}')


def test_remove_router():
    os.system('ip l2tp del session session_id 2013 tunnel_id 1000')
    if pytest.topo.name == 'server1':
        interface = pytest.net.getNodeByName('r_1').intf('eth13')
        pytest.net.getNodeByName('r_1').delIntf(interface)
        interface.delete()
        return
    print('Removing the router...')
    interface = pytest.net.getNodeByName('r_2').intf('r2-eth2')
    pytest.net.getNodeByName('r_2').delIntf(interface)
    interface.delete()
    pytest.net.delNode(pytest.net.getNodeByName('r_3'))

    try:
        pytest.net.getNodeByName('r_3')
    except:
        pass
    else:
        raise AssertionError('Router was not deleted')


def test_connectivity():
    if pytest.topo.name == 'server2':
        print('Checking that the traffic still goes through...')
        if not ping_test(pytest.net.getNodeByName('h_2'), '10.1.0.2', 10):
            raise AssertionError("Host cannot ping another host")


def test_create_new_router():
    if pytest.topo.name == 'server2':
        return
    print('Creating the new router...')
    with open('r_3_bgp_tmp.conf', 'w') as f:
        f.write(pytest.bgp_conf)
    with open('r_3_zebra_tmp.conf', 'w') as f:
        f.write(pytest.zebra_conf)
    pytest.net.addHost('r_3', cls=LinuxRouter)


def test_link_host():
    print('Linking needed nodes and interfaces ....')
    if pytest.topo.name == 'server2':
        time.sleep(1)
        create_session('r2-eth2', 2023)
        time.sleep(1)
        Intf('r2-eth2', node=pytest.net.getNodeByName('r_2'))

        return

    time.sleep(1)

    create_session('r3-eth1', 2023)
    Intf('r3-eth1', node=pytest.net.getNodeByName('r_3'))
    pytest.net.addLink(pytest.net.getNodeByName('r_1'), pytest.net.getNodeByName('r_3'),
                       intfName1='eth13',
                       intfName2='eth31')


def test_run_daemons_on_router():
    print('Starting daemons on the migrated router...')
    if pytest.topo.name == 'server2':
        return
    start_daemon(pytest.net.getNodeByName('r_3'), 'zebra', 'r_3_zebra_tmp.conf')
    start_daemon(pytest.net.getNodeByName('r_3'), 'bgpd', 'r_3_bgp_tmp.conf')


def test_connectivity_to_router_loopback():
    print('Trying to ping the migrated router...')
    if pytest.topo.name == 'server1':
        host_name = 'h_1'
        if not ping_test(pytest.net.getNodeByName(host_name), '10.100.2.4', 10):
            raise AssertionError(f"Host {host_name} cannot ping the migrated router")


def test_router_config_saved():
    print('Checking whether the configuration was migrated properly...')
    if pytest.topo.name == 'server2':
        return
    running_config = get_running_config(pytest.net.getNodeByName('r_3'), 'zebra')
    assert 'ip address 11.12.13.14/32' in running_config, 'Running config is different on migrated router...'


def test_connectivity2():
    print("Testing pings between hosts in different networks...")
    if pytest.topo.name == 'server1':
        host_name = 'h_1'
        ip_to_test = '10.2.0.2'
    else:
        host_name = 'h_2'
        ip_to_test = '10.1.0.2'

    if not ping_test(pytest.net.getNodeByName(host_name), ip_to_test, 30):
        raise AssertionError("Host cannot ping another host")


def test_end_clean():
    # Giving the other server chance to finish tests
    time.sleep(5)
    print('Cleanup...')
    clean()
