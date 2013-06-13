#!/usr/bin/env python
###
# Copyright (c) 2013 - Charles "sparticvs" Timko
# original Copyright (c) 2010 - Charles "sparticvs" Timko
#  held on ruby file this is ported from
#
# This is Beerware License version 42
# <sparticvs@popebp.com> wrote this file. As long as you retain this
# notice you can do whatever you want with this stuff. If we meet
# someday, and you think this stuff is worth it, you can buy me a 
# beer in return.
###
from ConfigParser import SafeConfigParser
from netaddr import IPAddress
from subprocess import call
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

def doRule(**kwargs):
    cmds = CONFIG.items("crowbar")
    for (key,val) in cmds:
        if 'cmd' in key:
            call(val % kwargs)

def insertRule(proto, dport, sport, dip, sip):
    doRule(action=INSERT, proto=proto, dport=dport,
           sport=sport, dip=dip, sip=sip)

def deleteRule(proto, dport, sport, dip, sip):
    doRule(action=DELETE, proto=proto, dport=dport,
           sport=sport, dip=dip, sip=sip)

def __createParser():
    parser = ArgumentParser(description="Poke holes in the firewall with this crowbar")
    control = parser.add_argument_group("Controls")
    controlAction = control.add_mutually_exclusive_group(required=True)
    controlAction.add_argument("-l", "--list", action="store_const",
                               const="list", dest="action",
                               help="List rules managed by this script")
    controlAction.add_argument("-L", "--load", action="store_const",
                               const="load", dest="action",
                               help="Load all the rules into Iptables")
    controlAction.add_argument("-R", "--reload", action="store_const",
                               const="reload", dest="action",
                               help="Reload all the rules")
    controlAction.add_argument("-U", "--unload", action="store_const",
                               const="unload", dest="action",
                               help="Unload all the rules from Iptables")
    controlAction.add_argument("-i", "--insert", action="store_const",
                               const="insert", dest="action",
                               help="Insert a new rule")
    controlAction.add_argument("-d", "--delete", action="store_const",
                               const="delete", dest="action",
                               help="Delete an existing rule")
    control.add_argument("-p", "--protocol", choices=["tcp", "udp", "all"],
                         help="Specify networking protocol")
    control.add_argument("--src-port", type=int, metavar="PORT",
                         help="Source Port")
    control.add_argument("--dest-port", type=int, metavar="PORT",
                         help="Destination Port")
    control.add_argument("--src-ip", default=IPAddress("0.0.0.0"),
                         type=IPAddress, metavar="IP",
                         help="Source IP Address (default is `any')")
    control.add_argument("--dest-ip", type=IPAddress,
                         metavar="IP",
                         help="Destination IP Address (LAN port)")
    parser.add_argument("-C", "--config", default=CONFIG_LOC, type=str,
                        help="Use a specific config file")
    return parser

def main():
    parser = __createParser()
    args = parser.parse_args()
    print args
    conf = getConfig(args.config)
    #engine = create_engine("sqlite:///etc/crowbar/iptables.db" )


if  __name__ == "__main__":
    main()
