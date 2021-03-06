import telnetlib
import socket
import time
import threading
import re
from constants import *


class Trigger(object):
    def __init__(self, client, regex, func, gag=False, keepmatching=False, priority=1):
        '''func takes three args: func(Robot, string, (caputuring, groups, in, string))'''
        self.client = client
        self.regex = regex
        self.func = func
        self.gag = gag
        self.keepmatching = keepmatching
        self.priority = priority


    def run(self, string, matches):
        self.func(self.client, string, matches)


class Timer(object):
    def __init__(self, client, interval, func, max_runs=1):
        '''Timer object.
        client is a reference to the running client instance.
        interval is how often the timer will fire.
        func is the target func for the timer to run.
        max_runs is the maximum number of times the timer will fire.
        if max_runs is None, the timer will fire forever.'''
        self.client = client
        self.interval = interval
        self.func = func
        self.thread = threading.Thread(target=self._func)
        self.thread.daemon = True
        self.runs = 0
        self.max_runs = max_runs
        self.isvalid = True


    def start(self):
        if not self.thread.isAlive():
            self.thread.start()

    def stop(self):
        self.isvalid = False

    def _func(self):
        while self.valid():
            if not self.valid():
                break
                
            time.sleep(self.interval)
            self.runs += 1
            self.func(self.client, self)


    def valid(self):
        '''Returns False if the timer isn't valid to run (hit max_runs or the thread already died)'''
        if (not self.isvalid and self.max_runs == 0):
            return False
        elif (self.runs >= self.max_runs):
            return False
        elif (not self.thread.isAlive()):
            return False
        else:
            return True


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
        self.timers = {}

        self.init()


    def init(self):
        pass

    def execute(self, string, delim=";"):
        self.connection.write("\n".join(string.split(delim)) + "\n")


    def add_trigger(self, regex, func, name, gag=False, keepmatching=False, priority=1):
        self.triggers[name] = Trigger(client=self, regex=regex, func=func, gag=gag, keepmatching=keepmatching, priority=priority)


    def add_timer(self, interval, func, max_runs=1, name=None):
        timer = Timer(client=self, interval=interval, func=func, max_runs=max_runs)
        timer.start()

        if not name:
            name = "timer-%d" % int(len(self.timers.keys()) + 1)

        self.timers[name] = timer

        #  for timername in self.timers.keys():
            #  if not self.timers[timername].valid():
                #  del self.timers[timername]


    def disconnect(self):
        self.connected = False
        self.connection.close()


    def connect(self):
        if not self.connected:
            try:
                self.connection = telnetlib.Telnet(self.host, self.port)
                time.sleep(.2)
                self.connection.sock.sendall(IAC + WILL + TTYPE)
                self.connection.sock.sendall(IAC + SB + TTYPE + IS + self.terminaltype + IAC + SE)

                self.connection.write("load %s %s\r\n" % (self.username, self.password))
                print "%s connected successfully" % self.username
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
            try:
                data = self.format_ansi(self.connection.read_until("\n"))
            except AttributeError:
                break

            if data not in ["\n", "\r\n"]:
                data = data.rstrip()

            printable = True

            for trigger in sorted(self.triggers.values(), key=lambda i: i.priority, reverse=True):
                matches = re.match(trigger.regex, data)
                if matches:
                    trigger.run(data, matches.groups())
                    if trigger.gag:
                        printable = False

                    if not trigger.keepmatching:
                        break

            if printable and not self.silent:
                print data

