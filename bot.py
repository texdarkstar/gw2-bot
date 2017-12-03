import telnetlib
import socket
import time
import threading
import re
from constants import *


class Trigger(object):
    def __init__(self, regex, func, gag=False):
        '''func takes three args: func(Robot, string, (caputuring, groups, in, string))'''
        self.regex = regex
        self.func = func
        self.gag = gag


class Robot(object):
    def __init__(self, username, password, silent=False, terminaltype="PYBOT-v2.0"):
        self.host = "godwars2.org"
        self.port = 3000
        self.terminaltype = terminaltype
        self.username = username
        self.password = password
        self.silent = silent
        self.connection = None
        self.connected = False
        self.triggers = {}

        self.init()


    def init(self):
        pass


    def execute(self, string):
        self.connection.write(string + "\n")


    def add_trigger(self, regex, func, name, gag=False):
        self.triggers[name] = Trigger(regex=regex, func=func, gag=gag)


    def connect(self):
        if not self.connected:
            try:
                self.connection = telnetlib.Telnet(self.host, self.port)
                time.sleep(.2)
                self.connection.sock.sendall(IAC + WILL + TTYPE)
                self.connection.sock.sendall(IAC + SB + TTYPE + IS + self.terminaltype + IAC + SE)

                self.connection.write("load %s %s\r\n" % (self.username, self.password))
                print "%s connected successfuly" % self.username
                self.connected = True

            except socket.error:
                print "%s unable to connect" % self.username

        elif self.connected:
            print "%s is already connected." % self.username


    def format_ansi(self, string):
        escape1 = re.compile(r'\x1b\[\d+m')
        escape2 = re.compile(r'\x1b\[\d+;\d+m')

        string = escape1.sub('', string)
        string = escape2.sub('', string)
        return string


    def loop(self):
        while self.connected:
            data = self.format_ansi(self.connection.read_until("\n"))
            if data not in ["\n", "\r\n"]:
                data = data.rstrip()

            for trigger in self.triggers.values():
                matches = re.match(trigger.regex, data)
                if matches:
                    trigger.func(self, data, matches.groups())
                    if not (trigger.gag) and not (self.silent):
                        print data
                else:
                    if not (self.silent):
                        print data
