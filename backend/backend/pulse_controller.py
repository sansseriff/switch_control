import subprocess
import os
import time
from verification import Verification
from numatoRelay import Relay
from node import Node, MaybeNode

from abc import ABC, abstractmethod
from models import SwitchState, Tree, T
from keysight33622A import keysight33622A

# Feature flags / environment configuration
DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes", "on")
FG_IP = os.getenv("FG_IP", "10.9.0.50")
EXTRA_SLEEP_TIME = 0


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

    @abstractmethod
    def cryo_mode(self):
        """
        Set the pulse controller to cryogenic mode.
        """
        pass
    
    @abstractmethod
    def room_temp_mode(self):
        """
        Set the pulse controller to room temperature mode.
        """
        pass

    def initialize_relay(self):
        relay_board = None  # Initialize with a default value
        serial_ports = get_serial_ports()

        if serial_ports:
            for port in serial_ports:
                try:
                    relay_board = Relay(port)
                    print("Relay initialized successfully")
                    for r in range(8):
                        relay_board.turn_off(
                            r,
                            Verification(
                                verified=True, timestamp=1, userConfirmed=True
                            ),
                        )
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


    def cryo_mode(self):
        pass
    
    def room_temp_mode(self):
        pass


class FunctionGeneratorPulseController(PulseController):
    """
    A PulseController that uses a function generator to send voltage pulses to the
    cryogenic relays.
    """

    def __init__(
        self,
        sleep_time: float = 0.050,
        pulse_time: float = 50,
        pulse_amplitude: float = 2.5,
        use_client: bool = True,
    ):
        super().__init__(sleep_time, pulse_time)

        # turn 1 into 1 1
        # turn 2 into 1 0 1
        # turn 3 into 1 0 0
        # turn 4 into 0 1 1
        # turn 5 into 0 1 0
        # turn 6 into 0 0 1
        # turn 7 into 0 0 0

        self.nodes = [Node(f"R{i}") for i in range(1, 7)]
        self.R1, self.R2, self.R3, self.R4, self.R5, self.R6 = self.nodes
        self.top_node: MaybeNode = self.R1
        self.use_client = use_client

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


        # on cats control computer, this is a static IP address reservation. 
        # using 'dhcpd-server' running on this computer.
        # see status of dhcpd server with: sudo systemctl status dhcpd
        # edit the config file for the dhcpd server with: sudo nano /etc/dhcp/dhcpd.conf

        # function generator, used for sending pulses

        if self.use_client:
            # Use client connection via TCP server
            from client_keysight33622A import ClientKeysight33622A
            self.fg = ClientKeysight33622A()
        else:
            # Use direct VISA connection
            self.fg = keysight33622A("10.9.0.18")


        # self.fg = keysight33622A("10.9.0.18")
        self.fg.connect()
        self.fg.setup_pulse(width=0.050) # 50 ms
        self.fg.set_output(1, 1)

        self.pulse_amplitude = pulse_amplitude


    def cryo_mode(self):
        self.pulse_amplitude = 2.5
        
    def room_temp_mode(self):
        self.pulse_amplitude = 5.0

    def flip_left(self, channel: int, verification: Verification):
        self.wire_switch(channel, verification)
        time.sleep(0.15)
        print("SENDING POSITIVE PULSE")
        if self.fg:
            self.fg.trigger_with_polarity(1, self.pulse_amplitude, "POS")
        else:
            if DEV_MODE:
                print("DEV_MODE: skipping POS pulse trigger")
            else:
                print("Function generator unavailable: skipping POS pulse trigger")
        time.sleep(0.1)

        time.sleep(EXTRA_SLEEP_TIME)

    def flip_right(self, channel: int, verification: Verification):
        self.wire_switch(channel, verification)
        time.sleep(0.15)
        print("SENDING NEGATIVE PULSE")
        if self.fg:
            self.fg.trigger_with_polarity(1, self.pulse_amplitude, "NEG")
        else:
            if DEV_MODE:
                print("DEV_MODE: skipping NEG pulse trigger")
            else:
                print("Function generator unavailable: skipping NEG pulse trigger")
        time.sleep(0.1)
        time.sleep(EXTRA_SLEEP_TIME)

    def wire_switch(self, channel: int, verification: Verification):
        """
        Wire switch the function generator to the specified channel.
        """
        channel = 7 - channel
        binary = bin(channel)[2:]
        # binary should be 3 digits long
        binary = binary.zfill(3)
        print("binary: ", binary)

        current_node = self.top_node

        for bit in enumerate(binary):
            if type(current_node) is not Node:
                print("Reached a None or end node, stopping.")
                continue

            print(
                f"starting with bit {bit} of {binary} at node {current_node.relay_name}"
            )
            if bit[1] == "0":
                # if not current_node.polarity:
                current_node.polarity = True
                idx = int(current_node.relay_index)
                # print(f"flip cryo relay {current_node.relay_index} left")
                # v.pulse_controller.flip_left(idx, verification)
                print("turning OFF relay ", idx)
                self.relay_board.turn_off(idx, verification)
            else:
                # if current_node.polarity:
                # print(f"flip cryo relay {current_node.relay_index} right")
                current_node.polarity = False
                idx = int(current_node.relay_index)
                # v.pulse_controller.flip_right(idx, verification)
                print("turning ON relay ", idx)
                self.relay_board.turn_on(idx, verification)

            current_node = current_node.to_next()

        # time.sleep(10)

    def cleanup(self):
        self.relay_board.Reset()
        super().cleanup()
        if hasattr(self, "fg") and self.fg:
            self.fg.disconnect()
