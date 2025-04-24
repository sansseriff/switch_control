import subprocess
import time
from verification import Verification
from numatoRelay import Relay


class PulseController:
    """
    The room temperature system/apparatus that sends voltage pulses to particular
    cryogenic relays this class could be rewritten, depending on how the controller
    is implemented and wired up. For example, if room temp relays create the voltage
    pulses by  turning off-on-off over ~50 ms, then flip_left and flip_right should
    run  the positive_pulse/negative_pulse methods inside.

    Alternatively, if a function generator is used to create the voltage pulses, and the
    room temp relays are used to wire-switching following the function generator, then
    """

    def __init__(self, sleep_time: float = 0.050, pulse_time: float = 50):
        self.relay_board = self.initialize_relay()
        self.sleep_time = sleep_time
        self.pulse_time = pulse_time

    def flip_left(self, channel: int, verification: Verification):
        self.simple_relay_flip_left(channel, verification)

    def flip_right(self, channel: int, verification: Verification):
        self.simple_relay_flip_right(channel, verification)

    def simple_relay_flip_left(self, channel: int, verification: Verification):
        self.relay_board.turn_off(0, verification)
        time.sleep(self.sleep_time)
        self.relay_board.send_pulse(channel, self.pulse_time, verification)
        time.sleep(self.sleep_time)

    def simple_relay_flip_right(self, channel: int, verification: Verification):
        self.relay_board.turn_on(0, verification)
        time.sleep(self.sleep_time)
        self.relay_board.send_pulse(channel, self.pulse_time, verification)
        time.sleep(self.sleep_time)
        self.relay_board.turn_off(0, verification)
        time.sleep(self.sleep_time)

    def initialize_relay(self):
        relay_board = None  # Initialize with a default value
        serial_ports = get_serial_ports()

        if serial_ports:
            for port in serial_ports:
                try:
                    relay_board = Relay(port)
                    print("Relay initialized successfully")
                    return relay_board
                except Exception as error:
                    print(f"Failed to initialize relay: {error}")
        else:
            print("No serial ports found, using debug mode")

        # If we reach here, either no ports were found or all connection attempts failed
        relay_board = Relay(None)
        return relay_board

    def cleanup(self):
        if self.relay_board and self.relay_board.serial:
            self.relay_board.close()


# Scan the system for serial ports
def get_serial_ports():
    ports: list[str | None] = []
    commands = ["ls /dev/ttyUSB*", "ls /dev/ttyACM*", "ls /dev/*usb*"]

    for cmd in commands:
        try:
            output = subprocess.check_output(cmd, shell=True, text=True)
            ports.extend(output.strip().split("\n"))
        except subprocess.CalledProcessError:
            # Ignore the error if no devices are found for the current pattern
            continue

    print("these are the ports: ", ports)

    return ports
