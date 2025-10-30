from fastapi import FastAPI, Request
import asyncio
from typing import Annotated
from contextlib import asynccontextmanager  # Import asynccontextmanager

# from uvicorn import run
import multiprocessing
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
import threading
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from starlette.responses import StreamingResponse

import time
import webview
import tempfile

from verification import Verification
from multiprocessing.connection import Connection
from fastapi import HTTPException

# import SyncManager type
# from multiprocessing.managers import SyncManager
# from multiprocessing.synchronize import Event as EventType
import argparse

# import AppKit

from pulse_controller import (
    PulseController,
    SimpleRelayPulseController,
    FunctionGeneratorPulseController,
    ClientKeysightPulseGenerator,
    make_pulse_generator,
)
from node import Node, MaybeNode
from models import (
    ButtonLabelsBase,
    Channel,
    ToggleRequest,
    SwitchState,
    Tree,
    T,
    SettingsBase,
    PulseGenRequest,
    PulseGenInfo,
)


from ampProtector import AmpProtector
from typing import Any
from pydantic import BaseModel

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
    Settings,
    TreeState,
)

FUNCTION_GEN = True

# Define the annotated dependency
DBSession = Annotated[Session, Depends(get_session)]


class CryoRelayManager:
    """
    Manages the cryogenic teledyne relays and their state.

    CryoRelayManager is concerned with the layout of the cryogenic relays. NOT how they are actuated.

    All the details of actuating a relay are left to the internal pulse_controller, for which there's multiple types.
    """

    def __init__(self, function_gen: bool = True):
        # Initialize switch and synchronization
        self.lock = threading.Lock()
        # Event loop reference for cross-thread scheduling (set by lifespan)
        self.loop: asyncio.AbstractEventLoop | None = None
        # SSE subscribers: each is an asyncio.Queue of JSON strings
        self.subscribers: set[asyncio.Queue[str]] = set()

        if function_gen:
            # override!!
            self.pulse_controller: PulseController = FunctionGeneratorPulseController(
                generator=ClientKeysightPulseGenerator()
            )
            # self.pulse_controller: PulseController = FunctionGeneratorPulseController()
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

        # if this is enabled, and the supply is not connected,
        # you'll get an indecipherable error
        # I have another program that accesses the keysight supply at the
        # same time. Using sockets and a client connection to allow
        # multiple python processes to access the VISA device
        self.amp_protector = AmpProtector(on=True, disabled=False, use_client=True)

    def cleanup(self):
        self.pulse_controller.cleanup()

    # ============== SSE helper methods ==============
    async def _broadcast_json(self, json_str: str):
        """Broadcast a JSON string to all subscribers without blocking.
        Removes subscribers that are no longer accepting messages.
        """
        to_remove: list[asyncio.Queue[str]] = []
        for q in list(self.subscribers):
            try:
                q.put_nowait(json_str)
            except asyncio.QueueFull:
                to_remove.append(q)
            except Exception:
                to_remove.append(q)
        for q in to_remove:
            self.subscribers.discard(q)

    async def broadcast_tree(self):
        """Serialize current tree_state and broadcast to all subscribers."""
        try:
            json_str = self.tree.tree_state.model_dump_json()
        except Exception:
            # Fallback: build from flatten_tree if needed
            json_str = flatten_tree(self.top_node).model_dump_json()
        await self._broadcast_json(json_str)

    def broadcast_tree_sync(self):
        """Schedule broadcast_tree from non-async contexts (e.g., threadpool)."""
        if self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast_tree(), self.loop)
            except RuntimeError:
                # Loop may be closed; ignore
                pass


class Services:
    """Container for long-lived services"""

    def __init__(self, cryo: CryoRelayManager):
        self.cryo = cryo


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created.")
    # Initialize hardware/services once for the process
    cryo_manager = await asyncio.to_thread(CryoRelayManager, FUNCTION_GEN)
    # Store current running loop so CryoRelayManager can schedule async work from threads
    cryo_manager.loop = asyncio.get_running_loop()
    app.state.services = Services(cryo=cryo_manager)
    yield
    # Code to run on shutdown (if any)
    print("Application shutting down.")
    try:
        app.state.services.cryo.cleanup()
        print("CryoRelayManager cleaned up.")
    except Exception as e:
        print(f"Error during CryoRelayManager cleanup: {e}")


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


# Dependencies to access services without touching app.state in handlers
def get_services(request: Request) -> Services:
    return request.app.state.services


def get_cryo(services: Annotated[Services, Depends(get_services)]) -> CryoRelayManager:
    return services.cryo


class PulseGenResponse(BaseModel):
    ok: bool
    info: PulseGenInfo


mimetypes.init()

PULSE_TIME = 50
SLEEP_TIME = 0.030
FRAMELESS: bool = False


# https://numato.com/docs/8-channel-usb-relay-module/
# OSX: ls /dev/*usb*


# def add_buttons(window: webview.Window):
#     window.native.standardWindowButton_(AppKit.NSWindowCloseButton).setHidden_(False)  # type: ignore
#     window.native.standardWindowButton_(AppKit.NSWindowMiniaturizeButton).setHidden_(  # type: ignore
#         False
#     )
#     window.native.standardWindowButton_(AppKit.NSWindowZoomButton).setHidden_(False)  # type: ignore


def start_window(pipe_send: Connection, url_to_load: str, debug: bool = False):

    # NOTE: you NEED this on some computers. If the fastapi server isn't ready, then the webview hangs with a blank white page.
    time.sleep(0.3)
    # TODO: figure out how to send a message from fastapi to pywebview that it's ready

    def on_closed():
        pipe_send.send("closed")

    _win = webview.create_window(
        "Switch Control",
        url=url_to_load,
        resizable=True,
        width=800,
        height=430,
        frameless=FRAMELESS,
        easy_drag=False,
    )
    # webview.start(debug=False) # NOTE if this is activated, then you don't get graceful shutdown from hitting the close button. (on osx)

    # https://github.com/r0x0r/pywebview/issues/1496#issuecomment-2410471185

    # if FRAMELESS:
    #     win.events.before_load += add_buttons
    _win.events.closed += on_closed
    print("debug is: ", debug)
    # webview.start(storage_path=tempfile.mkdtemp(), debug=debug)
    webview.start(storage_path=tempfile.mkdtemp(), debug=debug)
    # webview.start()
    _win.evaluate_js("window.special = 3")
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


# ============== Server-Sent Events endpoint ==============
@app.get("/events")
async def sse_events(
    request: Request, cryo: Annotated[CryoRelayManager, Depends(get_cryo)]
):
    """Stream TreeState updates to clients using Server-Sent Events (SSE).

    Each message is a JSON-serialized Tree (matching the /tree shape) in a
    standard SSE 'data: ...\n\n' frame. Sends an initial snapshot immediately
    after subscribing, then streams subsequent updates.
    """

    async def event_generator():
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=32)
        # Register this client
        cryo.subscribers.add(queue)
        try:
            # Send the initial state right away
            await queue.put(cryo.tree.tree_state.model_dump_json())
            while True:
                # Disconnect handling via timeout + polling
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    # Keep-alive comment to prevent proxies from closing the connection
                    yield ": keep-alive\n\n"
                    continue
                # Normal data frame
                yield f"data: {data}\n\n"
        finally:
            # Cleanup subscriber
            try:
                cryo.subscribers.discard(queue)
            except Exception:
                pass

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # Allow CORS preflight to succeed for browsers
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(
        event_generator(), media_type="text/event-stream", headers=headers
    )


def flatten_tree(root: MaybeNode) -> Tree:
    # Initialize defaults
    r_states: dict[str, SwitchState] = {
        f"R{i}": SwitchState(pos=False, color=False) for i in range(1, 8)
    }
    queue = [root]

    while queue:
        current_node = queue.pop(0)
        if isinstance(current_node, Node):
            r_states[current_node.relay_name] = SwitchState(
                pos=current_node.polarity, color=current_node.in_use
            )

            if isinstance(current_node.left, Node):
                queue.append(current_node.left)
            if isinstance(current_node.right, Node):
                queue.append(current_node.right)

    return Tree(
        R1=r_states["R1"],
        R2=r_states["R2"],
        R3=r_states["R3"],
        R4=r_states["R4"],
        R5=r_states["R5"],
        R6=r_states["R6"],
        R7=r_states["R7"],
        activated_channel=T.activated_channel,
    )


def init_tree(verification: Verification, cryo: CryoRelayManager):
    v: CryoRelayManager = cryo

    v.amp_protector.turn_off_amp()
    v.pulse_controller.unblock_pulser(verification)

    # v.pulse_controller.turn_on(0, verification)
    with v.lock:
        for node in v.nodes:
            # time.sleep(SLEEP_TIME)
            node.polarity = False
            idx = int(node.relay_index)
            v.pulse_controller.flip_left(idx, verification)

    # app.state.v.switch.turn_off(0, verification)

    update_color(v)
    v.tree.tree_state = flatten_tree(v.top_node)

    v.amp_protector.turn_on_if_previously_on()

    v.pulse_controller.block_pulser(verification)

    return v.tree.tree_state


def re_assert_tree(verification: Verification, cryo: CryoRelayManager):
    v: CryoRelayManager = cryo
    v.amp_protector.turn_off_amp()
    v.pulse_controller.unblock_pulser(verification)
    current_node = v.top_node

    with v.lock:
        while isinstance(current_node, Node):
            idx = int(current_node.relay_index)
            if current_node.polarity is True:
                v.pulse_controller.flip_right(idx, verification)
            else:
                v.pulse_controller.flip_left(idx, verification)
            current_node = current_node.to_next()
            if type(current_node) is int:
                break

    update_color(v)
    v.tree.tree_state = flatten_tree(v.top_node)

    v.amp_protector.turn_on_if_previously_on()
    v.pulse_controller.block_pulser(verification)

    return v.tree.tree_state


def update_color(cryo: CryoRelayManager):
    for node in cryo.nodes:
        node.in_use = False

    current_node = cryo.top_node
    while current_node is not None:
        if type(current_node) is int:
            T.activated_channel = current_node
            current_node = None
            break

        if type(current_node) is Node:
            current_node.in_use = True
            current_node = current_node.to_next()

    print("current output channel: ", T.activated_channel)


def apply_tree_state_to_nodes(cryo: CryoRelayManager, tree_state: Tree):
    """Set node polarities from a persisted Tree and refresh derived fields.
    Does not pulse hardware; only updates in-memory structures.
    """
    mapping = {
        "R1": cryo.R1,
        "R2": cryo.R2,
        "R3": cryo.R3,
        "R4": cryo.R4,
        "R5": cryo.R5,
        "R6": cryo.R6,
        "R7": cryo.R7,
    }
    for key, node in mapping.items():
        state: SwitchState = getattr(tree_state, key)
        node.polarity = bool(state.pos)
    # recompute in_use flags and activated channel
    update_color(cryo)
    cryo.tree.tree_state = flatten_tree(cryo.top_node)


def channel_to_state(
    channel: int,
    verification: Verification,
    cryo: CryoRelayManager,
    tree_memory_mode: bool,
):
    """
    take in user-numbering channel (1-8)
    """
    v: CryoRelayManager = cryo
    v.amp_protector.turn_off_amp()
    v.pulse_controller.unblock_pulser(verification)

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
    current_node = v.top_node

    for bit in enumerate(binary):
        print(bit[1])
        if type(current_node) is not Node:
            print("Reached a None or end node, stopping.")
            return
        time.sleep(SLEEP_TIME)
        if bit[1] == "0":
            if (not current_node.polarity) or (not tree_memory_mode):
                current_node.polarity = True
                idx = int(current_node.relay_index)
                print(f"flip cryo relay {current_node.relay_index} left")
                v.pulse_controller.flip_right(idx, verification)
        else:
            if (current_node.polarity) or (not tree_memory_mode):
                print(f"flip cryo relay {current_node.relay_index} right")
                current_node.polarity = False
                idx = int(current_node.relay_index)
                v.pulse_controller.flip_left(idx, verification)
        current_node = current_node.to_next()
        # After each step, compute and broadcast the intermediate tree state
        update_color(v)
        v.tree.tree_state = flatten_tree(v.top_node)
        v.broadcast_tree_sync()
    # Final state snapshot
    update_color(v)
    v.tree.tree_state = flatten_tree(v.top_node)
    v.broadcast_tree_sync()

    v.amp_protector.turn_on_if_previously_on()
    v.pulse_controller.block_pulser(verification)

    return v.tree.tree_state


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Any):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: Any):
    print("detail: ", exc)
    return JSONResponse(
        status_code=400,
        content={"message": "Bad Request", "detail": str(exc)},
    )


@app.post("/reset")
def reset(
    verification: Verification,
    cryo: Annotated[CryoRelayManager, Depends(get_cryo)],
    session: DBSession,
):
    state = init_tree(verification, cryo)
    # persist
    row = session.exec(select(TreeState).where(TreeState.id == 1)).one_or_none()
    if not row:
        row = TreeState(id=1)
    row.tree_json = state.model_dump_json()
    session.add(row)
    session.commit()
    session.refresh(row)
    return state


# Make sure the tree is in the correct state by re-submitting desired path
@app.post("/re_assert")
def re_assert(
    verification: Verification,
    cryo: Annotated[CryoRelayManager, Depends(get_cryo)],
    session: DBSession,
):
    state = re_assert_tree(verification, cryo)
    row = session.exec(select(TreeState).where(TreeState.id == 1)).one_or_none()
    if not row:
        row = TreeState(id=1)
    row.tree_json = state.model_dump_json()
    session.add(row)
    session.commit()
    session.refresh(row)
    return state


@app.post("/channel")
def request_channel(
    channel: Channel,
    cryo: Annotated[CryoRelayManager, Depends(get_cryo)],
    session: DBSession,
):
    print("cryo-channel requested: ", channel.number)
    # Read current tree_memory_mode from settings so changes are honored at runtime
    settings = session.exec(select(Settings).where(Settings.id == 1)).one_or_none()
    if not settings:
        settings = Settings(id=1)
        session.add(settings)
        session.commit()
        session.refresh(settings)

    state = channel_to_state(
        channel.number, channel.verification, cryo, bool(settings.tree_memory_mode)
    )
    # persist
    if state is not None:
        row = session.exec(select(TreeState).where(TreeState.id == 1)).one_or_none()
        if not row:
            row = TreeState(id=1)
        row.tree_json = state.model_dump_json()
        session.add(row)
        session.commit()
        session.refresh(row)
    return state


@app.get("/tree")
def get_tree(cryo: Annotated[CryoRelayManager, Depends(get_cryo)]):
    # tree is always available after lifespan init
    return cryo.tree.tree_state


@app.get("/tree/persisted", response_model=Tree)
def get_persisted_tree(session: DBSession):
    row = session.exec(select(TreeState).where(TreeState.id == 1)).one_or_none()
    if not row or not row.tree_json:
        raise HTTPException(status_code=404, detail="Persisted tree not found")
    return Tree.model_validate_json(row.tree_json)


@app.get("/initialize", response_model=InitResponsePublic)
async def initialize(
    session: DBSession, cryo: Annotated[CryoRelayManager, Depends(get_cryo)]
):  # Use DBSession
    """
    Initializes the application state, including the tree state and button labels.
    """
    tree_state: Tree | None = None
    labels: ButtonLabels | None = None
    settings: Settings | None = None

    ##

    try:
        # Load last saved tree state from DB (falls back to in-memory if missing)
        row = session.exec(select(TreeState).where(TreeState.id == 1)).one_or_none()
        if row and row.tree_json:
            try:
                tree_state = Tree.model_validate_json(row.tree_json)
                # also apply to running manager
                cryo.tree.tree_state = tree_state
                apply_tree_state_to_nodes(cryo, tree_state)
            except Exception:
                tree_state = cryo.tree.tree_state
        else:
            tree_state = cryo.tree.tree_state

        # Fetch button labels from the database
        statement = select(ButtonLabels).where(ButtonLabels.id == 1)
        results = session.exec(statement)
        labels = results.one_or_none()

        if not labels:
            # Should not happen if on_startup worked, but handle defensively
            print("Error: Button labels not found in DB during initialization.")
            raise HTTPException(status_code=500, detail="Button labels not found")

        # Fetch settings from the database
        settings_stmt = select(Settings).where(Settings.id == 1)
        settings = session.exec(settings_stmt).one_or_none()
        if not settings:
            settings = Settings(id=1)
            session.add(settings)
            session.commit()
            session.refresh(settings)

        # override Settings.pulse

        settings.pulse_generator_kind = "client"
        settings.pulse_generator_ip = "10.9.0.18"

        # Apply pulse amplitude based on cryo mode
        if isinstance(cryo.pulse_controller, FunctionGeneratorPulseController):
            cryo.pulse_controller.pulse_amplitude = (
                settings.cryo_voltage
                if settings.cryo_mode
                else settings.regular_voltage
            )

        # Ensure pulse generator matches persisted settings with fallback
        pulse_info = _ensure_pulse_generator(settings, cryo, session)

        if not tree_state:
            # Should not happen if initialization logic above worked
            print("Error: Tree state not available during initialization.")
            raise HTTPException(
                status_code=500, detail="Tree state initialization failed"
            )

        # this should get filtered into InitResponsePublic
        return InitResponse(
            tree_state=tree_state,
            button_labels=labels,
            settings=settings,
            pulse_generator=pulse_info,
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


# Settings endpoints
@app.get("/settings", response_model=SettingsBase)
def get_settings(session: DBSession):
    stmt = select(Settings).where(Settings.id == 1)
    settings = session.exec(stmt).one_or_none()
    if not settings:
        settings = Settings(id=1)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


@app.post("/settings", response_model=SettingsBase)
def update_settings(
    payload: SettingsBase,
    session: DBSession,
    cryo: Annotated[CryoRelayManager, Depends(get_cryo)],
):
    print("updating settings: ", payload)
    stmt = select(Settings).where(Settings.id == 1)
    settings = session.exec(stmt).one_or_none()

    # Only include fields provided by the client (won't overwrite others)
    data = payload.model_dump(exclude_unset=True)

    if not settings:
        # Create with provided data plus fixed id
        settings = Settings(id=1, **data)
    else:
        # Update existing instance dynamically so new fields are picked up automatically
        for key, value in data.items():
            if key != "id":
                setattr(settings, key, value)

    session.add(settings)
    session.commit()
    session.refresh(settings)

    print("after: ", settings)

    # Apply to running controller
    if isinstance(cryo.pulse_controller, FunctionGeneratorPulseController):
        cryo.pulse_controller.pulse_amplitude = (
            settings.cryo_voltage if settings.cryo_mode else settings.regular_voltage
        )

    return settings


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


# auto-shutoff amps when showing the warning dialog
@app.get("/preemptive_amp_shutoff")
def preemptive_amp_shutoff(cryo: Annotated[CryoRelayManager, Depends(get_cryo)]):
    v: CryoRelayManager = cryo

    v.amp_protector.turn_off_amp()

    return v.tree.tree_state


@app.get("/cryo_mode")
def set_cryo_mode(cryo: Annotated[CryoRelayManager, Depends(get_cryo)]):
    v: CryoRelayManager = cryo
    v.pulse_controller.cryo_mode()


@app.get("/room_temp_mode")
def set_room_temp_mode(cryo: Annotated[CryoRelayManager, Depends(get_cryo)]):
    v: CryoRelayManager = cryo
    v.pulse_controller.room_temp_mode()


@app.post("/pulse_generator", response_model=PulseGenResponse)
def switch_pulse_generator(
    payload: PulseGenRequest, cryo: Annotated[CryoRelayManager, Depends(get_cryo)]
):
    """Switch the active PulseGenerator implementation at runtime.

    Body:
    { "kind": "dev" | "keysight" | "client", "ip": "10.9.0.18" }
    """

    v: CryoRelayManager = cryo
    if not isinstance(v.pulse_controller, FunctionGeneratorPulseController):
        raise HTTPException(
            status_code=400,
            detail="Active PulseController does not support external pulse generators",
        )

    try:
        # Update settings in DB and apply with fallback
        session: Session = next(get_session())
        settings = session.exec(select(Settings).where(Settings.id == 1)).one_or_none()
        if not settings:
            settings = Settings(id=1)
        settings.pulse_generator_kind = payload.kind
        settings.pulse_generator_ip = payload.ip
        session.add(settings)
        session.commit()
        session.refresh(settings)
        info = _ensure_pulse_generator(settings, v, session)
        return PulseGenResponse(ok=True, info=info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to switch generator: {e}")


def _ensure_pulse_generator(
    settings: Settings, cryo: CryoRelayManager, session: Session
) -> PulseGenInfo:
    """Ensure the FunctionGeneratorPulseController has the generator from settings.
    Fall back to dev on failure. Persist the effective kind back to settings if needed.
    """
    v = cryo
    requested_kind = (settings.pulse_generator_kind or "dev").lower()
    print(f"Requested pulse generator: {requested_kind}")
    requested_ip = settings.pulse_generator_ip
    created = True
    message = None

    if not isinstance(v.pulse_controller, FunctionGeneratorPulseController):
        return PulseGenInfo(
            requested_kind=requested_kind,
            requested_ip=requested_ip,
            active_kind="simple-relay",
            created=True,
            message="Simple relay controller in use; no external generator",
        )

    try:
        gen = make_pulse_generator(requested_kind, requested_ip)
        v.pulse_controller.set_generator(gen)
        active_kind = requested_kind
    except Exception as e:
        # Fallback
        created = False
        message = f"Falling back to dev generator: {e}"
        gen = make_pulse_generator("dev", None)
        v.pulse_controller.set_generator(gen)
        active_kind = "dev"

    # Persist the active kind in settings if it changed
    if settings.pulse_generator_kind != active_kind:
        settings.pulse_generator_kind = active_kind
        session.add(settings)
        session.commit()
        session.refresh(settings)

    return PulseGenInfo(
        requested_kind=requested_kind,
        requested_ip=requested_ip,
        active_kind=active_kind,
        created=created,
        message=message,
    )


@app.post("/switch")
def toggle_switch(
    toggle: ToggleRequest,
    cryo: Annotated[CryoRelayManager, Depends(get_cryo)],
    session: DBSession,
):
    v: CryoRelayManager = cryo

    v.amp_protector.turn_off_amp()
    v.pulse_controller.unblock_pulser(toggle.verification)

    sw = v.nodes[toggle.number - 1]
    # print("the switch to toggle: ", sw.relay_name)
    with v.lock:
        if sw.polarity:
            idx = int(sw.relay_index)
            v.pulse_controller.flip_left(idx, toggle.verification)
            sw.polarity = False

        else:
            idx = int(sw.relay_index)
            v.pulse_controller.flip_right(idx, toggle.verification)
            sw.polarity = True

    update_color(v)
    v.tree.tree_state = flatten_tree(v.top_node)

    v.amp_protector.turn_on_if_previously_on()
    v.pulse_controller.block_pulser(toggle.verification)

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

    instance.stop()
