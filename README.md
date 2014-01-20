**NOTICE:** *This project has reached end-of-life. With nftables being officially added to the Linux Kernel in 3.13, I will no longer be supporting* crowbar *.  I will instead work on a new tool that will compile rules immediately into nftables byte-code.*

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


future work
------------------------
<del>The future of Netfilter is undecided at this point. There is a lot of code work going on by two separate camps
that is causing some upheaval in the community. There is XTables2 which is aiming at replacing Netfilter entirely
and removing all the protocol awareness code.  Then there is NFTables which is built by the Netfilter's maintainer
and is supposed to give an upgrade to Netfilter and swap out iptables for a more robust filtering engine that is
also protocol unaware.  So here we are, two camps with the same goal but separate routes being taken. I will
pick a camp after reviewing both of them and work with them and hopefully get the next iteration of this tool
to be included with their utilities release.</del>
