import time
from visaInst import visaInst


# manual for teledyneT3PS voltage sources is here: https://www.manualslib.com/manual/1637978/Teledyne-T3ps13206p.html?page=7#manual
# By Andrew Mueller, January 2022

# Find the ip address of the voltag source by pressing 'System' on the front panel
# type the ip address of the instrument into your browser. Note the port number.
# for example, the port in this visa string is "1026": TCPIP::10.7.0.147::1026::SOCKET


class teledyneT3PS(visaInst):
    """
    Class for keysight5322A counter
    """
    def __init__(self, ipAddress, port = 1026, **kwargs):
        """

        :param ipAddress: ie. '10.7.0.111'
        :param kwargs:
                     - offline: If True, then don't actually read/send data over visa
        """
        super().__init__(ipAddress, port = port, **kwargs)

    def reset(self):
        self.write('*RST')

    # reads actual voltage, not set voltage
    def getVoltage(self, channel):
        msg = f"MEASure{channel}:VOLTage?"
        return float(self.query(msg))

    # reads actual current, not set current
    def getCurrent(self, channel):
        msg = f"MEASure{channel}:CURRent?"
        return float(self.query(msg))

    # vOut and iOut output strings, including units (not very different from getVoltage)
    def getVOut(self, channel):
        msg = f"VOUT{channel}?"
        return self.query(msg)

    def getIOut(self, channel):
        msg = f"IOUT{channel}?"
        return self.query(msg)

    def enableChannel(self, channel):
        msg = f":OUTPut{channel}:STATe ON"
        msgsk = "OUTPut:STATe?"
        self.write(msg)
        return self.query(msgsk)

    def disableChannel(self, channel):
        msg = f":OUTPut{channel}:STATe OFF"
        msgsk = "OUTPut:STATe?"
        self.write(msg)
        return self.query(msgsk)

    def setOverVoltage(self, channel, voltage):
        # activates over voltage protection mode, and sets to voltage
        self.write(f":OUTPut{channel}:OVP:STATe ON")
        if self.query(f":OUTPut{channel}:OVP:STATe?") == "ON":
            voltage = round(voltage,3)
            self.write(f":OUTPut{channel}:OVP {voltage}")
            ret = self.query(f":OUTPut{channel}:OVP?")
            return f"OVP set to {ret}"
        else:
            print("Error setting OverVoltage. Exiting.")
            return 1

    def setOverCurrent(self, channel, current):
        # activates over current protection mode, and sets to voltage
        self.write(f":OUTPut{channel}:OCP:STATe ON")
        if self.query(f":OUTPut{channel}:OCP:STATe?") == "ON":

            current = round(current,3)
            self.write(f":OUTPut{channel}:OCP {current}")
            ret = self.query(f":OUTPut{channel}:OCP?")
            return f"OCP set to {ret}"
        else:
            print("Error setting OverCurrent. Exiting.")
            return 1

    def setCurrent(self, channel, current):
        self.write(f"ISET{channel}:{current}")
        return(self.query(f":SOURce{channel}:CURRent?"))

    def setVoltage(self, channel, voltage):
        self.write(f"VSET{channel}:{voltage}")
        return(self.query(f":SOURce{channel}:VOLTage?"))

    def setChannelMode(self,mode):
        """
        :param mode: "IND" -> Independent, "SER" -> Series, "PAR" -> Parallel
        """
        rs = -1
        if mode == "IND":
            rs = 0
        if mode == "SER":
            rs = 1
        if mode == "PAR":
            rs = 2
            print("yes")
        if rs < 0:
            print("Unkown command")
            return 1
        self.write(f"TRACK{rs}")
        time.sleep(0.4) # takes a moment to move switch inside
        return(self.query("MODE1?"))

    



if __name__=='__main__':
    source = teledyneT3PS("10.9.0.51", port=1026)
    source.connect()
    # print(float(source.getVoltage(1)))
    # print(source.getCurrent(1))
    # print(source.getVOut(1))
    # print(source.getIOut(1))
    print(source.enableChannel(1))

    source.setVoltage(1, 5.0)
    source.setOverCurrent(1, 1.2)
    # print(source.disableChannel(1))
    # print(source.setOverCurrent(1, 1.2))
    # print(source.setCurrent(1, .5))
    # print(source.setVoltage(1, 0.123))
    # print(source.enableChannel(1))
    # print(source.getVoltage(1))
    # print(source.setChannelMode("IND"))
    # source.setOverCurrent(1, .6)
    # for i in range(50):
    #     source.setVoltage(1,0.01*i)
    #     time.sleep(0.1)
    # source.disconnect()



    
