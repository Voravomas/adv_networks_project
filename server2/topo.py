from mininet.topo import Topo
from LinuxRouter import LinuxRouter


class CustomTopology(Topo):
    """
    Topology for right part
    h1(ping) - s1 - r1
                |
                r2
    """
    TUNNELS = {'r_2': [('eth52', 2052)], 'r_3': [('eth31', 2013)]}
    name = 'server2'

    def build(self):
        "Create custom topo"

        # Add host, router, switch
        host2 = self.addHost("h_2")
        switch2 = self.addSwitch("s_2")
        router2 = self.addHost("r_2", cls=LinuxRouter)
        router3 = self.addHost("r_3", cls=LinuxRouter)

        # Add links
        self.addLink(host2, switch2,
                     intfName1='h2-eth1',
                     intfName2='s2-eth1')
        self.addLink(switch2,
                     router2,
                     intfName1='s2-eth2',
                     intfName2='r2-eth1')
        self.addLink(router2,
                     router3,
                     intfName1='r2-eth2',
                     intfName2='r3-eth1')
