import time
from visaInst import visaInst


class keysightE36312A(visaInst):
    """
    Class for keysight E36312A voltage source - Generalized implementation
    Provides individual functions for controlling different aspects of source
    """

    def __init__(self, ipAddress: str, **kwargs):
        """
        :param ipAddress: ie. '10.7.0.111'
        :param kwargs:
                     - offline: If True, then don't actually read/send data over visa
        """
        super().__init__(ipAddress, **kwargs)

        self.high_level = 0

    def init(self):
        self.write("INIT")

    def reset(self):
        self.write("*RST")

    def output_on(self, channel: int):
        self.write(f"OUTP ON, (@{channel})")
        self.write("*OPC")

    def output_off(self, channel: int):
        self.write(f"OUTP OFF, (@{channel})")
        self.write("*OPC")


    def get_on_off(self, channel: int):
        msg = f"OUTP? (@{channel})"
        return self.query(msg)

    def getVoltage(self, channel: int):
        msg = f"MEAS:VOLT? (@{channel})"
        return float(self.query(msg))
    
    def getCurrent(self, channel: int):
        msg = f"MEAS:CURR? (@{channel})"
        return float(self.query(msg))




if __name__=='__main__':
    source = keysightE36312A("10.9.0.17")
    source.connect()
    # print(float(source.getVoltage(1)))
    # print(source.getCurrent(1))
    # print(source.getVOut(1))
    # print(source.getIOut(1))


    print(source.output_on(3))

    time.sleep(3)
    print(source.getVoltage(3))
    print(source.get_on_off(3))


    print(source.output_off(3))

    time.sleep(3)
    print(source.getVoltage(3))
    print(source.get_on_off(3))
    # print(source.enableChannel(1))

    # source.setVoltage(1, 5.0)
    # source.setOverCurrent(1, 1.2)