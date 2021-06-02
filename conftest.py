import pytest


def pytest_addoption(parser):
    parser.addoption("--topology", action="store", default="server1",
                     help="Topology of given node (server1 or server2)")
    parser.addoption("--source_ip", action="store", default="0.0.0.0", help="IP address of current machine")
    parser.addoption("--remote_ip", action="store", default="0.0.0.0", help="IP address of the remote machine")
