crowbar
=======

Simple Firewall/NAT/Gateway control script


requirements
------------
  * Python 2.7
  * netaddr module
  * sqlalchemy module

usage
-----
    usage: crowbar.py [-h] [-l] [-L] [-R] [-U] [-i] [-d] [-p {tcp,udp,all}]
                      [--src-port PORT] [--dest-port PORT] [--src-ip IP]
                      [--dest-ip IP] [-C CONFIG]
    
    NAT Port Forwarding Tool
    
    optional arguments:
      -h, --help            show this help message and exit
      -C CONFIG, --config CONFIG
                          Use a specific config file
    
    Controls:
      -l, --list            List rules managed by this script
      -L, --load            Load all the rules into Iptables
      -R, --reload          Reload all the rules
      -U, --unload          Unload all the rules from Iptables
      -i, --insert          Insert a new rule
      -d, --delete          Delete an existing rule
      -p {tcp,udp,all}, --protocol {tcp,udp,all}
                            Specify networking protocol
      --src-port PORT       Source Port
      --dest-port PORT      Destination Port
      --src-ip IP           Source IP Address (default is `any')
      --dest-ip IP          Destination IP Address (LAN port)
