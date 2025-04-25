from fastapi import FastAPI, Request
import asyncio
from typing import Annotated
from contextlib import asynccontextmanager  # Import asynccontextmanager

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
# from multiprocessing.managers import SyncManager
# from multiprocessing.synchronize import Event as EventType
import requests
import argparse

import AppKit

from pulse_controller import (
    PulseController,
    SimpleRelayPulseController,
    FunctionGeneratorPulseController,
)
from node import Node, MaybeNode
from models import (
    ButtonLabelsBase,
    Channel,
    ToggleRequest,
    SwitchState,
    Tree,
    T,
)


# print("THISS: ", THISS)
from location import WEB_DIR
import mimetypes
from uvicorn import Config, Server

from sqlmodel import Session, select
from db import (
    get_session,
    create_db_and_tables,
    ButtonLabels,
    InitResponse,
    InitResponsePublic,
    ButtonLabelsBase,
)

FUNCTION_GEN = True

# Define the annotated dependency
DBSession = Annotated[Session, Depends(get_session)]


class CryoRelayManager:
    """
    Manages the cryogenic teledyne relays and their state.
    """

    def __init__(self, function_gen: bool = True):
        # Initialize switch

        if function_gen:
            self.pulse_controller: PulseController = FunctionGeneratorPulseController()
        else:
            self.pulse_controller: PulseController = SimpleRelayPulseController()

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


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created.")
    yield
    # Code to run on shutdown (if any)
    print("Application shutting down.")


# Pass the lifespan manager to the FastAPI app
app = FastAPI(lifespan=lifespan)


# Add CORS middleware with permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
FRAMELESS: bool = False


# https://numato.com/docs/8-channel-usb-relay-module/
# OSX: ls /dev/*usb*


def add_buttons(window: webview.Window):
    window.native.standardWindowButton_(AppKit.NSWindowCloseButton).setHidden_(False)  # type: ignore
    window.native.standardWindowButton_(AppKit.NSWindowMiniaturizeButton).setHidden_(  # type: ignore
        False
    )
    window.native.standardWindowButton_(AppKit.NSWindowZoomButton).setHidden_(False)  # type: ignore


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
    state: dict[str, SwitchState | int] = {}
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
        else:
            v.pulse_controller.flip_left(idx, verification)
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
            if (not current_node.polarity) or (not REMEMBER_STATE):
                current_node.polarity = True
                idx = int(current_node.relay_index)
                print(f"flip cryo relay {current_node.relay_index} left")
                v.pulse_controller.flip_left(idx, verification)
        else:
            if (current_node.polarity) or (not REMEMBER_STATE):
                print(f"flip cryo relay {current_node.relay_index} right")
                current_node.polarity = False
                idx = int(current_node.relay_index)
                v.pulse_controller.flip_right(idx, verification)
        current_node = current_node.to_next()
    update_color()
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
    print("cryo-channel requested: ", channel.number)
    return channel_to_state(channel.number, channel.verification)


@app.get("/tree")
def get_tree():
    # this will error if the tree is not initialized
    v: CryoRelayManager = app.state.v
    try:
        return v.tree.tree_state
    except:
        print("/tree endpoint called before initialization")


@app.get("/initialize", response_model=InitResponsePublic)
async def initialize(session: DBSession):  # Use DBSession
    """
    Initializes the application state, including the tree state and button labels.
    """
    tree_state: Tree | None = None
    labels: ButtonLabels | None = None  # Expecting the DB model

    try:
        # Check if CryoRelayManager is already initialized in app state
        if hasattr(app.state, "v") and app.state.v:
            tree_state = app.state.v.tree.tree_state
        else:
            # Initialize CryoRelayManager if not already done
            manager = await asyncio.to_thread(CryoRelayManager, FUNCTION_GEN)
            app.state = State({"v": manager})
            tree_state = app.state.v.tree.tree_state

        # Fetch button labels from the database
        statement = select(ButtonLabels).where(ButtonLabels.id == 1)
        results = session.exec(statement)
        labels = results.one_or_none()

        if not labels:
            # Should not happen if on_startup worked, but handle defensively
            print("Error: Button labels not found in DB during initialization.")
            raise HTTPException(status_code=500, detail="Button labels not found")

        if not tree_state:
            # Should not happen if initialization logic above worked
            print("Error: Tree state not available during initialization.")
            raise HTTPException(
                status_code=500, detail="Tree state initialization failed"
            )

        # this should get filtered into InitResponsePublic
        return InitResponse(
            tree_state=tree_state,
            button_labels=labels,  # Pass the validated public model instance
        )

    except Exception as e:
        print(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {e}")


@app.get("/button_labels", response_model=ButtonLabelsBase)
def get_button_labels(session: DBSession):
    statement = select(ButtonLabels).where(ButtonLabels.id == 1)
    results = session.exec(statement)
    db_labels = results.one_or_none()
    if not db_labels:
        raise HTTPException(status_code=404, detail="Button labels not found")

    return db_labels


@app.post("/button_labels", response_model=ButtonLabelsBase)  # Use public model
def update_button_labels(
    labels: ButtonLabelsBase,
    session: DBSession,  # Use base model for input
):
    statement = select(ButtonLabels).where(ButtonLabels.id == 1)
    results = session.exec(statement)
    db_labels = results.one_or_none()

    if not db_labels:
        print("Button labels row not found, creating one.")
        # Create DB model instance from the input base model
        db_labels = ButtonLabels(id=1, **labels.model_dump())
    else:
        # Update existing labels using data from the input base model
        for key, value in labels.model_dump().items():
            # Ensure we don't try to set 'id' if it somehow slips in
            if key != "id":
                setattr(db_labels, key, value)

    session.add(db_labels)
    session.commit()
    session.refresh(db_labels)
    print("Button labels updated in DB.")

    # Remove manual dictionary creation
    # response_dict = {k: v for k, v in db_labels.model_dump().items() if k != 'id'}
    # Return the DB object directly; FastAPI filters based on response_model
    return db_labels


@app.post("/switch")
def toggle_switch(toggle: ToggleRequest):
    v: CryoRelayManager = app.state.v

    sw = v.nodes[toggle.number - 1]
    # print("the switch to toggle: ", sw.relay_name)

    if not sw.polarity:
        sw.polarity = True
        idx = int(sw.relay_index)
        v.pulse_controller.flip_left(idx, toggle.verification)

    else:
        sw.polarity = False
        idx = int(sw.relay_index)
        v.pulse_controller.flip_right(idx, toggle.verification)

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
