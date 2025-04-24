from fastapi import FastAPI, Request
import asyncio

# from uvicorn import run
import multiprocessing
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends

import time
import webview
import tempfile

from verification import Verification
from multiprocessing.connection import Connection
from starlette.datastructures import State
from fastapi import HTTPException
from multiprocessing import Manager, Event

# import SyncManager type
from multiprocessing.managers import SyncManager
from multiprocessing.synchronize import Event as EventType
import requests
import argparse  # Add this import

import AppKit

from pulse_controller import PulseController  # Import the PulseController class

# import Event type from multiprocessing


# from location import THISS


pulse_mode = True


# print("THISS: ", THISS)
from location import WEB_DIR
import mimetypes
from uvicorn import Config, Server


class Channel(BaseModel):
    number: int
    verification: Verification


class ToggleRequest(BaseModel):
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


class T(BaseModel):
    tree_state: Tree
    activated_channel: int


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


MaybeNode = Node | int | None


# # Create a Manager instance
# manager = Manager()

# # Create a shared dictionary
# shared_state = manager.dict()


# Create an event for cleanup
# cleanup_event = Event()


class CryoRelayManager:
    """
    Manages the cryogenic teledyne relays and their state.
    """

    def __init__(self):
        # Initialize switch
        self.pulse_controller = PulseController()
        # Initialize nodes
        self.nodes = [Node(f"R{i}") for i in range(1, 8)]
        self.R1, self.R2, self.R3, self.R4, self.R5, self.R6, self.R7 = self.nodes
        self.top_node: MaybeNode = self.R1

        #           ___  R1 ____
        #         /              \
        #       R2                R3
        #    /      \          /      \
        #   R4       R5       R6       R7
        #  /  \     /  \     /  \     /  \
        # 7    6   5    4   3    2   1    0   # channel according to the relay board
        # 8    7   6    5   4    3   2    1   # channel according to the user numbering

        # Set up tree structure
        self.R1.left = self.R2
        self.R1.right = self.R3
        self.R2.left = self.R4
        self.R2.right = self.R5
        self.R3.left = self.R6
        self.R3.right = self.R7

        self.R4.left = 7
        self.R4.right = 6
        self.R5.left = 5
        self.R5.right = 4
        self.R6.left = 3
        self.R6.right = 2
        self.R7.left = 1
        self.R7.right = 0

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

    def cleanup(self):
        self.pulse_controller.cleanup()


app = FastAPI()
# app.state = State({"v": StateManager()})

# Add CORS middleware with permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# Add dependency
def get_state_manager():
    print("the manager: ", app.state.v)
    print("something inside: ", app.state.v.pulse_controller)
    return app.state.v.v


mimetypes.init()

PULSE_TIME = 50
SLEEP_TIME = 0.050
REMEMBER_STATE: bool = False
FRAMELESS: bool = True


# https://numato.com/docs/8-channel-usb-relay-module/
# OSX: ls /dev/*usb*


def add_buttons(window: webview.Window):
    window.native.standardWindowButton_(AppKit.NSWindowCloseButton).setHidden_(False)
    window.native.standardWindowButton_(AppKit.NSWindowMiniaturizeButton).setHidden_(
        False
    )
    window.native.standardWindowButton_(AppKit.NSWindowZoomButton).setHidden_(False)


def start_window(pipe_send: Connection, url_to_load: str, debug: bool = False):
    def on_closed():
        pipe_send.send("closed")

    win = webview.create_window(
        "Switch Control",
        url=url_to_load,
        resizable=True,
        width=800,
        height=412,
        frameless=FRAMELESS,
        easy_drag=False,
    )

    # https://github.com/r0x0r/pywebview/issues/1496#issuecomment-2410471185

    if FRAMELESS:
        win.events.before_load += add_buttons
    win.events.closed += on_closed
    print("debug is: ", debug)
    webview.start(storage_path=tempfile.mkdtemp(), debug=debug)
    win.evaluate_js("window.special = 3")
    # print(f"Active GUI backend: {webview._webview.gui.__name__}")


class UvicornServer(multiprocessing.Process):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config

    def stop(self):
        self.terminate()

    def run(self):
        print("running server")
        self.server.run()


app.mount("/assets", StaticFiles(directory=Path(WEB_DIR, "assets")), name="")


# return the index.html file on browser
@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
    mimetypes.add_type("application/javascript", ".js")
    return FileResponse(Path(WEB_DIR, "index.html"))


def flatten_tree(root: MaybeNode) -> Tree:
    state = {}
    state["activated_channel"] = T.activated_channel
    queue = [root]

    while queue:
        current_node = queue.pop(0)
        if type(current_node) is Node:
            state[current_node.relay_name] = SwitchState(
                pos=current_node.polarity, color=current_node.in_use
            )

            if isinstance(current_node.left, Node):
                queue.append(current_node.left)
            if isinstance(current_node.right, Node):
                queue.append(current_node.right)

    # print("state: ", state)
    return Tree(**state)


def init_tree(verification: Verification):
    v: CryoRelayManager = app.state.v

    # v.pulse_controller.turn_on(0, verification)

    for node in v.nodes:
        # time.sleep(SLEEP_TIME)
        node.polarity = False
        idx = int(node.relay_index)
        v.pulse_controller.flip_right(idx, verification)

    # app.state.v.switch.turn_off(0, verification)

    update_color()
    app.state.v.tree.tree_state = flatten_tree(v.top_node)

    return v.tree.tree_state


def re_assert_tree(verification: Verification):
    v: CryoRelayManager = app.state.v
    current_node = v.top_node

    while type(current_node) is Node:
        idx = int(current_node.relay_index)
        if current_node.polarity is True:
            v.pulse_controller.flip_right(idx, verification)
            # app.state.v.switch.turn_off(0, verification)
            # time.sleep(SLEEP_TIME)
            # app.state.v.switch.send_pulse(idx, PULSE_TIME, verification)

        else:
            v.pulse_controller.flip_left(idx, verification)
            # app.state.v.switch.turn_on(0, verification)
            # time.sleep(SLEEP_TIME)
            # app.state.v.switch.send_pulse(idx, PULSE_TIME, verification)
            # time.sleep(SLEEP_TIME)
            # app.state.v.switch.turn_off(0, verification)
        # time.sleep(SLEEP_TIME)
        current_node = current_node.to_next()

        if type(current_node) is int:
            break

    update_color()
    app.state.v.tree.tree_state = flatten_tree(v.top_node)

    return app.state.v.tree.tree_state


def update_color():
    for node in app.state.v.nodes:
        node.in_use = False

    current_node = app.state.v.top_node
    while current_node is not None:
        if type(current_node) is int:
            T.activated_channel = current_node
            current_node = None
            break

        if type(current_node) is Node:
            current_node.in_use = True
            current_node = current_node.to_next()

    print("current output channel: ", T.activated_channel)


def channel_to_state(
    channel: int,
    verification: Verification,
):
    """
    take in user-numbering channel (1-8)
    """

    v: CryoRelayManager = app.state.v

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
    current_node = app.state.v.top_node

    for bit in enumerate(binary):
        print(bit[1])

        if type(current_node) is not Node:
            print("Reached a None or end node, stopping.")
            return

        time.sleep(SLEEP_TIME)

        if bit[1] == "0":
            # want cryo-relay to point left

            if (not current_node.polarity) or (not REMEMBER_STATE):
                # flip the relay
                current_node.polarity = True

                idx = int(current_node.relay_index)

                v.pulse_controller.flip_left(idx, verification)
                # app.state.v.switch.turn_off(0, verification)
                # time.sleep(SLEEP_TIME)
                # app.state.v.switch.send_pulse(idx, PULSE_TIME, verification)
                # time.sleep(SLEEP_TIME)

        else:
            if (current_node.polarity) or (not REMEMBER_STATE):
                # flip the relay
                current_node.polarity = False

                idx = int(current_node.relay_index)

                v.pulse_controller.flip_right(idx, verification)
                # app.state.v.switch.turn_on(0, verification)
                # time.sleep(SLEEP_TIME)
                # app.state.v.switch.send_pulse(idx, PULSE_TIME, verification)
                # time.sleep(SLEEP_TIME)
                # app.state.v.switch.turn_off(0, verification)
                # time.sleep(SLEEP_TIME)

        current_node = current_node.to_next()

    # print("BEFORE: ", "R1:", tree.tree_app.state.v.R1.color, "  R2:", tree.tree_app.state.v.R2.color, "  R3: ", tree.tree_app.state.v.R3.color, "  R4:", tree.tree_app.state.v.R4.color, "  R5:", tree.tree_app.state.v.R5.color, "  R6:", tree.tree_app.state.v.R6.color, "  R7:", tree.tree_app.state.v.R7.color)
    update_color()
    # print("After: ", "R1:", tree.tree_app.state.v.R1.color, "  R2:", tree.tree_app.state.v.R2.color, "  R3: ", tree.tree_app.state.v.R3.color, "  R4:", tree.tree_app.state.v.R4.color, "  R5:", tree.tree_app.state.v.R5.color, "  R6:", tree.tree_app.state.v.R6.color, "  R7:", tree.tree_app.state.v.R7.color)
    app.state.v.tree.tree_state = flatten_tree(v.top_node)

    return v.tree.tree_state


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
    return channel_to_state(channel.number, channel.verification)


@app.get("/tree")
def get_tree():
    # this will error if the tree is not initialized
    v: CryoRelayManager = app.state.v
    try:
        return v.tree.tree_state
    except:
        print("/tree endpoint called before initialization")


@app.get("/initialize")
async def initialize():
    """
    In a simple FastAPI app that runs in the main thread, you'd be able to access data in the
    global namespace. CryoRelayManager could just be initialized at the top of the file
    and used in any function as a global variable. But since pywebview must run in the main
    process and fastapi runs in a separate process, accessing state like CryoRelayManager is
    more complicated. Starlette (on which fastapi is built) provides a way to store state
    in the app object, which is a dictionary-like object that can be used to store data
    that needs to be shared across requests. This is what we do here.

    Todo: check out FastAPI Dependencies, for use instead of app.state
    """
    val = False

    try:
        # v: CryoRelayManager =
        val = app.state.v.tree.tree_state
    except AttributeError:
        print("tree state not initialized")

    if val:
        print("already initialized")
        return app.state.v.tree.tree_state

    try:
        manager = await asyncio.to_thread(CryoRelayManager)
        app.state = State({"v": manager})

        # after the above two lines, this call should work
        tree_state = app.state.v.tree.tree_state
        return tree_state

    except Exception as e:
        print(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail="Initialization failed")


@app.post("/switch")
def toggle_switch(toggle: ToggleRequest):
    v: CryoRelayManager = app.state.v

    sw = v.nodes[toggle.number - 1]
    print("the switch to toggle: ", sw.relay_name)

    if not sw.polarity:
        # flip the relay
        sw.polarity = True

        idx = int(sw.relay_index)

        v.pulse_controller.flip_left(idx, toggle.verification)
        # app.state.v.switch.turn_off(0, toggle.verification)
        # time.sleep(SLEEP_TIME)
        # app.state.v.switch.send_pulse(idx, PULSE_TIME, toggle.verification)

    else:
        # flip the relay
        sw.polarity = False

        idx = int(sw.relay_index)
        v.pulse_controller.flip_right(idx, toggle.verification)
        # app.state.v.switch.turn_on(0, toggle.verification)
        # time.sleep(SLEEP_TIME)
        # app.state.v.switch.send_pulse(idx, PULSE_TIME, toggle.verification)
        # time.sleep(SLEEP_TIME)
        # app.state.v.switch.turn_off(0, toggle.verification)

    update_color()
    app.state.v.tree.tree_state = flatten_tree(v.top_node)
    return v.tree.tree_state


@app.post("/cleanup")
async def cleanup():
    v: CryoRelayManager = app.state.v
    try:
        if app.state and v:
            v.cleanup()
            print("Cleanup done")
        return {"ok": True}
    except Exception as e:
        print(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Switch Control Backend")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    log_level = "debug" if args.debug else None

    server_ip = "0.0.0.0"
    webview_ip = "localhost"
    server_port = 8854  # use a more random port
    conn_recv, conn_send = multiprocessing.Pipe()
    # init_event = multiprocessing.Event()  # Create an Event object

    # Start server first
    # user 1 worker for easier data sharing
    config = Config(
        "main:app", host=server_ip, port=server_port, log_level=log_level, workers=1
    )
    instance = UvicornServer(config=config)
    instance.start()

    print("Server started")

    # # Give server time to initialize
    # time.sleep(1)

    # Then start window

    windowsp = multiprocessing.Process(
        target=start_window,
        args=(conn_send, f"http://{webview_ip}:{server_port}/", args.debug),
    )

    windowsp.start()

    window_status = ""
    while "closed" not in window_status:
        window_status = conn_recv.recv()
        print(f"got {window_status}", flush=True)

    # Call the /cleanup endpoint
    try:
        response = requests.post(f"http://{server_ip}:{server_port}/cleanup")
    except Exception as e:
        print(f"Exception while calling cleanup endpoint: {e}")

    instance.stop()
