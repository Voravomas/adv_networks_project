"""The experiment module is responsible for collecting topology and scenario
settings.

"""

import importlib
import os
import sys


class Experiment:
    """Class that describes a network experiment.  An experiment is a
    particular combination of topology and scenario.

    A topology determines the nodes and their links in the network.

    A scenario determines which daemons need to be started on which nodes and
    the location of the relevant config files.

    """

    def __init__(self, topology, scenario):
        root_dir = os.path.dirname(sys.modules['__main__'].__file__)

        # Check if the topology directory exists.
        topo_dir = os.path.join(root_dir, "topology/{}".format(topology))
        if not os.path.exists(topo_dir):
            raise KeyError("Topology \"{}\" not supported".format(topology))

        # Extract the topology class.
        self._topo = importlib.import_module('topology.{}.topo'.format(topology)).NetTopo

        # Initialise list of daemons.
        self.daemons = []


        for daemon in ["zebra", "staticd", "bgpd"]:
            if not hasattr(self, daemon):
                self._get_daemon_nodes(topo_dir, daemon)

    def _get_daemon_nodes(self, parent_dir, daemon):
        # Each daemon entry should be a directory.
        daemon_dir = os.path.join(parent_dir, daemon)
        if os.path.exists(daemon_dir) and os.path.isdir(daemon_dir):
            # Make sure zebra is always first on the list of daemons.
            if daemon == "zebra":
                self.daemons.insert(0, daemon)
            else:
                self.daemons.append(daemon)
            setattr(self, daemon, set())
            setattr(self, "{}_conf".format(daemon), daemon_dir)

            # Each node running this daemons must have a conf file in the
            # daemon directory called <node_name>.conf.
            for conf in os.listdir(daemon_dir):
                # Make sure we're only dealing with conf files.
                if conf.endswith(".conf"):
                    getattr(self, daemon).add(conf.split('.')[0])

    @property
    def topo(self):
        """The topology of this scenario.

        """
        return self._topo

    @property
    def script(self):
        """The script to run after the daemons have been started.

        """
        return self._scenario_script
