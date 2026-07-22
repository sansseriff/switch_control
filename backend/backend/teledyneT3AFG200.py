import time
from visaInst import visaInst


class teledyneT3AFG200(visaInst):
    """
    Class for Teledyne T3AFG200 AWG.

    Mirrors the public interface of keysight33622A so it can be a drop-in
    replacement. The underlying SCPI is very different: the T3AFG uses the
    LeCroy-style `C<n>:BSWV PARAM,VALUE` syntax rather than the Keysight
    `:SOURce<n>:...` tree. All translation happens in this class.

    Notable behavioral differences from the Keysight 33622A:
      - Function names: Keysight uses SIN/SQU/PULS; T3AFG uses SINE/SQUARE/
        PULSE. set_function() accepts either and translates.
      - Output state: Keysight accepts 0/1; T3AFG accepts ON/OFF. set_output
        translates so callers can keep passing 0/1.
      - get_output(): Keysight `:OUTP?` returns "0"/"1"; T3AFG `Cn:OUTP?`
        returns e.g. "C1:OUTP ON,LOAD,HZ,PLRT,NOR" which must be parsed.
      - Manual trigger: Keysight has a top-level `:TRIGger<n>` command;
        T3AFG only supports manual trigger inside burst/sweep, via
        `Cn:BTWV MTRIG`. immediate_trigger() assumes burst mode is on.
      - Burst trigger sources: Keysight {IMMediate, EXTernal, TIMer, BUS};
        T3AFG {INT, EXT, MAN}. TIMer has no exact equivalent (mapped to INT).
      - *OPC: on the T3AFG this only sets the ESR bit; the instrument
        already serializes commands, so *OPC is essentially a no-op.
      - phase_sync(): the Keysight has a dedicated phase-sync command. The
        T3AFG approximation is to re-zero both channels' phases.
      - init(): Keysight's "INIT" arms the trigger system. The T3AFG has no
        equivalent; this is a no-op.
      - Default socket port is 5025 on both instruments (see programming
        guide section 1.2.4). Telnet uses 5024 — do not use that here.
    """

    # Translation table from Keysight short-form function names to T3AFG WVTP.
    _FUNCTION_MAP = {
        "SIN": "SINE",
        "SINE": "SINE",
        "SQU": "SQUARE",
        "SQUARE": "SQUARE",
        "PULS": "PULSE",
        "PULSE": "PULSE",
        "RAMP": "RAMP",
        "NOIS": "NOISE",
        "NOISE": "NOISE",
        "DC": "DC",
        "ARB": "ARB",
        "PRBS": "PRBS",
    }

    # Burst trigger source translation: Keysight -> T3AFG.
    _TRIG_SRC_MAP = {
        "IMMediate": "INT",
        "IMM": "INT",
        "INT": "INT",
        "EXTernal": "EXT",
        "EXT": "EXT",
        "BUS": "MAN",
        "MAN": "MAN",
        "TIMer": "INT",
        "TIM": "INT",
    }

    def __init__(self, ipAddress: str, **kwargs):
        """
        :param ipAddress: ie. '10.7.0.111'
        :param kwargs:
                     - offline: If True, then don't actually read/send data over visa
        """
        super().__init__(ipAddress, **kwargs)

        self.high_level = 0

    @staticmethod
    def _edge_time_to_seconds(edge_time) -> float:
        """
        Accept either a float (seconds) or a Keysight-style string like
        "10000 ns" / "1 us" / "5e-6 s" and return seconds. The T3AFG BSWV
        RISE/FALL parameters take a bare number in seconds.
        """
        if isinstance(edge_time, (int, float)):
            return float(edge_time)
        s = str(edge_time).strip().lower()
        units = {"ns": 1e-9, "us": 1e-6, "ms": 1e-3, "s": 1.0}
        for suffix, scale in units.items():
            if s.endswith(suffix):
                return float(s[: -len(suffix)].strip()) * scale
        return float(s)

    def init(self):
        # The Keysight "INIT" arms its trigger subsystem. T3AFG has no equivalent.
        pass

    def reset(self):
        self.write("*RST")

    # General control functions
    def set_function(self, channel: int, function_type: str):
        """
        Set the function type for a specific channel.
        Accepts Keysight short forms (SIN, SQU, PULS) and translates them.
        """
        wvtp = self._FUNCTION_MAP.get(function_type.upper(), function_type.upper())
        self.write(f"C{channel}:BSWV WVTP,{wvtp}")
        self.write("*OPC")

    def set_pulse_width(self, channel: int, width: float):
        """
        Set the width of a pulse in seconds
        :param channel: Channel number (1 or 2)
        :param width: Width in seconds
        """
        self.write(f"C{channel}:BSWV WIDTH,{width}")
        self.write("*OPC")

    def set_frequency(self, channel: int, freq: float):
        """
        Set the frequency of the output
        :param channel: Channel number (1 or 2)
        :param freq: Frequency in Hz
        """
        self.write(f"C{channel}:BSWV FRQ,{freq}")
        self.write("*OPC")

    def set_amplitude(self, channel: int, amplitude: float):
        """
        Set the amplitude of the output
        :param channel: Channel number (1 or 2)
        :param amplitude: Amplitude in Vpp
        """
        self.write(f"C{channel}:BSWV AMP,{amplitude}")
        self.write("*OPC")

    def set_offset(self, channel: int, offset: float):
        """
        Set the DC offset of the output
        :param channel: Channel number (1 or 2)
        :param offset: Offset in Volts
        """
        self.write(f"C{channel}:BSWV OFST,{offset}")
        self.write("*OPC")

    def set_high_level(self, channel: int, high: float):
        """Set the high voltage level (V)."""
        self.write(f"C{channel}:BSWV HLEV,{high}")
        self.write("*OPC")

    def set_low_level(self, channel: int, low: float):
        """Set the low voltage level (V)."""
        self.write(f"C{channel}:BSWV LLEV,{low}")
        self.write("*OPC")

    def set_duty_cycle(self, channel: int, duty: float):
        """Set the duty cycle (%). Only valid when current WVTP is SQUARE or PULSE."""
        self.write(f"C{channel}:BSWV DUTY,{duty}")
        self.write("*OPC")

    def set_phase(self, channel: int, phase: float):
        """
        Set the phase of the output in degrees
        :param channel: Channel number (1 or 2)
        :param phase: Phase in degrees
        """
        self.write(f"C{channel}:BSWV PHSE,{phase}")
        self.write("*OPC")

    def apply_pulse(self, channel: int, freq: float, amplitude: float, offset: float):
        """
        Configure a pulse waveform with specified parameters.
        Keysight had a single APPLy:PULSe command; T3AFG needs separate BSWV writes.
        """
        self.write(f"C{channel}:BSWV WVTP,PULSE")
        self.write(f"C{channel}:BSWV FRQ,{freq}")
        self.write(f"C{channel}:BSWV AMP,{amplitude}")
        self.write(f"C{channel}:BSWV OFST,{offset}")
        self.write("*OPC")

    def set_output(self, channel: int, state: int):
        """
        Turn the output on or off for a specific channel
        :param channel: Channel number (1 or 2)
        :param state: 0 for off, 1 for on
        """
        on_off = "ON" if int(state) else "OFF"
        self.write(f"C{channel}:OUTP {on_off}")
        self.write("*OPC")

    def get_output(self, channel: int) -> int:
        """
        Get the output state for a specific channel.
        T3AFG returns e.g. "C1:OUTP ON,LOAD,HZ,PLRT,NOR"; parse the first field.
        :return: 0 for off, 1 for on
        """
        response = self.query(f"C{channel}:OUTP?")
        # Response is "C1:OUTP ON,LOAD,HZ,PLRT,NOR" — split off header, take first CSV field.
        try:
            payload = response.split(" ", 1)[1]
            state = payload.split(",", 1)[0].strip().upper()
        except IndexError:
            state = response.strip().upper()
        return 1 if state == "ON" else 0

    def set_polarity(self, channel: int, polarity: str):
        """
        Set the polarity of the output
        :param channel: Channel number (1 or 2)
        :param polarity: 'POS' or 'NEG'
        """
        if polarity == "POS":
            self.write(f"C{channel}:OUTP PLRT,NOR")
        elif polarity == "NEG":
            self.write(f"C{channel}:OUTP PLRT,INVT")
        else:
            raise ValueError("Polarity must be 'POS' or 'NEG'")
        self.write("*OPC")

    def phase_sync(self):
        """
        Synchronize the phase of all channels.
        T3AFG has no exact equivalent of Keysight's :SOURce:PHASe:SYNChronize;
        the closest behavior is to zero both channel phases.
        """
        self.write("C1:BSWV PHSE,0")
        self.write("C2:BSWV PHSE,0")

    def immediate_trigger(self, channel: int):
        # T3AFG only accepts manual triggers in burst/sweep mode; this targets burst.
        self.write(f"C{channel}:BTWV MTRIG")

    def trigger_with_polarity(self, channel: int, high_level: float, polarity: str):
        self.set_pulse_polarity(channel, polarity, high_level)
        time.sleep(0.5)
        self.immediate_trigger(channel)
        time.sleep(0.5)
        self.write("*OPC")

    # Maintaining backward compatibility with original functions
    def filter_channel(self, phase: float, freq: float):
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

    def set_pulse_polarity(self, channel: int, polarity: str, high_level: float = 0):
        """
        Set the polarity of the pulse waveform.
        Mirrors the Keysight behavior: amplitude = high_level, offset = ±high_level/2,
        and the output polarity flipped to match.
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

    def setup_pulse(
        self,
        channel: int = 1,
        period: float = 0.5,
        width: float = 0.050,
        edge_time: str = "10000 ns",
    ):
        """
        Set up a pulse waveform with specified parameters
        :param channel: Channel number (1 or 2)
        :param period: Period in seconds
        :param width: Pulse width in seconds
        :param edge_time: Edge time, either seconds (float) or a string like "10000 ns"
        """
        edge_s = self._edge_time_to_seconds(edge_time)

        self.write(f"C{channel}:BSWV WVTP,PULSE")
        self.write(f"C{channel}:BSWV PERI,{period}")
        self.write(f"C{channel}:BSWV WIDTH,{width}")
        # Keysight had a single TRANsition:BOTH; T3AFG splits into RISE / FALL.
        self.write(f"C{channel}:BSWV RISE,{edge_s}")
        self.write(f"C{channel}:BSWV FALL,{edge_s}")
        self.enable_burst(channel)
        self.write("*OPC")

    def enable_burst(self, channel: int):
        self.write(f"C{channel}:BTWV STATE,ON")

    def disable_burst(self, channel: int):
        self.write(f"C{channel}:BTWV STATE,OFF")

    def set_thermal_source_mode(self):
        self.write("C1:BSWV WVTP,SQUARE")
        self.write("C2:BSWV WVTP,SQUARE")
        self.write("C1:BSWV DUTY,34.5")
        self.write("C2:BSWV DUTY,34.5")
        self.write("C1:BSWV PERI,1")
        self.write("C2:BSWV PERI,1")

        self.disable_burst(1)
        self.set_amplitude(1, 1)
        self.set_amplitude(2, 1.210)
        self.set_offset(1, 0.5)
        self.set_offset(2, 1.210 / 2)

    def setup_trigger(self, channel, source: str):
        """
        Set the burst trigger source. Accepts Keysight names
        {IMMediate, EXTernal, TIMer, BUS} and maps to T3AFG {INT, EXT, MAN}.
        TIMer has no exact equivalent on the T3AFG and is mapped to INT.
        """
        if source not in ["IMMediate", "EXTernal", "TIMer", "BUS"]:
            raise ValueError("Invalid trigger source. Must be one of IMMediate, EXTernal, TIMer, BUS.")

        t3_src = self._TRIG_SRC_MAP[source]
        return self.write(f"C{channel}:BTWV TRSR,{t3_src}")


if __name__ == "__main__":
    fg = teledyneT3AFG200("10.9.0.18")
    fg.connect()

    time.sleep(0.2)

    fg.set_amplitude(2, 1.60)
    fg.set_offset(2, 0.8)
