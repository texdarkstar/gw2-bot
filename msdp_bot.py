from bot import Robot
from constants import *


class RobotMSDP(Robot):
    def __init__(self, username, password, silent=False, terminaltype="PYBOT-v2.0"):
        super(Robot, self).__init__()
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
