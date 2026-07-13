# Switch Control

![switchui](./switch_ui.png)

A python program and webview-based user interface for controlling a cryogenic RF switch.

The python program sends serial commands to an 8 channel [numato relay board](https://numato.com/product/8-channel-usb-relay-module/). This, in turn, sends positive and negative voltage pulses to a binary tree of teledyne relays. This allows one pair of SMA inputs to be switched to 1 of 8 possible differential output pairs in a ARC6-8ch connector.

![relay_board](./teledyne_relay_board.jpg)

The Python entrypoint is `backend/backend/main.py`. It uses lab-link with a
Starlette server and an integrated `pywebview` window. The Svelte UI is built
from `/switch_control`.

The backend's `AppState` reactive model is the single live source of truth for
the relay tree, active channel, labels, settings, and pulse-generator status.
The browser receives snapshots and reactive JSON patches over lab-link's
WebSocket and sends hardware operations as lab-link commands. There are no
REST polling or server-sent-event state paths.

Remote access is protected by a startup passphrase. QR/copy URLs carry the
passphrase in the URL fragment; the login page exchanges it for a 12-hour
HttpOnly, SameSite session cookie and removes it from the address bar before
loading the UI. Plain LAN URLs show the passphrase form, and unauthenticated
WebSocket connections are rejected before lab-link sends application state.
Set `remote_access_passphrase` in `backend/backend/system_settings.yml` for a
stable passphrase, or leave it null to generate a new one on each startup.

This is a trusted-LAN convenience gate, not encrypted transport. Use HTTPS or
a private overlay network when traffic confidentiality is required.

Use `build_ui_and_run.sh` to compile the frontend user interface, copy it into the `/backend` directory, and start the python webserver using the `uv` python project manager.

Sometimes when editing the user interface, it's helpful to see changes to the code updated immediately in the UI. For this, use `dev_ui.sh`. This will run a vite dev-server, and allow you to see the UI inside a browser tab as you edit and update its code.

## Installation

Run this command to download and install on macos or linux:

```bash
curl -s https://switch.snsphd.online/dl.sh -o dl.sh && bash dl.sh
```
