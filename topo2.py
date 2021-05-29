from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI



####################
# Notes:
#   Put this file into ~/mininet/custom and name topo2.py
#
# Usage:
#   sudo python3 topo2.py     <- start mininet
#   pingall                   <- pings all to all (except s1)
#   dump                      <- lists information about the nodes, switches and controllers
#   exit                      <- exit from mininet
#   sudo mn -c                <- clears all previous mn connections
####################


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class Topo2(Topo):
    """
    Topology for right part
    h1(ping) - s1 - r1
                |
                r2
    """
    def build(self):
        "Create custom topo"

        # Add host, router, switch
        host1Ping = self.addHost("h1", ip='10.0.1.1/24')
        switch1 = self.addSwitch("s1")
        router1 = self.addHost("r1", cls=LinuxRouter, ip='10.0.1.3/24')
        router2 = self.addHost("r2", cls=LinuxRouter, ip='10.0.1.4/24')
        # Add links
        self.addLink(host1Ping, switch1)
        self.addLink(switch1,
                    router1,
                    intfName2='r1-eth1',
                    params2={'ip': '10.0.1.3/24'})
        self.addLink(switch1,
                    router2,
                    intfName2='r2-eth1',
                    params2={'ip': '10.0.1.4/24'})


def run():
    topo = Topo2()
    net = Mininet(topo=topo)

    net.start()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()

