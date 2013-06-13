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
from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

INSERT = "-I"
DELETE = "-D"

CONFIG_LOC = "/etc/crowbar/crowbar.cfg"
CONFIG = None
ENGINE = None
SESSION = None

Base = declarative_base()

class Rule(Base):
    __tablename__ = "Rule"
    __table_args__ = {'sqlite_autoincrement': True}


    id = Column(Integer, primary_key=True)
    src_ip = Column(Integer)
    dest_ip = Column(Integer)
    src_port = Column(Integer)
    dest_port = Column(Integer)
    proto = Column(String)

    def __init__(self, proto, dport, sport, dip, sip):
        self.proto = proto
        self.src_ip = int(sip)
        self.dest_ip = int(dip)
        self.src_port = sport
        self.dest_port = dport

    def __repr__(self):
        return "<Rule('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.id,
                                                               self.src_ip,
                                                               self.dest_ip,
                                                               self.src_port,
                                                               self.dest_port,
                                                               self.proto)


def getEngine():
    global ENGINE
    if ENGINE is None:
        ENGINE = create_engine("%s:///%s" % (getConfig().get("database",
                                                            "driver"),
                                            getConfig().get("database", "db")))
    return ENGINE

def getSession():
    global SESSION
    if SESSION is None:
        Session = sessionmaker(bind=getEngine())
        SESSION = Session()
    return SESSION

def getRules():
    sess = getSession()
    print sess.query(Rule).all()

def getConfig(cfgFile=None):
    global CONFIG
    if CONFIG is None:
        CONFIG = SafeConfigParser()
        CONFIG.read([cfgFile])
    return CONFIG

def doRule(**kwargs):
    cmds = getConfig.items("crowbar")
    for (key,val) in cmds:
        if 'cmd' in key:
            call(val % kwargs)

def insertRule(proto, dport, sport, dip, sip):
    sess = getSession()
    rule = Rule(proto, dport, sport, dip, sip)
    sess.add(rule)
    print rule
    sess.commit()
"""
    doRule(action=INSERT, proto=proto, dport=dport,
           sport=sport, dip=dip, sip=sip)
"""
def deleteRule(proto, dport, sport, dip, sip):
    doRule(action=DELETE, proto=proto, dport=dport,
           sport=sport, dip=dip, sip=sip)

def __createParser():
    parser = ArgumentParser(description="NAT Port Forwarding Tool")
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
    # Populate the configuration the first time
    getConfig(args.config)
    Base.metadata.create_all(bind=getEngine())

    if args.action is "list":
        getRules()
        pass
    elif args.action is "load":
        pass
    elif args.action is "reload":
        pass
    elif args.action is "unload":
        pass
    elif args.action is "insert":
        insertRule(args.protocol, args.dest_port, args.src_port, args.dest_ip, args.src_ip)
        pass
    elif args.action is "delete":
        pass

if  __name__ == "__main__":
    main()
