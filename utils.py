import os
import sys
import importlib


def get_topology(topology_name):
    root_dir = os.path.dirname(sys.modules['__main__'].__file__)

    # Check if the topology directory exists.
    topo_dir = os.path.join(root_dir, topology_name)
    if not os.path.exists(topo_dir):
        raise KeyError("Topology \"{}\" not supported".format(topology_name))

    # Extract the topology class.
    return importlib.import_module(f'{topology_name}/topo.py').CustomTopology
