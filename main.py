import argparse
import os
import sys

from mininet.net import Mininet
from mininet.cli import CLI
from utils import get_topology, create_tunnel, create_session
from mininet.net import Intf

FRR_BIN_DIR = "/usr/lib/frr"
DAEMONS = ["zebra", "staticd", "bgpd"]


def start_daemon(node, daemon, conf_file):
    """Start one FRR daemon on a given node.

    """
    node.cmd("{bin_dir}/{daemon}"
             " -f {conf_file}"
             " -d"
             " -i /tmp/{node_name}-{daemon}.pid"
             " > /tmp/{node_name}-{daemon}.out 2>&1"
             .format(bin_dir=FRR_BIN_DIR,
                     daemon=daemon,
                     conf_file=conf_file,
                     node_name=node.name))
    node.waitOutput()


def clean():
    """Clean all state left over from a previous experiment.

    """
    os.system("rm -f /tmp/R*.log /tmp/R*.pid /tmp/R*.out")
    os.system("rm -f /tmp/h*.log /tmp/h*.pid /tmp/h*.out")
    os.system("mn -c >/dev/null 2>&1")
    os.system("killall -9 {} > /dev/null 2>&1"
              .format(' '.join(os.listdir(FRR_BIN_DIR))))


def run(topology, topology_name, daemons, source_ip, remote_ip):
    """Start a network experiment.

    """

    # Clean up any state from previous experiments.
    clean()
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)

    # Start Mininet.
    net = Mininet(topo=topology())

    create_tunnel(source_ip, remote_ip, 1000)
    for node_name in topology.TUNNELS.keys():
        for (int_name, session_id) in topology.TUNNELS[node_name]:
            create_session(int_name, session_id)
            Intf(int_name, node=net.getNodeByName(node_name))

    net.start()

    for node in net.hosts:
        print(f'{node.name}: {node.IP()}')
        node.cmd(f'ip a del dev {node.name.replace("_", "")}-eth1 {node.IP()}')
        for daemon in daemons:
            conf_file = os.path.join(root_dir, topology_name, 'conf', daemon, f'{node.name}.conf')
            if os.path.exists(conf_file):
                start_daemon(node, daemon, conf_file)
            else:
                print(f'Could not find conf/{daemon}/{node.name}.conf file')

        if node.name.startswith('r'):
            # Enable IP forwarding
            node.cmd("sysctl -w net.ipv4.ip_forward=1")
            node.waitOutput()


    with open('tmp', 'w') as f:
        print('''cisco
enable
cisco
conf t
int lo
ip a 10.10.10.10/32
exit
exit
exit
''', file=f)
    print(net.getNodeByName('r_3').cmd('telnet localhost 2601 < tmp > running 2>&1'))

    CLI(net)
    net.stop()
    if daemons:
        os.system("killall -9 {}".format(' '.join(daemons)))


def main():
    """Route 0 entry point.

    """

    parser = argparse.ArgumentParser(
        description='Launch an FRR network experiment in Mininet.')
    parser.add_argument('-t', '--topology', required=True,
                        help='the topology of the network')
    parser.add_argument('-sip', '--source-ip', required=True, help='This machine IP address')
    parser.add_argument('-rip', '--remote-ip', required=True, help='Remote machine IP address')
    args = parser.parse_args()

    run(get_topology(args.topology), args.topology, DAEMONS, args.source_ip, args.remote_ip)


if __name__ == "__main__":
    main()
