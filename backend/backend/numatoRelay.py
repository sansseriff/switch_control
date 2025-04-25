import time
import serial
from verification import Verification


class Relay(object):
    """Numato Relay Class"""

    def __init__(self, visa_name: str | None, resource_name_prefix: str = "A0M"):
        if visa_name is None:
            self.serial = None
            print("No relay connected. Debug mode.")
            return

        self.serial = serial.Serial()
        self.serial.baudrate = 9600
        self.serial.port = visa_name
        self.serial.timeout = 0.25
        self.OptChan = 1
        self.serial.open()

        # print(f"resource name for {visa_name}: ", self.getVersion())

        if self.getVersion().startswith(resource_name_prefix):
            print("Relay Connected")
        else:
            print("Relay not connected")
            self.serial.close()
            self.serial = None
            raise ConnectionError("Failed to connect to the relay.")

    def read(self, bits: int):
        # print("Reading Bits")
        if self.serial:
            return self.serial.read(bits).decode()
        else:
            return "NO SERIAL. DEBUG RETURN"

    def write(self, string: str):
        if self.serial:
            self.serial.write(str.encode(string + "\n\r"))
        else:
            print("NO SERIAL. DEBUG SENDING: ", string)
        # print(string)

    def query(self, string: str, bits: int):
        self.write(string)
        # _ = self.read(bits)
        data = self.read(bits)
        # Remove the sent command and newlines from the response
        # also remove trailing '>' character
        response = data.replace(string, "").replace("\n", "").replace("\r", "")[:-1]
        return response

    def get_channel(self, chan: int) -> str:
        if chan == 10:
            return "A"
        elif chan == 11:
            return "B"
        elif chan == 12:
            return "C"
        elif chan == 13:
            return "D"
        elif chan == 14:
            return "E"
        elif chan == 15:
            return "F"
        elif chan == 16:
            return "G"
        elif chan == 17:
            return "H"
        elif chan == 18:
            return "I"
        elif chan == 19:
            return "J"
        elif chan == 20:
            return "K"
        elif chan == 21:
            return "L"
        elif chan == 22:
            return "M"
        elif chan == 23:
            return "N"
        elif chan == 24:
            return "O"
        elif chan == 25:
            return "P"
        elif chan == 26:
            return "Q"
        elif chan == 27:
            return "R"
        elif chan == 28:
            return "S"
        elif chan == 29:
            return "T"
        elif chan == 30:
            return "U"
        elif chan == 31:
            return "V"
        else:
            return str(chan)

    def turn_on(self, channel: int, verification: Verification):
        assert verification.verified, "Verification not complete"
        chan = self.get_channel(channel)
        self.write("relay on " + chan)
        return True

    def turn_off(self, channel: int, verification: Verification):
        assert verification.verified, "Verification not complete"
        chan = self.get_channel(channel)
        self.write("relay off " + chan)
        return True

    def chan_read(self, channel: int):
        chan = self.get_channel(channel)
        ans = self.query("relay read " + chan, 100)

        print("response: ", ans)

        if "on" in ans:
            return True
        elif "off" in ans:
            return False
        else:
            print("returning non matching answer")
            return ans

    def send_pulse(self, channel: int, pulseWidth: float, verification: Verification):
        assert verification.verified, "Verification not complete"

        self.turn_on(channel, verification)
        time.sleep(float(pulseWidth / 1000))
        self.turn_off(channel, verification)

    def close(self):
        self.TurnOffOptChannel()

    def new(self, channel: int):
        chan = self.get_channel(channel)
        startime = time.time()
        self.write("relay on " + chan)
        t1 = time.time()
        print(t1 - startime)

        time.sleep(0.1)
        t2 = time.time()
        print(t2 - t1)
        self.write("relay off " + chan)
        t3 = time.time()
        print(t3 - t2)
        self.chan_read(channel)
        t4 = time.time()
        print(t4 - t3)

    def OptChannelPlusOne(self):
        self.write("relay on 8")
        time.sleep(1)
        self.write("relay off 8")
        if self.OptChan == 6:
            self.OptChan = 1
        else:
            self.OptChan += 1

    def SetOptChannel(self, chan: int):
        while self.OptChan is not chan:
            self.OptChannelPlusOne()
            time.sleep(1)

    def TurnOffOptChannel(self):
        while self.OptChan != 1:
            self.OptChannelPlusOne()
            time.sleep(1)

    def getVersion(self):
        return self.query("ver", 100)

    def ReadAll(self):
        return self.query("relay readall", 100)

    def Reset(self):
        self.write("reset")

    def SetWavelength(self, wl: int | str):
        if wl == 1550:
            self.SetOptChannel(2)
            self.OptChan = 2
        elif wl == 1064:
            self.SetOptChannel(3)
            self.OptChan = 3
        elif wl == 775:
            self.SetOptChannel(4)
            self.OptChan = 4
        elif wl == 532:
            self.SetOptChannel(5)
            self.OptChan = 5
        elif wl == "DCR":
            self.SetOptChannel(6)
            self.OptChan = 6

    def FindPosition(self, wl: int | str):
        if wl == 1550:
            self.OptChan = 2
        elif wl == 1064:
            self.OptChan = 3
        elif wl == 775:
            self.OptChan = 4
        elif wl == 532:
            self.OptChan = 5
        elif wl == "DCR":
            self.OptChan = 6


if __name__ == "__main__":
    visa_name_mac = "/dev/tty.usbmodem11201"
    # run ls /dev/*usb* to find the correct name for the relay

    relay = Relay(visa_name_mac)

    relay.Reset()
