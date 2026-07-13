from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import html
import mimetypes
import multiprocessing
from multiprocessing.connection import Connection
from pathlib import Path
import socket
import tempfile
import threading
import time
from typing import Any

from lab_link import (
    CommandContext,
    CommandError,
    LabSync,
    LanPassphraseAuth,
    ReactiveModel,
)
import psutil
from pydantic import Field
from sqlmodel import Session, select
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import (
    FileResponse,
    HTMLResponse,
)
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from uvicorn import Config, Server
import webview
import yaml

from ampProtector import AmpProtector
from db import ButtonLabels, Settings, TreeState, create_db_and_tables, engine
from location import BASE_DIR, WEB_DIR
from models import (
    ButtonLabelsBase,
    SettingsBase,
    Tree,
)
from pulse_controller import (
    ClientKeysightPulseGenerator,
    FunctionGeneratorPulseController,
    PulseController,
    SimpleRelayPulseController,
    make_pulse_generator,
)
from verification import Verification


PULSE_TIME = 50
SLEEP_TIME = 0.030
FRAMELESS = False
SERVE_PORT = 8854


def _read_system_config() -> dict[str, Any]:
    path = Path(BASE_DIR, "system_settings.yml")
    if not path.exists():
        return {}
    with path.open() as file:
        return yaml.safe_load(file) or {}


configured_remote_passphrase = _read_system_config().get("remote_access_passphrase")
remote_access = LanPassphraseAuth(
    passphrase=str(configured_remote_passphrase) if configured_remote_passphrase else None,
    cookie_name="switch_control_session",
    allowed_origins={
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:1420",
        "http://localhost:1420",
        "tauri://localhost",
    },
)


class ReactiveSwitchState(ReactiveModel):
    pos: bool = False
    color: bool = False


class ReactiveTreeState(ReactiveModel):
    R1: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    R2: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    R3: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    R4: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    R5: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    R6: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    R7: ReactiveSwitchState = Field(default_factory=ReactiveSwitchState)
    activated_channel: int = 0


class ReactiveButtonLabels(ReactiveModel):
    label_0: str = "Ch 1"
    label_1: str = "Ch 2"
    label_2: str = "Ch 3"
    label_3: str = "Ch 4"
    label_4: str = "Ch 5"
    label_5: str = "Ch 6"
    label_6: str = "Ch 7"
    label_7: str = "Ch 8"


class ReactiveSettings(ReactiveModel):
    cryo_mode: bool = False
    cryo_voltage: float = 2.5
    regular_voltage: float = 5.0
    tree_memory_mode: bool = False
    title_label: str = "Title Here"
    pulse_generator_kind: str = "dev"
    pulse_generator_ip: str | None = None


class ReactivePulseGeneratorInfo(ReactiveModel):
    requested_kind: str | None = None
    requested_ip: str | None = None
    active_kind: str = "dev"
    created: bool = True
    message: str | None = None


class AppState(ReactiveModel):
    tree_state: ReactiveTreeState = Field(default_factory=ReactiveTreeState)
    button_labels: ReactiveButtonLabels = Field(default_factory=ReactiveButtonLabels)
    settings: ReactiveSettings = Field(default_factory=ReactiveSettings)
    pulse_generator: ReactivePulseGeneratorInfo = Field(
        default_factory=ReactivePulseGeneratorInfo
    )


sync = LabSync(auth=remote_access)
state = sync.bind_state(AppState())


class CryoRelayManager:
    """Owns hardware resources only; live application state lives in ``state``."""

    def __init__(self, enabled: bool = False, function_gen: bool = True):
        self.enabled = enabled
        self.lock = threading.Lock()
        if function_gen:
            self._pulse_controller: PulseController = FunctionGeneratorPulseController(
                generator=ClientKeysightPulseGenerator()
            )
        else:
            self._pulse_controller = SimpleRelayPulseController()
        self._amp_protector = AmpProtector(on=True, disabled=False, use_client=True)

    def cleanup(self) -> None:
        self._pulse_controller.cleanup()

    def turn_off_amp(self) -> None:
        if self.enabled:
            self._amp_protector.turn_off_amp()

    def flip_left(self, index: int, verification: Verification) -> None:
        if self.enabled:
            self._pulse_controller.flip_left(index, verification)

    def flip_right(self, index: int, verification: Verification) -> None:
        if self.enabled:
            self._pulse_controller.flip_right(index, verification)

    def unblock_pulser(self, verification: Verification) -> None:
        if self.enabled:
            self._pulse_controller.unblock_pulser(verification)

    def block_pulser(self, verification: Verification) -> None:
        if self.enabled:
            self._pulse_controller.block_pulser(verification)

    def turn_on_if_previously_on(self) -> None:
        if self.enabled:
            self._amp_protector.turn_on_if_previously_on()

    def set_pulse_amplitude(self, settings: ReactiveSettings) -> None:
        if isinstance(self._pulse_controller, FunctionGeneratorPulseController):
            self._pulse_controller.pulse_amplitude = (
                settings.cryo_voltage
                if settings.cryo_mode
                else settings.regular_voltage
            )

    def ensure_pulse_generator(
        self, kind: str, ip: str | None
    ) -> ReactivePulseGeneratorInfo:
        requested_kind = (kind or "dev").lower()
        if not isinstance(self._pulse_controller, FunctionGeneratorPulseController):
            return ReactivePulseGeneratorInfo(
                requested_kind=requested_kind,
                requested_ip=ip,
                active_kind="simple-relay",
                message="Simple relay controller in use; no external generator",
            )
        try:
            generator = make_pulse_generator(requested_kind, ip)
            self._pulse_controller.set_generator(generator)
            return ReactivePulseGeneratorInfo(
                requested_kind=requested_kind,
                requested_ip=ip,
                active_kind=requested_kind,
            )
        except Exception as exc:
            self._pulse_controller.set_generator(make_pulse_generator("dev", None))
            return ReactivePulseGeneratorInfo(
                requested_kind=requested_kind,
                requested_ip=ip,
                active_kind="dev",
                created=False,
                message=f"Falling back to dev generator: {exc}",
            )


services: CryoRelayManager | None = None
hardware_command_lock = asyncio.Lock()


def cryo_manager() -> CryoRelayManager:
    if services is None:
        raise RuntimeError("hardware services have not started")
    return services


# The fixed relay topology is represented below as ``(left, right)`` children:
#
#           ___  R1 ____
#         /              \
#       R2                R3
#    /      \          /      \
#   R4       R5       R6       R7
#  /  \     /  \     /  \     /  \
# 7    6   5    4   3    2   1    0   relay-board channel
# 8    7   6    5   4    3   2    1   user-facing channel
#
# Each relay's position lives in the reactive AppState. ``pos=True`` follows
# the left child and ``pos=False`` follows the right child. Traversal begins at
# R1 and ends at an integer leaf; that leaf becomes ``activated_channel``.
TREE_CHILDREN: dict[str, tuple[str | int, str | int]] = {
    "R1": ("R2", "R3"),
    "R2": ("R4", "R5"),
    "R3": ("R6", "R7"),
    "R4": (7, 6),
    "R5": (5, 4),
    "R6": (3, 2),
    "R7": (1, 0),
}


def _relay(name: str) -> ReactiveSwitchState:
    return getattr(state.tree_state, name)


def _active_path() -> tuple[list[str], int]:
    current: str | int = "R1"
    path: list[str] = []
    while isinstance(current, str):
        path.append(current)
        left, right = TREE_CHILDREN[current]
        current = left if _relay(current).pos else right
    return path, current


def _refresh_derived_tree_state() -> None:
    path, channel = _active_path()
    active = set(path)
    for relay_name in TREE_CHILDREN:
        _relay(relay_name).color = relay_name in active
    state.tree_state.activated_channel = channel


def _verification(data: dict[str, Any]) -> Verification:
    return Verification.model_validate(data)


def _tree_from_persisted(tree: Tree) -> ReactiveTreeState:
    return ReactiveTreeState.model_validate(tree.model_dump())


def _tree_for_database() -> Tree:
    return Tree.model_validate(state.tree_state.model_dump(mode="json"))


def _persist_tree() -> None:
    with Session(engine) as session:
        row = session.exec(select(TreeState).where(TreeState.id == 1)).one_or_none()
        if row is None:
            row = TreeState(id=1)
        row.tree_json = _tree_for_database().model_dump_json()
        session.add(row)
        session.commit()


def _persist_settings() -> None:
    with Session(engine) as session:
        row = session.exec(select(Settings).where(Settings.id == 1)).one_or_none()
        data = state.settings.model_dump(mode="json")
        if row is None:
            row = Settings(id=1, **data)
        else:
            for key, value in data.items():
                setattr(row, key, value)
        session.add(row)
        session.commit()


def _persist_labels() -> None:
    with Session(engine) as session:
        row = session.exec(
            select(ButtonLabels).where(ButtonLabels.id == 1)
        ).one_or_none()
        data = state.button_labels.model_dump(mode="json")
        if row is None:
            row = ButtonLabels(id=1, **data)
        else:
            for key, value in data.items():
                setattr(row, key, value)
        session.add(row)
        session.commit()


async def _prepare_switching(verification: Verification) -> None:
    manager = cryo_manager()
    await asyncio.to_thread(manager.turn_off_amp)
    await asyncio.to_thread(manager.unblock_pulser, verification)


async def _finish_switching(verification: Verification) -> None:
    manager = cryo_manager()
    await asyncio.to_thread(manager.turn_on_if_previously_on)
    await asyncio.to_thread(manager.block_pulser, verification)


@asynccontextmanager
async def _switching(verification: Verification):
    async with hardware_command_lock:
        await _prepare_switching(verification)
        try:
            yield cryo_manager()
        finally:
            await _finish_switching(verification)


@sync.command
async def reset_tree(ctx: CommandContext, verification: dict[str, Any]) -> None:
    verified = _verification(verification)
    async with _switching(verified) as manager:
        for index in range(1, 8):
            await asyncio.to_thread(manager.flip_left, index, verified)
        with sync.batch():
            for relay_name in TREE_CHILDREN:
                _relay(relay_name).pos = False
            _refresh_derived_tree_state()
        await asyncio.to_thread(_persist_tree)


@sync.command
async def re_assert_tree(ctx: CommandContext, verification: dict[str, Any]) -> None:
    verified = _verification(verification)
    path, _ = _active_path()
    async with _switching(verified) as manager:
        for relay_name in path:
            relay_index = int(relay_name[1:])
            pulse = manager.flip_right if _relay(relay_name).pos else manager.flip_left
            await asyncio.to_thread(pulse, relay_index, verified)


@sync.command
async def request_channel(
    ctx: CommandContext, number: int, verification: dict[str, Any]
) -> None:
    if number < 0 or number > 7:
        raise CommandError(
            code="invalid_channel",
            message="Channel must be between 0 and 7.",
            path="/tree_state/activated_channel",
        )
    verified = _verification(verification)
    binary = bin(7 - number)[2:].zfill(3)
    current: str | int = "R1"
    async with _switching(verified) as manager:
        for bit in binary:
            if not isinstance(current, str):
                raise RuntimeError("relay path ended before the requested channel")
            desired_position = bit == "0"
            relay = _relay(current)
            should_pulse = (
                relay.pos != desired_position or not state.settings.tree_memory_mode
            )
            if should_pulse:
                await asyncio.sleep(SLEEP_TIME)
                pulse = manager.flip_right if desired_position else manager.flip_left
                await asyncio.to_thread(pulse, int(current[1:]), verified)
            relay.pos = desired_position
            _refresh_derived_tree_state()
            left, right = TREE_CHILDREN[current]
            current = left if relay.pos else right
        await asyncio.to_thread(_persist_tree)


@sync.command
async def toggle_switch(
    ctx: CommandContext, number: int, verification: dict[str, Any]
) -> None:
    if number < 1 or number > 7:
        raise CommandError(
            code="invalid_relay", message="Relay must be between 1 and 7."
        )
    verified = _verification(verification)
    relay = _relay(f"R{number}")
    async with _switching(verified) as manager:
        pulse = manager.flip_left if relay.pos else manager.flip_right
        await asyncio.to_thread(pulse, number, verified)
        with sync.batch():
            relay.pos = not relay.pos
            _refresh_derived_tree_state()
        await asyncio.to_thread(_persist_tree)


@sync.command
async def preemptive_amp_shutoff(ctx: CommandContext) -> None:
    async with hardware_command_lock:
        await asyncio.to_thread(cryo_manager().turn_off_amp)


@sync.command
def get_server_info(ctx: CommandContext) -> dict[str, Any]:
    """Return every non-loopback IPv4 address that can serve the remote UI."""
    ipaddrs: list[str] = []
    for addresses in psutil.net_if_addrs().values():
        for address in addresses:
            if (
                address.family == socket.AF_INET
                and not address.address.startswith("127.")
                and address.address != "0.0.0.0"
                and address.address not in ipaddrs
            ):
                ipaddrs.append(address.address)

    if not ipaddrs:
        ipaddrs = ["127.0.0.1"]

    invite = remote_access.create_invite()
    return {
        "hostname": socket.gethostname(),
        "ipaddr": ipaddrs[0],
        "ipaddrs": ipaddrs,
        "port": SERVE_PORT,
        "passphrase": remote_access.passphrase,
        "invite": invite.token,
        "invite_expires_at": invite.expires_at.isoformat(),
    }


@sync.command
async def update_settings(ctx: CommandContext, settings: dict[str, Any]) -> None:
    validated = SettingsBase.model_validate(settings)
    with sync.batch():
        for key, value in validated.model_dump(mode="json").items():
            setattr(state.settings, key, value)
    async with hardware_command_lock:
        await asyncio.to_thread(cryo_manager().set_pulse_amplitude, state.settings)
    await asyncio.to_thread(_persist_settings)


@sync.command
async def update_configuration(
    ctx: CommandContext, labels: dict[str, Any], title_label: str
) -> None:
    validated = ButtonLabelsBase.model_validate(labels)
    with sync.batch():
        state.button_labels = ReactiveButtonLabels.model_validate(
            validated.model_dump(mode="json")
        )
        state.settings.title_label = title_label
    await asyncio.to_thread(_persist_labels)
    await asyncio.to_thread(_persist_settings)


@sync.command
async def switch_pulse_generator(
    ctx: CommandContext, kind: str, ip: str | None = None
) -> None:
    async with hardware_command_lock:
        info = await asyncio.to_thread(cryo_manager().ensure_pulse_generator, kind, ip)
    with sync.batch():
        state.settings.pulse_generator_kind = info.active_kind
        state.settings.pulse_generator_ip = ip
        state.pulse_generator = info
    await asyncio.to_thread(_persist_settings)


def _load_persisted_state() -> dict[str, Any]:
    with Session(engine) as session:
        tree_row = session.exec(select(TreeState).where(TreeState.id == 1)).one()
        labels = session.exec(select(ButtonLabels).where(ButtonLabels.id == 1)).one()
        settings = session.exec(select(Settings).where(Settings.id == 1)).one()
        tree = Tree.model_validate_json(tree_row.tree_json)
        return {
            "tree_state": _tree_from_persisted(tree).model_dump(mode="json"),
            "button_labels": ReactiveButtonLabels.model_validate(
                labels.model_dump(exclude={"id"})
            ).model_dump(mode="json"),
            "settings": ReactiveSettings.model_validate(
                settings.model_dump(exclude={"id"})
            ).model_dump(mode="json"),
            "pulse_generator": ReactivePulseGeneratorInfo().model_dump(mode="json"),
        }


def _read_hardware_config() -> tuple[bool, bool]:
    data = _read_system_config()
    return bool(data.get("enabled", False)), bool(data.get("function_gen", True))


@asynccontextmanager
async def lifespan(app: Starlette):
    global services
    print("Creating database and loading authoritative state...")
    create_db_and_tables()
    sync.load_state(_load_persisted_state())
    enabled, function_gen = _read_hardware_config()
    services = await asyncio.to_thread(CryoRelayManager, enabled, function_gen)
    try:
        pulse_info = await asyncio.to_thread(
            services.ensure_pulse_generator,
            state.settings.pulse_generator_kind,
            state.settings.pulse_generator_ip,
        )
        state.pulse_generator = pulse_info
        state.settings.pulse_generator_kind = pulse_info.active_kind
        await asyncio.to_thread(services.set_pulse_amplitude, state.settings)
        await asyncio.to_thread(_persist_settings)
        _refresh_derived_tree_state()
        async with sync.lifespan(app):
            yield
    finally:
        if services is not None:
            await asyncio.to_thread(services.cleanup)
        services = None


mimetypes.init()


def _login_page(error: str = "") -> HTMLResponse:
    error_markup = (
        f'<p class="error" role="alert">{html.escape(error)}</p>' if error else ""
    )
    document = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Switch Control — Remote Access</title>
  <style>
    :root { font-family: Arial, Helvetica, sans-serif; color: #18181b; background: #fbfbfb; }
    body { min-height: 100vh; margin: 0; display: grid; place-items: center; padding: 1rem; box-sizing: border-box; }
    main { width: min(100%, 22rem); background: white; border: 1px solid #e5e7eb; border-radius: .55rem; box-shadow: 0 10px 30px rgba(0,0,0,.08); padding: 1.25rem; }
    h1 { margin: 0 0 .45rem; font-size: 1.2rem; }
    p { color: #6b7280; font-size: .86rem; line-height: 1.4; }
    label { display: block; margin: 1rem 0 .35rem; font-size: .82rem; font-weight: 600; }
    input { box-sizing: border-box; width: 100%; padding: .62rem .7rem; border: 1.5px solid #dfe2e9; border-radius: .3rem; font: inherit; letter-spacing: .04em; }
    button { width: 100%; margin-top: .7rem; padding: .62rem; border: 1.5px solid #534deb; border-radius: .3rem; background: #534deb; color: white; font: inherit; cursor: pointer; }
    .error { color: #b42318; background: #fff1f0; border-radius: .3rem; padding: .5rem .6rem; }
    .note { margin-bottom: 0; font-size: .75rem; }
  </style>
</head>
<body>
  <main>
    <h1>Switch Control</h1>
    <p>Enter the remote-access passphrase shown on the host computer.</p>
    __ERROR__
    <form id="login" action="/sync/auth/login" method="post">
      <label for="passphrase">Access passphrase</label>
      <input id="passphrase" name="passphrase" type="password" autocomplete="current-password" required autofocus />
      <button type="submit">Open Switch Control</button>
    </form>
    <p class="note">Use only on a trusted network. This local HTTP connection is not encrypted.</p>
  </main>
  <script>
    const form = document.getElementById("login");
    const error = document.querySelector(".error") || document.createElement("p");
    error.className = "error";
    error.setAttribute("role", "alert");

    function message(code) {
      if (code === "invalid_credentials") return "That passphrase was not accepted.";
      if (code === "invalid_or_expired_invite") return "This access link has expired or has already been used.";
      if (code === "rate_limited") return "Too many attempts. Wait one minute and try again.";
      return "Remote access could not be authenticated.";
    }

    async function authenticate(path, body) {
      const response = await fetch(path, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(message(result.error));
      location.replace(location.pathname);
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      authenticate("/sync/auth/login", {
        passphrase: document.getElementById("passphrase").value,
      }).catch((cause) => {
        error.textContent = cause.message;
        form.before(error);
      });
    });

    const invite = new URLSearchParams(location.hash.slice(1)).get("invite");
    if (invite) {
      history.replaceState(null, "", location.pathname + location.search);
      authenticate("/sync/auth/invite", { invite }).catch((cause) => {
        error.textContent = cause.message;
        form.before(error);
      });
    }
  </script>
</body>
</html>""".replace("__ERROR__", error_markup)
    return HTMLResponse(
        document,
        headers={
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
            "Referrer-Policy": "no-referrer",
        },
    )


async def return_index(request: Request):
    mimetypes.add_type("application/javascript", ".js")
    if not remote_access.is_http_authorized(request):
        return _login_page()
    return FileResponse(Path(WEB_DIR, "index.html"))


routes = [*sync.routes]
web_path = Path(WEB_DIR)
if web_path.exists():
    routes.extend(
        [
            Mount("/assets", StaticFiles(directory=web_path / "assets"), name="assets"),
            Route("/", return_index),
        ]
    )

app = Starlette(routes=routes, lifespan=lifespan)


def start_window(pipe_send: Connection, url_to_load: str, debug: bool = False) -> None:
    time.sleep(0.3)

    def on_closed() -> None:
        pipe_send.send("closed")

    window = webview.create_window(
        "Switch Control",
        url=url_to_load,
        resizable=True,
        width=800,
        height=430,
        frameless=FRAMELESS,
        easy_drag=False,
    )
    window.events.closed += on_closed
    webview.start(storage_path=tempfile.mkdtemp(), debug=debug)


class UvicornServer(multiprocessing.Process):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)

    def stop(self) -> None:
        self.terminate()

    def run(self) -> None:
        self.server.run()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Switch Control Backend")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    server_port = SERVE_PORT
    conn_recv, conn_send = multiprocessing.Pipe()
    server = UvicornServer(
        Config(
            "main:app",
            host="0.0.0.0",
            port=server_port,
            log_level="debug" if args.debug else None,
            workers=1,
        )
    )
    server.start()
    window_process = multiprocessing.Process(
        target=start_window,
        args=(conn_send, f"http://localhost:{server_port}/", args.debug),
    )
    window_process.start()
    window_status = ""
    while "closed" not in window_status:
        window_status = conn_recv.recv()
    server.stop()
