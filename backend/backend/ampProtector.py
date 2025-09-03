# source = teledyneT3PS("10.9.0.51", port=1026)
# from teledyneT3PS import teledyneT3PS
from keysightE36312A import keysightE36312A
import time

class AmpProtector():
    """
    Class for controlling the Keysight E36312A power supply
    Can use either direct connection or client connection via TCP server
    """

    def __init__(self, disabled: bool = False, on: bool = False, channel: int = 3, use_client: bool = True):
        self.disabled = disabled
        self.channel = channel
        self.use_client = use_client
        
        if not self.disabled:
            if self.use_client:
                # Use client connection via TCP server
                from client_keysightE36312A import ClientKeysightE36312A
                self.source = ClientKeysightE36312A()
            else:
                # Use direct VISA connection
                self.source = keysightE36312A("10.9.0.17")
            
            self.source.connect()

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
        
        # disabled for now, for safety
        # self.source.output_on(self.channel)
        time.sleep(0.2)

        # assert self.source.get_on_off(self.channel) == "1", "Amp did not turn on"

    def turn_on_if_previously_on(self):
        if self.disabled:
            return

        if self.on:
            self.turn_on_amp()

    def is_amp_on(self):
        """Check if the amp is currently on"""
        if self.disabled:
            return False
        try:
            return self.source.get_on_off(self.channel) == "1"
        except:
            return False

    def get_voltage(self):
        """Get current voltage reading"""
        if self.disabled:
            return 0.0
        try:
            return self.source.getVoltage(self.channel)
        except:
            return 0.0

    def get_current(self):
        """Get current current reading"""
        if self.disabled:
            return 0.0
        try:
            return self.source.getCurrent(self.channel)
        except:
            return 0.0

    def __del__(self):
        if self.disabled:
            return
        self.source.disconnect()
