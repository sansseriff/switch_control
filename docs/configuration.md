# Hardware configuration

All per-machine hardware settings live in a single file:

```
backend/backend/system_settings.yml
```

This file is **gitignored** — it holds values specific to one physical
instrument, so it never gets committed. A neutral template,
`system_settings.example.yml`, is tracked in the repo; copy it to get started:

```bash
cp backend/backend/system_settings.example.yml backend/backend/system_settings.yml
```

The backend reads this file once at startup (`main.lifespan`) and uses it to
decide whether hardware is active and which pulse generator to drive.

## Settings reference

```yaml
# Master switch: when false, all hardware actions (relays, pulses, amp) are
# no-ops. Keep false on any machine without the physical hardware attached.
enabled: true

# true  -> FunctionGeneratorPulseController (a function generator drives pulses)
# false -> SimpleRelayPulseController
function_gen: true

# Which pulse generator this instrument uses (see table below).
pulse_generator_kind: teledyne-client
pulse_generator_ip: 10.9.0.19

# Sleep between relay operations, in seconds. Leave unset for the code
# default (0.050).
pulse_sleep_time: 1

# Legacy migration only — see the Remote access note below.
remote_access_passphrase: null
```

| Key | Meaning |
| --- | --- |
| `enabled` | Master hardware switch. `false` ⇒ every relay/pulse/amp call is a silent no-op (safe dev mode). Must be `true` on the real instrument. |
| `function_gen` | `true` selects `FunctionGeneratorPulseController`; `false` selects `SimpleRelayPulseController`. |
| `pulse_generator_kind` | Which pulse generator backend to activate at startup. |
| `pulse_generator_ip` | IP for the direct-VISA backends. Ignored by the `*-client` kinds (they talk to the socket server). |
| `pulse_sleep_time` | Optional. Overrides the controller's inter-operation sleep. Unset ⇒ `0.050`. |
| `remote_access_passphrase` | Legacy migration only. |

!!! info "Precedence"
    When `pulse_generator_kind` is set in the yaml, it **overrides** the value
    persisted in the database at startup — so a fresh install boots straight
    onto this machine's hardware. Committed code defaults stay machine-neutral
    (`dev`).

## Pulse generator kinds

| `kind` | Backend | Connection |
| --- | --- | --- |
| `dev` | `DevModePulseGenerator` | None — prints mock actions. Default. |
| `keysight` | `KeysightPulseGenerator` | Direct VISA to a Keysight 33622A at `pulse_generator_ip`. |
| `client` | `ClientKeysightPulseGenerator` | Socket server on `localhost:8888`. |
| `teledyne` | `TeledynePulseGenerator` | Direct VISA to a Teledyne T3AFG200 at `pulse_generator_ip`. |
| `teledyne-client` | `ClientTeledynePulseGenerator` | Socket server on `localhost:8888`. |

The two `*-client` kinds both speak the same JSON-RPC method names to the
**same** `lab_remote_terminal_control` socket server on `localhost:8888`. The
server picks the physical instrument via its own `--keysight` / `--teledyne`
flag, so on the client side the kind is mostly a label for the operator.

## This lab's setup (Teledyne T3AFG200)

This instrument drives a Teledyne T3AFG200 arbitrary waveform generator over
the shared socket server, so its `system_settings.yml` uses:

```yaml
enabled: true
function_gen: true
pulse_generator_kind: teledyne-client
pulse_generator_ip: 10.9.0.19
pulse_sleep_time: 1
```

!!! warning "Start the socket server first"
    The `teledyne-client` (and `client`) kinds connect to a separate
    `lab_remote_terminal_control` server on `localhost:8888`. Make sure that
    server is running **in `--teledyne` mode** before launching the app,
    otherwise the pulse generator will fail to connect and the backend falls
    back to the `dev` generator.

At startup you should see `Requested pulse generator: teledyne-client` in the
backend log. If a generator fails to initialize, the backend logs the error
and falls back to `dev` rather than crashing.

## Other hardware

These are the same across machines and generally need no configuration:

- **Relay board:** an 8-channel numato USB relay board on `/dev/ttyACM0`.
- **Amp protector:** guards the amplifier power supply; it uses a client
  (socket) connection so multiple Python processes can share the VISA device.
