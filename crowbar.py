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
        self.id = None
        self.proto = proto
        self.src_ip = int(sip)
        self.dest_ip = int(dip)
        self.src_port = sport
        self.dest_port = dport

    def __repr__(self):
        """Create a string representative of the objet"""
        tpl = (self.id, IPAddress(self.src_ip), IPAddress(self.dest_ip),
               self.src_port, self.dest_port, self.proto)
        return "<Rule('%s', '%s', '%s', '%s', '%s', '%s')>" % tpl

    def __str__(self):
        """Create a string in the table format"""
        output = "| {:^15} | {:^5} | {:^15} | {:^5} | {:^5} |"
        return output.format(IPAddress(self.src_ip), self.src_port,
                             IPAddress(self.dest_ip), self.dest_port,
                             self.proto)

    @staticmethod
    def __runCmds(**kwargs):
        """Build and execute the firewall commands"""
        cmds = getConfig().items("crowbar")
        for (key,val) in cmds:
            if 'cmd' in key:
                call(val % kwargs)

    def __buildAndRunCmd(self, action):
        """Build the commands off of this instance"""
        self.__runCmds(action=action, proto=self.proto, dport=self.dest_port,
                       sport=self.src_port, dip=IPAddress(self.dest_ip),
                       sip=IPAddress(self.src_ip))

    def delete(self):
        """Run the delete commands in IPTables"""
        if self.id is None:
            raise RuntimeError("Rule doesn't exist")
        self.__buildAndRunCmd(DELETE)

    def insert(self):
        """Run the insert commands in IPTables"""
        self.__buildAndRunCmd(INSERT)

def getEngine():
    """Singleton to return the db engine"""
    global ENGINE
    if ENGINE is None:
        ENGINE = create_engine("%s:///%s" % (getConfig().get("database",
                                                            "driver"),
                                            getConfig().get("database", "db")))
    return ENGINE

def getSession():
    """Singleton to return the db session"""
    global SESSION
    if SESSION is None:
        Session = sessionmaker(bind=getEngine())
        SESSION = Session()
    return SESSION

def getAllRules():
    """Return a collection of all rules"""
    sess = getSession()
    return sess.query(Rule).all()

def getConfig(cfgFile=None):
    """Singleton to return the configuration"""
    global CONFIG
    if CONFIG is None:
        CONFIG = SafeConfigParser()
        CONFIG.read([cfgFile])
    return CONFIG

def insertRule(proto, dport, sport, dip, sip):
    """Insert arule into the table and system"""
    sess = getSession()
    rule = Rule(proto, dport, sport, dip, sip)
    sess.add(rule)
    rule.insert()
    sess.commit()

def deleteRule(proto, dport, sport, dip, sip):
    """Delete a rule from the Table and system"""
    sess = getSession()
    rule = sess.query(Rule).filter(Rule.proto == proto,
                                   Rule.dest_port == dport,
                                   Rule.src_port == sport,
                                   Rule.dest_ip == dip,
                                   Rule.src_ip == sip).one()
    sess.delete(rule)
    rule.delete()
    sess.commit()

def deleteRules(rules):
    """Delete a collection of rules from IPTables"""
    for rule in rules:
        rule.delete()

def printRules():
    """Print out the firewall rules we are maintaining"""
    rules = getAllRules()
    print "+-----------------+-------+-----------------+-------+-------+"
    print "|     Src IP      | Port  |     Dest IP     | Port  | Proto |"
    print "+-----------------+-------+-----------------+-------+-------+"
    for rule in rules:
        print rule
    print "+-----------------+-------+-----------------+-------+-------+"

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

def loadRules():
    """Load all rules in the db into iptables"""
    rules = getAllRules()
    for rule in rules:
        rule.insert()

def unloadRules():
    """Delete all the rules in the db from iptables"""
    rules = getAllRules()
    for rule in rules:
        rule.delete()

def main():
    """Main subroutine to handle all basic tasks"""
    parser = __createParser()
    args = parser.parse_args()
    # Populate the configuration the first time
    getConfig(args.config)
    Base.metadata.create_all(bind=getEngine())

    if args.action is "list":
        printRules()
    elif args.action is "load":
        loadRules()
    elif args.action is "reload":
        unloadRules()
        loadRules()
    elif args.action is "unload":
        unloadRules()
    elif args.action is "insert":
        insertRule(args.protocol, args.dest_port, args.src_port, args.dest_ip, args.src_ip)
    elif args.action is "delete":
        deleteRule(args.protocol, args.dest_port, args.src_port, args.dest_ip, args.src_ip)

if  __name__ == "__main__":
    main()
