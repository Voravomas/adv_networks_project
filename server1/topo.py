from mininet.topo import Topo
from mininet.node import Node
from LinuxRouter import LinuxRouter

class CustomTopology(Topo):
    """
    Topology for left part
    h1(ping) - s1 - r1
    """

    TUNNELS = {'r_1': [('eth13', 2013)], 'r_5': [('eth52', 2052)]}
    name = 'server1'

    def build(self):
        """Create custom topo"""

        # Add host, router, switch
        host1Ping = self.addHost("h_1")
        switch1 = self.addSwitch("s_1")
        router1 = self.addHost("r_1", cls=LinuxRouter)
        router4 = self.addHost("r_4", cls=LinuxRouter)
        router5 = self.addHost("r_5", cls=LinuxRouter)

        # Add links
        self.addLink(host1Ping, switch1,
                     intfName2='s1-eth1',
                     intfName1='h1-eth1')

        self.addLink(switch1,
                     router1,
                     intfName1='s1-eth2',
                     intfName2='r1-eth1')

        self.addLink(router1, router4,
                     intfName1='r1-eth2',
                     intfName2='r4-eth1')
        self.addLink(router4, router5,
                     intfName1='r4-eth2',
                     intfName2='r5-eth1')



