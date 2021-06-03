import argparse
from mininet.net import Mininet
from mininet.cli import CLI
from utils import *
from mininet.net import Intf
import pytest

DAEMONS = ["zebra", "staticd", "bgpd"]


def pytest_namespace():
    return {
        'net': None,
        'topo': None
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


def test_network_creation(topology):
    assert topology in ('server1', 'server2'), "Topology should be either server1 or server2"
    topo = get_topology(topology)
    pytest.topo = topo
    pytest.net = Mininet(topo=topo())


def test_assign_tunnel_interfaces(source_ip, remote_ip):
    assert remote_ip != source_ip
    create_tunnel(source_ip, remote_ip, 1000)
    for node_name in pytest.topo.TUNNELS.keys():
        for (int_name, session_id) in pytest.topo.TUNNELS[node_name]:
            create_session(int_name, session_id)
            Intf(int_name, node=pytest.net.getNodeByName(node_name))


def test_net_start():
    pytest.net.start()


def test_daemons_starting():
    for node in pytest.net.hosts:
        node.cmd(f'ip a del dev {node.name.replace("_", "")}-eth1 {node.IP()}')
        for daemon in DAEMONS:
            conf_file = os.path.join(os.getcwd(), pytest.topo.name, 'conf', daemon, f'{node.name}.conf')
            if node.name.startswith("h_") and daemon == "bgpd" or \
                    node.name.startswith("r_") and daemon == "staticd":
                if os.path.exists(conf_file):
                    AssertionError(f"{daemon} is found in {node.name} when it does not have to")
                else:
                    continue
            if os.path.exists(conf_file):
                start_daemon(node, daemon, conf_file)
            else:
                AssertionError(f"{daemon} is NOT found in {node.name}")

        if node.name.startswith('r'):
            # Enable IP forwarding
            node.cmd("sysctl -w net.ipv4.ip_forward=1")
            node.waitOutput()


def test_set_loopback_ip(topology):
    if topology == 'server1':
        node_name = 'r_1'
    else:
        node_name = 'r_3'
    node = pytest.net.getNodeByName(node_name)
    set_loopback_ip(node, '11.12.13.14/32')
    assert 'ip address 11.12.13.14/32' in get_running_config(node, 'zebra')


def test_internal_ping():
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
    if pytest.topo.name == 'server1':
        host_name = 'h_1'
        ip_to_test = '10.2.0.2'
    else:
        host_name = 'h_2'
        ip_to_test = '10.1.0.2'

    for i in range(30):
        if 'ms' in pytest.net.getNodeByName(host_name).cmd(f'ping {ip_to_test} -c 1')[:-10]:
            break
        time.sleep(1)
    else:
        raise AssertionError("Host cannot ping another host")


def test_socket_connection():
    from client_server_socket import client, server
    if pytest.topo.name == "server1":
        res = server((source_ip, 5000))
        print(res)
    elif pytest.topo.name == "server2":
        client((remote_ip, 5000), "MESSAGE!!!")


def test_clean():
    clean()
