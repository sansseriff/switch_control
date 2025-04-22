import time
from visaInst import visaInst


class keysight33622A(visaInst):
    """
    Class for keysight 33622A AWG - Generalized implementation
    Provides individual functions for controlling different aspects of the waveform
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

    # General control functions
    def set_function(self, channel, function_type):
        """
        Set the function type for a specific channel
        :param channel: Channel number (1 or 2)
        :param function_type: Function type (SIN, SQU, PULS, etc.)
        """
        self.write(f":SOURce{channel}:FUNCtion {function_type}")
        self.write("*OPC")

    def set_pulse_width(self, channel, width):
        """
        Set the width of a pulse in seconds
        :param channel: Channel number (1 or 2)
        :param width: Width in seconds
        """
        self.write(f":SOURce{channel}:FUNCtion:PULSe:WIDTh {width}")
        self.write("*OPC")

    def set_frequency(self, channel, freq):
        """
        Set the frequency of the output
        :param channel: Channel number (1 or 2)
        :param freq: Frequency in Hz
        """
        self.write(f":SOURce{channel}:FREQuency {freq}")
        self.write("*OPC")

    def set_amplitude(self, channel, amplitude):
        """
        Set the amplitude of the output
        :param channel: Channel number (1 or 2)
        :param amplitude: Amplitude in Vpp
        """
        self.write(f":SOURce{channel}:VOLTage {amplitude}")
        self.write("*OPC")

    def set_offset(self, channel, offset):
        """
        Set the DC offset of the output
        :param channel: Channel number (1 or 2)
        :param offset: Offset in Volts
        """
        self.write(f":SOURce{channel}:VOLTage:OFFSet {offset}")
        self.write("*OPC")

    def set_phase(self, channel, phase):
        """
        Set the phase of the output in degrees
        :param channel: Channel number (1 or 2)
        :param phase: Phase in degrees
        """
        self.write(f":SOURce{channel}:PHASe {phase}")
        self.write("*OPC")

    def apply_pulse(self, channel, freq, amplitude, offset):
        """
        Configure a pulse waveform with specified parameters
        :param channel: Channel number (1 or 2)
        :param freq: Frequency in Hz
        :param amplitude: Amplitude in Vpp
        :param offset: DC offset in Volts
        """
        self.write(f":SOURce{channel}:APPLy:PULSe {freq},{amplitude} VPP,{offset} V")
        self.write("*OPC")

    def set_output(self, channel, state):
        """
        Turn the output on or off for a specific channel
        :param channel: Channel number (1 or 2)
        :param state: 0 for off, 1 for on
        """
        self.write(f":OUTPut{channel} {state}")
        self.write("*OPC")

    def set_polarity(self, channel, polarity):
        """
        Set the polarity of the output
        :param channel: Channel number (1 or 2)
        :param polarity: 'POSitive' or 'NEGative'
        """
        if polarity == "POS":
            # self.write(f':SOURce{channel}:BURSt:GATE:POLarity NORMal')
            self.write(f":OUTPut{channel}:POLarity NORMal")
        elif polarity == "NEG":
            # self.write(f':SOURce{channel}:BURSt:GATE:POLarity INVerted')
            self.write(f":OUTPut{channel}:POLarity INVerted")
        else:
            raise ValueError("Polarity must be 'POS' or 'NEG'")
        self.write("*OPC")

    def phase_sync(self):
        """Synchronize the phase of all channels"""
        self.write(":SOURce:PHASe:SYNChronize")

    def enable_burst(self, channel, burst_count=1):
        """
        Enable burst mode for a specific channel
        :param channel: Channel number (1 or 2)
        :param burst_count: Number of bursts
        """
        pass
        # self.write(f':SOURCe{channel}:BURSt')
        # self.write('*OPC')
        # self.write(f':SOURce{channel}:BURSt:NCYCles {burst_count}')
        # self.write(f':SOURce{channel}:BURSt:STATe ON')
        # self.write('*OPC')

    def immediate_trigger(self, channel):
        self.write(f":TRIGger{channel}")
        # self.write('*OPC')

    def trigger_with_polarity(self, channel, high_level, polarity):
        self.set_pulse_polarity(channel, polarity, high_level)
        self.immediate_trigger(channel)
        self.write("*OPC")

    # Maintaining backward compatibility with original functions
    def filter_channel(self, phase, freq):
        """Legacy compatibility function for channel 1 settings"""
        self.apply_pulse(1, freq, 0.140, 0)
        self.set_phase(1, phase)
        self.set_pulse_width(1, 4.5e-05)

    def gating_channel(self, x):
        """Legacy compatibility function for channel 2 settings"""
        self.set_pulse_width(2, 9e-05)
        self.apply_pulse(2, 3000.0, 0.090, x)
        self.set_phase(2, 0)

    def channels_off(self):
        """Turn both channels off"""
        self.set_output(2, 0)
        self.set_output(1, 0)

    def channels_on(self):
        """Turn both channels on"""
        self.set_output(2, 1)
        self.set_output(1, 1)

    def phase_zero(self):
        """Set phase to zero for both channels"""
        self.set_phase(1, 0)
        self.set_phase(2, 0)

    # def setup_immedate_pulse(self, channel, high_level):
    #     # pass
    #     self.set_output(1,1)

    #     self.write('*OPC')

    # self.write('*OPC')
    # time.sleep(0.03)

    # self.immediate_trigger(1)
    # time.sleep(1)

    def set_pulse_polarity(self, channel, polarity, high_level=0):
        """
        Set the polarity of the pulse waveform
        :param channel: Channel number (1 or 2)
        :param polarity: 'POSitive' or 'NEGative'
        """

        self.set_amplitude(channel, high_level)

        if polarity == "POS":
            self.set_offset(channel, high_level / 2)
            self.set_polarity(channel, "POS")
        elif polarity == "NEG":
            self.set_offset(channel, -high_level / 2)
            self.set_polarity(channel, "NEG")
        else:
            raise ValueError("Polarity must be 'POS' or 'NEG'")
        self.write("*OPC")

    def setup_pulse(self, channel=1, period=0.5, width=0.050, edge_time="10000 ns"):
        """
        Set up a pulse waveform with specified parameters
        :param channel: Channel number (1 or 2)
        :param period: Period in seconds
        :param width: Pulse width in seconds
        :param edge_time: Edge time in seconds
        """
        # First, explicitly set the function type to PULSE
        self.write(f":SOURce{channel}:FUNCtion PULSe")

        # Continue with pulse parameter configurations

        self.write(f":SOURce{channel}:FUNCtion:PULSe:PERiod {period}")
        self.write(f":SOURce{channel}:FUNCtion:PULSe:WIDTh {width}")
        self.write(f":SOURce{channel}:FUNCtion:PULSe:TRANsition:BOTH {edge_time}")
        self.write("*OPC")

        # print(self.query('*OPC?'))

    def set_thermal_source_mode(self):
        self.write(f":SOURce1:FUNCtion SQUare")
        self.write(f":SOURCe2:FUNCtion SQUare")
        self.write(f":SOURce1:FUNCtion:SQUare:DCYCle 34.5")
        self.write(f":SOURce2:FUNCtion:SQUare:DCYCle 34.5")
        self.write(f":SOURce1:FUNCtion:SQUare:PERiod 1")
        self.write(f":SOURce2:FUNCtion:SQUare:PERiod 1")
        self.set_amplitude(1, 1)
        self.set_amplitude(2, 1.210)
        self.set_offset(1, 0.5)
        self.set_offset(2, 1.210 / 2)


if __name__ == "__main__":
    fg = keysight33622A("10.9.0.50")
    fg.connect()

    fg.setup_pulse(width=0.2)

    fg.set_output(1, 1)

    for i in range(60):
        fg.trigger_with_polarity(1, 5.0, "POS")
        time.sleep(1.2)
        fg.trigger_with_polarity(1, 5.0, "NEG")
        time.sleep(1.2)

    # fg.trigger_with_polarity(1, 5.0, 'POS')
    # time.sleep(4)
    # fg.trigger_with_polarity(1, 5.0, 'NEG')
    # time.sleep(4)
    # fg.trigger_with_polarity(1, 5.0, 'POS')
    # time.sleep(4)
    # fg.trigger_with_polarity(1, 5.0, 'NEG')
    # time.sleep(4)
    # fg.trigger_with_polarity(1, 5.0, 'POS')
    # time.sleep(4)
    # fg.trigger_with_polarity(1, 5.0, 'NEG')
    # time.sleep(4)

    # fg.set_thermal_source_mode()

    # time.sleep(0.1)
    # fg.enable_burst(1, 1)

    # fg.disconnect()
    # time.sleep(0.1)
    # fg.setup_immedate_pulse(1, 2.0)
    # time.sleep(0.1)
    # fg.set_polarity(1, 'POS')

    # time.sleep(2)
    # fg.immediate_trigger(1)

    # fg.immediate_pulse(1, 2.0, 'POS')

    # for i in range(3):
    #     fg.immediate_pulse(1, 2.0, 'POS')
    #     time.sleep(0.5)
    #     fg.immediate_pulse(1, 2.0, 'NEG')
    #     time.sleep(0.5)

    # # fg.set_polarity(1, 'POS')
    # time.sleep(2)
    # fg.set_polarity(1, 'NEG')

    # # Example of using the new API
    # fg.channels_off()
    # fg.set_function(1, 'PULSe')
    # fg.set_frequency(1, 5000)
    # fg.set_pulse_width(1, 4.5e-05)
    # fg.set_amplitude(1, 0.140)
    # fg.set_offset(1, 0)

    # fg.set_function(2, 'PULSe')
    # fg.set_frequency(2, 3000)
    # fg.set_pulse_width(2, 9e-05)
    # fg.set_amplitude(2, 0.090)
    # fg.set_offset(2, 0)

    # fg.set_amplitude(1, 1.111)
    # fg.set_offset(1, 1.111/2)

    # # time.sleep(2)
    # # fg.channels_on()
    # fg.set_output(1, 1)
    # fg.immediate_trigger(1)
    # time.sleep(3)
    # # fg.set_output(1, 0)
    # # fg.immediate_trigger(1)
    # fg.immediate_trigger(1)
    # time.sleep(3)
    # # fg.set_output(1, 1)
    # # fg.immediate_trigger(2)
    # time.sleep(3)
    # fg.channels_off()
