"""
visaInst.py
Author: Alex Walter
Date: Dec 12, 2019

With inspiration from the old JPL Library of snspd-scripts written by Simone Frasca, Boris Korzh

A generic base class to talk to instrument hardware over TCIP with visa
"""

import pyvisa


class visaInst:
    def __init__(self, ipAddress, port=5025, offline=False):
        """

        :param ipAddress: The ip address. ie 10.7.0.114 [string]
        :param port: The port on the host computer [int]
        :param offline: If True, just pretend to send data over the visa
        """
        self.ipAddress = ipAddress
        self.port = port
        self.offline = offline

    def connect(self):
        if self.offline:
            print("Connected to offline instrument " + str(self.__class__))
            return True
        rm = pyvisa.ResourceManager("@py")

        self.inst = rm.open_resource(
            "TCPIP::" + self.ipAddress + "::" + str(self.port) + "::SOCKET"
        )
        self.inst.read_termination = "\n"
        self.inst.timeout = max(
            10000, self.inst.timeout
        )  # Make visa timeout at least 10000 ms
        print(self.query("*IDN?"))
        # print(self.inst.timeout)
        return self.inst

    def disconnect(self):
        if self.offline:
            print("Disconnected from offline instrument " + str(self.__class__))
            return True
        return self.inst.close()

    def write(self, cmd: str):
        if self.offline:
            return True
        return self.inst.write(cmd)

    def read(self) -> str:
        if self.offline:
            return ""
        return self.inst.read()

    def query(self, cmd: str) -> str:
        if self.offline:
            return ""
        return self.inst.query(cmd)
