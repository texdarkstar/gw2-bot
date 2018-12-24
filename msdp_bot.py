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
        elif (self.runs < self.max_runs):
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
        self.msdp = False
        self.triggers = {}
        self.timers = {}
        self.registered_msdp = {}
        self.registered_msdp_send = {}
        self.init()

    def chew_msdp(self, sock, command, option):
        if command == WILL and option == MSDP:
            self.msdp = True
            sock.sendall(IAC + DO + MSDP)
            sock.sendall(
                IAC + SB + MSDP + MSDP_VAR + "LIST" + MSDP_VAL + "REPORTABLE_VARIABLES" + IAC + SE)

        if self.msdp == True:  # and command == SB:
            data = self.connection.read_sb_data()

            if data.strip() and data[0] == MSDP:
                data = data.split(MSDP_VAR)

                for row in data:
                    var = row.split(MSDP_VAL)
                    if len(var) == 2:
                        print repr(var)
                        if var[0] in self.registered_msdp_send.keys():  # send requests take precedence over reports
                            self.registered_msdp_send[var[0]](var[1])

                        elif var[0] in self.registered_msdp.keys():
                            self.registered_msdp[var[0]](var[1])

    def register_msdp(self, var, callback):
        var = var.upper()
        if var not in self.registered_msdp.keys():  # we haven't asked to report this
            msdp = IAC + SB + MSDP + MSDP_VAR + "REPORT" + MSDP_VAL + var + IAC + SE
            self.registered_msdp[var] = callback
            self.connection.sock.sendall(msdp)

    def register_msdp_list(self, *variables):  # ((var, callback))
        msdp = IAC + SB + MSDP + MSDP_VAR + "REPORT"
        for row in variables:
            var, callback = row
            var = var.upper()
            msdp += MSDP_VAL + var
            self.registered_msdp[var] = callback
        msdp += IAC + SE
        self.connection.sock.sendall(msdp)

    def get_msdp(self, var, callback):
        msdp = IAC + SB + MSDP + MSDP_VAR + "SEND" + MSDP_VAL + var + IAC + SE
        self.registered_msdp_send[var] = callback
        self.connection.sock.sendall(msdp)

    def unregister_msdp(self, var):
        var = var.upper()
        if var in self.registered_msdp.keys():
            msdp = IAC + SB + MSDP + MSDP_VAR + "UNREPORT" + MSDP_VAL + var + IAC + SE
            del self.registered_msdp[var]
            self.connection.sock.sendall(msdp)

    def init(self):
        pass

    def execute(self, string):
        self.connection.write(string + "\n")

    def add_trigger(self, regex, func, name, gag=False, keepmatching=False, priority=1):
        self.triggers[name] = Trigger(client=self, regex=regex, func=func, gag=gag, keepmatching=keepmatching,
                                      priority=priority)

    def add_timer(self, interval, func, max_runs=1, name=None):
        timer = Timer(client=self, interval=interval, func=func, max_runs=max_runs)
        timer.start()

        if not name:
            name = "timer-%d" % int(len(self.timers.keys()) + 1)

        self.timers[name] = timer


x


def disconnect(self):
    self.connected = False
    self.connection.close()


def connect(self):
    if not self.connected:
        try:
            self.connection = telnetlib.Telnet(self.host, self.port)
            self.connection.set_option_negotiation_callback(self.chew_msdp)

            time.sleep(.2)
            self.connection.sock.sendall(IAC + WILL + TTYPE)
            self.connection.sock.sendall(IAC + SB + TTYPE + IS + self.terminaltype + IAC + SE)
            time.sleep(.2)
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
