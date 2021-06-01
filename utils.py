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
    return importlib.import_module(f'{topology_name}.topo').CustomTopology


def _remove_tunnel(tunnel_id):
    os.system(f'ip l2tp del tunnel tunnel_id {tunnel_id}')


def create_tunnel(local_ip, remote_ip, tunnel_id=1000):
    _remove_tunnel(tunnel_id)
    os.system(
        f'ip l2tp add tunnel tunnel_id {tunnel_id} peer_tunnel_id {tunnel_id} encap udp local {local_ip} remote {remote_ip} udp_sport 60000 udp_dport 60000')


def create_session(int_name, session_id=2000, tunnel_id=1000):
    os.system(
        f'ip l2tp add session name {int_name} tunnel_id {tunnel_id} session_id {session_id} peer_session_id {session_id}')
