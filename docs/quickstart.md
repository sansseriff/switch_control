# Quickstart

This guide takes you from a fresh checkout to a running Switch Control app.

## Prerequisites

- **Linux or macOS** (the app opens a native [pywebview] window).
- **git**.
- Everything else — [uv] (Python 3.13 toolchain) and [Bun] (web assets) — is
  installed automatically by `setup.sh` if it isn't already present.

!!! note "Hardware is optional for a first run"
    The app runs without any instruments attached. With hardware disabled it
    starts in a safe **no-op / dev** mode — the UI works, but relay and pulse
    actions do nothing. See [Hardware configuration](configuration.md) to turn
    real hardware on.

## 1. Get the code

```bash
git clone https://github.com/sansseriff/switch_control.git
cd switch_control
```

## 2. Run the setup script

```bash
bash setup.sh
```

Choose **1** when prompted to let [uv] manage a local, portable Python 3.13
environment. The script:

1. Installs `uv` if needed, then creates `backend/.venv` and runs `uv sync` to
   install the Python dependencies from `backend/pyproject.toml`.
2. Installs [Bun] if needed, then runs `bun install` and `bun run buildall` in
   `switch_control/` to compile the Svelte UI and copy it into the backend.

Prefer to manage Python yourself? Choose **2** and install the
`backend/pyproject.toml` dependencies into your own Python 3.13+ environment.

## 3. Configure hardware (optional)

Each machine carries its own **untracked** `system_settings.yml`. Copy the
template and edit it for the instrument this computer controls:

```bash
cp backend/backend/system_settings.example.yml backend/backend/system_settings.yml
```

To actually drive hardware you'll set `enabled: true` and pick a
`pulse_generator_kind`. Full details — including this lab's Teledyne T3AFG200
setup — are on the [Hardware configuration](configuration.md) page.

## 4. Run the app

From the repo root:

```bash
cd switch_control
sh run.sh
```

`run.sh` launches the backend with uv: `cd ./backend/backend && uv run main.py`.
Add `--debug` to run in debug mode:

```bash
sh run.sh --debug
```

Equivalent one-liner without the script:

```bash
cd backend/backend && uv run main.py
```

### Rebuild the UI and run in one step

If you've changed the Svelte frontend and want to recompile it before starting:

```bash
sh build_ui_and_run.sh
```

This runs `bun run buildall` in `switch_control/`, then starts the backend.

## Developing the UI with live reload

Editing the frontend is much faster with a Vite dev server that hot-reloads in
a browser tab:

```bash
sh dev_ui.sh
```

This runs `SKIP_LOADING=true bun run dev` in `switch_control/`. Open the URL it
prints (typically `http://localhost:5173`) to see UI changes as you save.

## Common commands

| Task | Command |
| --- | --- |
| First-time setup | `bash setup.sh` |
| Run the app | `cd switch_control && sh run.sh` |
| Run in debug mode | `cd switch_control && sh run.sh --debug` |
| Run directly | `cd backend/backend && uv run main.py` |
| Rebuild UI, then run | `sh build_ui_and_run.sh` |
| UI live-reload dev server | `sh dev_ui.sh` |

[pywebview]: https://pywebview.flowrl.com/
[Bun]: https://bun.sh/
[uv]: https://docs.astral.sh/uv/
