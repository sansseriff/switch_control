import subprocess
import time
from verification import Verification
from numatoRelay import Relay
from node import Node, MaybeNode

from abc import ABC, abstractmethod
from models import SwitchState, Tree, T


class PulseController(ABC):
    """
    The room temperature system/apparatus that sends voltage pulses to particular
    cryogenic relays. Inherit and rewrite methods in this class to implement the
    functionality of whichever system is used to generate the voltage pulses.

    For example, if room temp relays create the voltage pulses by  turning
    off-on-off over ~50 ms, then use the SimpleRelayPulseController class.

    Alternatively, if a function generator is used to create the voltage pulses,
    and the room temp relays are used to wire-switching following the function
    generator, then use the FunctionGeneratorPulseController class.
    """

    def __init__(self, sleep_time: float = 0.050, pulse_time: float = 50):
        self.relay_board = self.initialize_relay()
        self.sleep_time = sleep_time
        self.pulse_time = pulse_time

    @abstractmethod
    def flip_left(self, channel: int, verification: Verification):
        pass

    @abstractmethod
    def flip_right(self, channel: int, verification: Verification):
        pass

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


class SimpleRelayPulseController(PulseController):
    """
    A simple implementation of the PulseController that uses a relay board to send
    voltage pulses to the cryogenic relays.
    """

    def __init__(self, sleep_time: float = 0.050, pulse_time: float = 50):
        super().__init__(sleep_time, pulse_time)

    def flip_left(self, channel: int, verification: Verification):
        self.relay_board.turn_off(0, verification)
        time.sleep(self.sleep_time)
        self.relay_board.send_pulse(channel, self.pulse_time, verification)
        time.sleep(self.sleep_time)

    def flip_right(self, channel: int, verification: Verification):
        self.relay_board.turn_on(0, verification)
        time.sleep(self.sleep_time)
        self.relay_board.send_pulse(channel, self.pulse_time, verification)
        time.sleep(self.sleep_time)
        self.relay_board.turn_off(0, verification)
        time.sleep(self.sleep_time)


class FunctionGeneratorPulseController(PulseController):
    """
    A PulseController that uses a function generator to send voltage pulses to the
    cryogenic relays.
    """

    def __init__(self, sleep_time: float = 0.050, pulse_time: float = 50):
        super().__init__(sleep_time, pulse_time)

        self.nodes = [Node(f"R{i}") for i in range(1, 7)]
        self.R1, self.R2, self.R3, self.R4, self.R5, self.R6 = self.nodes
        self.top_node: MaybeNode = self.R1

        # using room temp relays for wire switching
        #
        #        Function Generator
        #                |
        #           ___  R1 ____
        #         /              \
        #       R2                R3
        #    /      \          /      \
        #   R4       R5       R6       |
        #  /  \     /  \     /  \      |
        # 7    6   5    4   3    2     1   # channel according to the relay board

        # Set up tree structure
        self.R1.left = self.R2
        self.R1.right = self.R3
        self.R2.left = self.R4
        self.R2.right = self.R5
        self.R3.left = self.R6

        self.R3.right = 1

        self.R4.left = 7
        self.R4.right = 6
        self.R5.left = 5
        self.R5.right = 4
        self.R6.left = 3
        self.R6.right = 2

        # Initialize state
        self.tree_state = Tree(
            R1=SwitchState(pos=False, color=False),
            R2=SwitchState(pos=False, color=False),
            R3=SwitchState(pos=False, color=False),
            R4=SwitchState(pos=False, color=False),
            R5=SwitchState(pos=False, color=False),
            R6=SwitchState(pos=False, color=False),
            R7=SwitchState(pos=False, color=False),
            activated_channel=0,
        )
        self.tree = T(tree_state=self.tree_state, activated_channel=0)

    def flip_left(self, channel: int, verification: Verification):
        # Implement function generator logic for flipping left

        # flip the channel numbering
        # channel = 7 - channel
        # switch from user to relay channel numbering
        # channel -= 1
        binary = bin(channel)[2:]
        # binary should be 3 digits long
        binary = binary.zfill(3)
        print("binary: ", binary)

    def flip_right(self, channel: int, verification: Verification):
        # Implement function generator logic for flipping right
        # flip the channel numbering
        channel = 7 - channel
        # switch from user to relay channel numbering
        # channel -= 1
        binary = bin(channel)[2:]
        # binary should be 3 digits long
        binary = binary.zfill(3)
        print("binary: ", binary)
