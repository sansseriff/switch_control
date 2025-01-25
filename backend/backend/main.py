import subprocess

from fastapi import FastAPI, Request
from uvicorn import run
import multiprocessing
from pathlib import Path

# from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from numatoRelay import Relay
import time
import webview
import tempfile

from verification import Verification

# from location import THISS


# print("THISS: ", THISS)
from location import WEB_DIR
import mimetypes
from uvicorn import Config, Server


app = FastAPI()


mimetypes.init()

PULSE_TIME = 40
SLEEP_TIME = 0.005
REMEMBER_STATE: bool = True


# https://numato.com/docs/8-channel-usb-relay-module/
# OSX: ls /dev/*usb*


def start_window(pipe_send, url_to_load):
    def on_closed():
        pipe_send.send("closed")

    win = webview.create_window(
        "Switch Control", url=url_to_load, resizable=True, width=800, height=412
    )
    win.events.closed += on_closed
    webview.start(storage_path=tempfile.mkdtemp())


class UvicornServer(multiprocessing.Process):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()


app.mount("/assets", StaticFiles(directory=Path(WEB_DIR, "assets")), name="")


# return the index.html file on browser
@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
    mimetypes.add_type("application/javascript", ".js")
    return FileResponse(Path(WEB_DIR, "index.html"))


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

    return ports


# Initialize the switch with one of the detected serial ports
serial_ports = get_serial_ports()
print("serial ports: ", serial_ports)
if serial_ports:
    switch = Relay(serial_ports[0])
else:
    switch = Relay(None)  # debug mode


@app.get("/")
def hello():
    return "Hello, World!"


# export interface ChannelVerification {
#  verified: boolean;
#  timestamp: number;
#  userConfirmed: boolean;
# }


class Channel(BaseModel):
    number: int
    verification: Verification


class Sw(BaseModel):
    number: int
    verification: Verification


class SwitchState(BaseModel):
    pos: bool
    color: bool


class Tree(BaseModel):
    R1: SwitchState
    R2: SwitchState
    R3: SwitchState
    R4: SwitchState
    R5: SwitchState
    R6: SwitchState
    R7: SwitchState
    activated_channel: int


tree_state = Tree(
    R1=SwitchState(pos=False, color=False),
    R2=SwitchState(pos=False, color=False),
    R3=SwitchState(pos=False, color=False),
    R4=SwitchState(pos=False, color=False),
    R5=SwitchState(pos=False, color=False),
    R6=SwitchState(pos=False, color=False),
    R7=SwitchState(pos=False, color=False),
    activated_channel=0,
)


class T(BaseModel):
    tree_state: Tree
    activated_channel: int


tree = T(tree_state=tree_state, activated_channel=0)


class Node:
    def __init__(self, relay_name: str):
        self.left: Node | None | int = None
        self.right: Node | None | int = None

        self.relay_name = relay_name
        self.relay_index = int(relay_name[1])  # R1 -> 1
        self.polarity = False  # False/0 is right, True/1 is left

        self.in_use = False

    def to_next(self):
        # process to whichever switch is 'pointed to' by this switch
        if self.polarity:
            return self.left
        else:
            return self.right


def flatten_tree(root: Node) -> Tree:
    state = {}
    state["activated_channel"] = T.activated_channel
    queue = [root]

    while queue:
        current_node = queue.pop(0)
        if current_node:
            state[current_node.relay_name] = SwitchState(
                pos=current_node.polarity, color=current_node.in_use
            )

            if isinstance(current_node.left, Node):
                queue.append(current_node.left)
            if isinstance(current_node.right, Node):
                queue.append(current_node.right)

    print("state: ", state)
    return Tree(**state)


#           ___  R1 ____
#         /              \
#       R2                R3
#    /      \          /      \
#   R4       R5       R6       R7
#  /  \     /  \     /  \     /  \
# 7    6   5    4   3    2   1    0   # channel according to the relay board
# 8    7   6    5   4    3   2    1   # channel according to the user

nodes = [Node(f"R{i}") for i in range(1, 8)]
R1, R2, R3, R4, R5, R6, R7 = nodes

# set up the tree
R1.left = R2
R1.right = R3
R2.left = R4
R2.right = R5
R3.left = R6
R3.right = R7

R4.left = 7
R4.right = 6
R5.left = 5
R5.right = 4
R6.left = 3
R6.right = 2
R7.left = 1
R7.right = 0


def init_tree():
    switch.turn_on(0)

    for node in nodes:
        time.sleep(SLEEP_TIME)
        node.polarity = False
        idx = int(node.relay_index)
        switch.send_pulse(idx, PULSE_TIME)

    switch.turn_off(0)

    update_color()
    tree.tree_state = flatten_tree(R1)

    return tree.tree_state


def re_assert_tree():
    current_node = R1

    while current_node is not None:
        idx = int(current_node.relay_index)
        if current_node.polarity is True:
            switch.turn_off(0)
            time.sleep(SLEEP_TIME)
            switch.send_pulse(idx, PULSE_TIME)

        else:
            switch.turn_on(0)
            time.sleep(SLEEP_TIME)
            switch.send_pulse(idx, PULSE_TIME)
            time.sleep(SLEEP_TIME)
            switch.turn_off(0)
        time.sleep(SLEEP_TIME)
        current_node = current_node.to_next()

        if type(current_node) is int:
            break

    update_color()
    tree.tree_state = flatten_tree(R1)

    return tree.tree_state


def update_color():
    for node in nodes:
        node.in_use = False

    current_node = R1
    while current_node is not None:
        if type(current_node) is int:
            T.activated_channel = current_node
            current_node = None
            break

        current_node.in_use = True
        current_node = current_node.to_next()

    print("current output channel: ", T.activated_channel)


def channel_to_state(channel: int):
    """
    take in user-numbering channel (1-8)
    """

    if channel < 0 or channel > 7:
        print("Invalid channel number, stopping.")
        return

    # flip the channel numbering
    channel = 7 - channel

    # switch from user to relay channel numbering
    # channel -= 1
    binary = bin(channel)[2:]
    # binary should be 3 digits long
    binary = binary.zfill(3)
    current_node = R1

    for bit in enumerate(binary):
        print(bit[1])

        if current_node is None:
            print("Reached a None node, stopping.")
            return

        time.sleep(SLEEP_TIME)
        if bit[1] == "0":
            # current_node = current_node.left

            if current_node.polarity != True or (not REMEMBER_STATE):
                # flip the relay
                current_node.polarity = True

                idx = int(current_node.relay_index)
                switch.turn_off(0)

                time.sleep(SLEEP_TIME)

                switch.send_pulse(idx, PULSE_TIME)

                time.sleep(SLEEP_TIME)

        else:
            if (current_node.polarity != False) or (not REMEMBER_STATE):
                # flip the relay
                current_node.polarity = False

                idx = int(current_node.relay_index)
                switch.turn_on(0)
                time.sleep(SLEEP_TIME)

                switch.send_pulse(idx, PULSE_TIME)

                time.sleep(SLEEP_TIME)
                switch.turn_off(0)
                time.sleep(SLEEP_TIME)

        current_node = current_node.to_next()

    # print("BEFORE: ", "R1:", tree.tree_state.R1.color, "  R2:", tree.tree_state.R2.color, "  R3: ", tree.tree_state.R3.color, "  R4:", tree.tree_state.R4.color, "  R5:", tree.tree_state.R5.color, "  R6:", tree.tree_state.R6.color, "  R7:", tree.tree_state.R7.color)
    update_color()
    # print("After: ", "R1:", tree.tree_state.R1.color, "  R2:", tree.tree_state.R2.color, "  R3: ", tree.tree_state.R3.color, "  R4:", tree.tree_state.R4.color, "  R5:", tree.tree_state.R5.color, "  R6:", tree.tree_state.R6.color, "  R7:", tree.tree_state.R7.color)
    tree.tree_state = flatten_tree(R1)

    return tree.tree_state


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    print("detail: ", exc)
    return JSONResponse(
        status_code=400,
        content={"message": "Bad Request", "detail": str(exc)},
    )


@app.post("/reset")
def reset(verification: Verification):
    return init_tree(verification)


# Make sure the tree is in the correct state by re-submitting desired path
@app.post("/re_assert")
def re_assert(verification: Verification):
    return re_assert_tree(verification)


@app.post("/channel")
def request_channel(channel: Channel):
    print("channel number: ", channel.number)
    return channel_to_state(channel.number)


@app.get("/tree")
def get_tree():
    # print("tree state: ", tree_state)
    return tree.tree_state


@app.post("/switch")
def toggle_switch(swp: Sw):
    sw = nodes[swp.number - 1]
    print("the switch to toggle: ", sw.relay_name)

    if sw.polarity == False:
        # flip the relay
        sw.polarity = True

        idx = int(sw.relay_index)
        switch.turn_off(0)
        time.sleep(SLEEP_TIME)
        switch.send_pulse(idx, PULSE_TIME)

    else:
        # flip the relay
        sw.polarity = False

        idx = int(sw.relay_index)
        switch.turn_on(0)
        time.sleep(SLEEP_TIME)
        switch.send_pulse(idx, PULSE_TIME)
        time.sleep(SLEEP_TIME)
        switch.turn_off(0)

    update_color()
    tree.tree_state = flatten_tree(R1)
    return tree.tree_state


# don't want to heat things up unnecessarily
# init_tree()

# if __name__ == "__main__":
#     multiprocessing.freeze_support()  # For Windows support

#     run(app, host="0.0.0.0", port=9050, reload=False, workers=1)


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8000
    conn_recv, conn_send = multiprocessing.Pipe()

    windowsp = multiprocessing.Process(
        target=start_window, args=(conn_send, f"http://{server_ip}:{server_port}/")
    )
    windowsp.start()

    config = Config("main:app", host=server_ip, port=server_port, log_level="debug")
    instance = UvicornServer(config=config)
    instance.start()

    window_status = ""
    while "closed" not in window_status:
        # get a unit of work
        window_status = conn_recv.recv()
        # report
        print(f"got {window_status}", flush=True)

    instance.stop()
