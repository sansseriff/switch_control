# source = teledyneT3PS("10.9.0.51", port=1026)
# from teledyneT3PS import teledyneT3PS
from keysightE36312A import keysightE36312A
import time

class AmpProtector():
    """
    Class for controlling the Keysight E36312A power supply
    """

    def __init__(self, disabled: bool = False, on: bool = False, channel: int = 3):
        self.disabled = disabled
        self.channel = channel
        if not self.disabled:
            self.source = keysightE36312A("10.9.0.17")
            self.source.connect()
            # self.source.enableChannel(1)
            # self.source.setCurrent(1, 0.58)
            # self.source.setOverCurrent(1, 1.2)

        self.on: bool = on # does not turn on amp, but identifies if default state is on or off


    def turn_off_amp(self):
        if self.disabled:
            return
        # self.source.setVoltage(1, 0.0)
        # self.source.disableChannel(1)
        self.source.output_off(self.channel)
        time.sleep(0.4)

        assert self.source.get_on_off(self.channel) == "0", "Amp did not turn off"
        assert self.source.getVoltage(self.channel) <= 0.005, "Amp did not turn off completely"


    def turn_on_amp(self):
        if self.disabled:
            return
        time.sleep(0.4)
        # self.source.setVoltage(1, 4.4948)
        # self.source.enableChannel(1)

    def turn_on_if_previously_on(self):
        if self.disabled:
            return



        if self.on:
            self.turn_on_amp()

    def __del__(self):
        if self.disabled:
            return
        self.source.disconnect()
