#!/usr/bin/env python2.7
###
# 
# 
###
from ConfigParser import SafeConfigParser
from netaddr import IPAddress
from argparse import ArgumentParser, FileType
from sqlalchemy import create_engine

INSERT = "-I"
DELETE = "-D"

CONFIG_LOC = "/etc/crowbar/crowbar.cfg"
CONFIG = None
ENGINE = None

def getEngine():
    global ENGINE
    if ENGINE is None:
        ENGINE = create_engine("%s://%s" % (CONFIG.get("database", "driver"),
                                            CONFIG.get("database", "db")))
    return ENGINE

def getConfig(cfgFile):
    global CONFIG
    if CONFIG is None:
        CONFIG = SafeConfigParser()
        CONFIG.read([cfgFile])
    return CONFIG
    

def __createParser():
    parser = ArgumentParser(description="Poke holes in the firewall with this crowbar")
#    actionGroup = parser.add_mutually_exclusive_group(required=True)
#    controlGroup = actionGroup.add_argument_group("Control Actions")
#    controlActionGroup = controlGroup.add_mutually_exclusive_group()
    control = parser.add_argument_group("Controls")
    controlAction = control.add_mutually_exclusive_group(required=True)
#    actionGroup.add_argument("-l", "--list", help="List rules managed by this script")
#    actionGroup.add_argument("-L", "--load", help="Load all the rules into Iptables")
#    actionGroup.add_argument("-R", "--reload", help="Reload all the rules")
#    actionGroup.add_argument("-U", "--unload", help="Unload all the rules from Iptables")
    controlAction.add_argument("-i", "--insert", action="store_true", help="Insert a new rule")
    controlAction.add_argument("-d", "--delete", action="store_true", help="Delete an existing rule")
    control.add_argument("-p", "--protocol", choices=["tcp", "udp", "all"],
                         help="Specify networking protocol")
    control.add_argument("--src-port", type=int, help="Source Port")
    control.add_argument("--dest-port", type=int, help="Destination Port")
    control.add_argument("--src-ip", default=IPAddress("0.0.0.0") , type=IPAddress, help="Source IP Address [default is `any']")
    control.add_argument("--dest-ip", type=IPAddress,
                         help="Destination IP Address (connected to the LAN port)")
    parser.add_argument("-C", "--config", default=CONFIG_LOC, type=str, help="Use a specific config file")
    return parser

def main():
    parser = __createParser()
    args = parser.parse_args()
    print args
    conf = getConfig(args.config)
    print conf.get("crowbar", "wan_if")
    #engine = create_engine("sqlite:///etc/crowbar/iptables.db" )


if  __name__ == "__main__":
    main()
