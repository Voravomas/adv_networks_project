# Adding support of node migration for multimode mininet setup with config

## Presentation:
[Link](https://docs.google.com/presentation/d/1_XS8AXAUyR2-d6jJ0lx79-S-rPiI0-VbIMJfsxXo7tc/edit?usp=sharing)


## Structure
There are two topologies saved in directories `server1` and `server2`. Configuration of all the FRR daemons is stored in the `conf` directory
of each of 2 directories stated above. All the testing staff is the same for two servers. You should pass the argument `--topology` to
pytest to specify the selected one.


## Usage:
### Prerequisites:
* 2 VM's with installed `FRR`, `mininet` and `traceroute` and `python3.6+`
* Connection between the VM's (may be through the internet)
### Usage steps
* Clone this repository to both the VM's:  `git clone https://github.com/Voravomas/adv_networks_project`
* Run tests on both VM's but with different topologies
```sudo pytest-3 test_main.py --topology <TOPOLOGY> --source_ip <CURRENT_VM_IP_ADDRESS> --remote_ip <REMOTE_VM_IP_ADDRESS> [-x]```
  Where `<TOPOLOGY>` can be either `server1` or `server2` and `-x` makes tests stop after the first failure
#### NOTE: tests should be run within at most 30 seconds interval. Otherwise, they will not be able to synchronize


## Task:
1. Have at least 3 FRR routers in a cluster (2 routers on one server and one on another)<br/>
2. Verify connectivity between all routers<br/>
3. Do some runtime configuration on the routers. (IP, files, etc.)<br/>
4. Migrate one router from the server with two routers to another server.<br/>
5. Verify connectivity.<br/>
6. Do configuration in a way that 2 additional hosts won’t lose connectivity during node migration.<br/>


## Topology:
![Topology](other/adv-net-pr2.png?raw=true "Title")

## Plan:
1. **DONE** Create Basic Topology
2. **DONE** Create Server1 config and test it
3. **DONE** Create Server2 config and test it
4. **DONE** Test connectivity between servers
5. **DONE** Send running config from Server2 to Server1
6. **DONE** Migrate R3
7. **DONE** Write tests
8. **DONE** Create presentation

## Other notes:

* To add internet to Mininet: `sudo dhclient eth1`

* Add l2tp tunnel: `sudo ip l2tp add tunnel tunnel_id 1000 peer_tunnel_id 1000 ncap udp local <LOCAL_IP> remote <REMOTE_IP> udp_sport 60000 udp_dport 60000`
* Add session: `sudo ip l2tp add session name eth12 tunnel_id 1000 session_id 2000 peer_session_id 2000`
