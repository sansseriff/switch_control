<script lang="ts">
  import { Dialog, Label, Switch } from "bits-ui";
  import X from "phosphor-svelte/lib/X";
  import DotsThreeVertical from "phosphor-svelte/lib/DotsThreeVertical";
  import GeneralButton from "./GeneralButton.svelte";
  import { tree } from "../state.svelte";
  import { Popover } from "bits-ui";
  // base dialog styles
  import "../dialog.css";

  interface Props {
    isOpen: any;
  }

  let { isOpen = $bindable() }: Props = $props();

  const ids = {
    cryo: "cryo-mode-toggle",
    memory: "tree-memory-toggle",
  } as const;

  // local mirrors for toggle binding (Svelte 5 recommends not binding to member expressions)
  //   let cryo = $state(tree.cryo_mode);
  //   let memory = $state(tree.tree_memory_mode);
  console.log("tree.cryo_mode ", tree.cryo_mode);
  console.log("tree.cryo_voltage ", tree.cryo_voltage);
  console.log("tree.regular_voltage ", tree.regular_voltage);

  let cryo = $state(true);
  let memory = $state(false);
  let cryoVoltage = $state(0);
  let regularVoltage = $state(0);

  // Initialize local copies only when the dialog opens.
  // This avoids mutating global state unless the user clicks Save.
  let wasOpen = false;
  $effect(() => {
    if (isOpen && !wasOpen) {
      cryo = $state.snapshot(tree.cryo_mode);
      memory = $state.snapshot(tree.tree_memory_mode);
      cryoVoltage = $state.snapshot(tree.cryo_voltage);
      regularVoltage = $state.snapshot(tree.regular_voltage);

      console.log("MenuDialog opened; copied settings");
      console.log("cryo: ", cryo);
      console.log("memory: ", memory);
      console.log("cryoVoltage: ", cryoVoltage);
      console.log("regularVoltage: ", regularVoltage);
    }
    wasOpen = isOpen;
  });

  function applyAndClose() {
    tree.cryo_mode = cryo;
    tree.tree_memory_mode = memory;
    tree.cryo_voltage = Number(cryoVoltage);
    tree.regular_voltage = Number(regularVoltage);
    // persist to backend
    tree.saveSettings();
    isOpen = false;
  }
</script>

<Dialog.Root bind:open={isOpen}>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Settings</Dialog.Title>
      <Dialog.Description>Configure runtime options.</Dialog.Description>

      <div class="rows">
        <!-- Cryo row with settings popover -->
        <div class="row">
          <div class="switch-row">
            <div class="left">
              <Switch.Root
                id={ids.cryo}
                name="cryo-mode"
                bind:checked={cryo}
                class="switch-root"
                aria-labelledby="cryo-label"
              >
                <Switch.Thumb class="switch-thumb" />
              </Switch.Root>
              <div class="text">
                <Label.Root id="cryo-label" for={ids.cryo} class="label"
                  >Cryo mode</Label.Root
                >
                <div class="hint">
                  Cryo mode sends less voltage to the relays
                </div>
              </div>
            </div>
            <div class="right">
              <Popover.Root>
                <Popover.Trigger>
                  <button
                    type="button"
                    class="icon-button"
                    aria-label="Set voltages"
                  >
                    <DotsThreeVertical size={25} weight="bold" />
                  </button>
                </Popover.Trigger>
                <Popover.Portal>
                  <Popover.Content sideOffset={8} class="popover-card">
                    <div class="popover-title">Pulse Voltage</div>
                    <div class="field">
                      <label for="cryo-voltage">Cryo voltage</label>
                      <input
                        id="cryo-voltage"
                        type="number"
                        step="0.01"
                        min="0"
                        max="10"
                        bind:value={cryoVoltage}
                      />
                    </div>
                    <div class="field">
                      <label for="regular-voltage">Room temp. voltage</label>
                      <input
                        id="regular-voltage"
                        type="number"
                        step="0.01"
                        min="0"
                        max="10"
                        bind:value={regularVoltage}
                      />
                    </div>
                  </Popover.Content>
                </Popover.Portal>
              </Popover.Root>
            </div>
          </div>
        </div>

        <!-- Tree-memory row -->
        <div class="row">
          <div class="switch-group">
            <Switch.Root
              id={ids.memory}
              name="tree-memory-mode"
              bind:checked={memory}
              class="switch-root"
              aria-labelledby="memory-label"
            >
              <Switch.Thumb class="switch-thumb" />
            </Switch.Root>
            <div class="text">
              <Label.Root id="memory-label" for={ids.memory} class="label"
                >Tree-memory mode</Label.Root
              >
              <div class="hint">
                Don't send pulses to relays already in the required state
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="buttons">
        <GeneralButton onclick={() => (isOpen = false)}>Cancel</GeneralButton>
        <div style="width: 8px;"></div>
        <GeneralButton onclick={applyAndClose}>Save</GeneralButton>
      </div>

      <Dialog.Close>
        <div class="close-icon">
          <X />
          <span class="sr-only">Close</span>
        </div>
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<style>
  .rows {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.25rem;
    margin-bottom: 0.25rem;
  }
  .row {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.25rem 0;
  }
  .row + .row {
    border-top: 1px solid var(--muted, #e5e7eb);
    padding-top: 0.5rem;
  }
  .switch-group {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
  }
  .switch-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
  }
  .left {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
  }
  .right {
    display: flex;
    align-items: center;
  }
  .text {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }
  :global(.label) {
    font-size: 0.95rem;
    font-weight: 600;
  }
  .hint {
    font-size: 0.8rem;
    color: #6b7280; /* gray-500 */
    padding-left: 0.05rem;
  }

  /* Switch styles (no Tailwind) */
  :global(.switch-root) {
    position: relative;
    display: inline-flex;
    align-items: center;
    width: 44px;
    min-width: 44px;
    height: 24px;
    min-height: 24px;
    padding: 2px;
    border-radius: 9999px;
    cursor: pointer;
    outline: none;
    transition:
      background-color 150ms ease,
      box-shadow 150ms ease;
    box-shadow: inset 0 0 0 0 rgba(0, 0, 0, 0.1);
    background-color: var(--switch-off-bg, #e5e7eb); /* gray-200 */
  }
  :global(.switch-root[data-state="checked"]) {
    background-color: var(--switch-on-bg, #111827); /* near black */
  }
  :global(.switch-root:focus-visible) {
    box-shadow:
      0 0 0 2px #111827,
      0 0 0 4px #ffffff;
  }
  :global(.switch-root:disabled) {
    opacity: 0.5;
    cursor: not-allowed;
  }

  :global(.switch-thumb) {
    pointer-events: none;
    display: block;
    width: 20px;
    height: 20px;
    border-radius: 9999px;
    background-color: var(--switch-thumb-bg, #ffffff);
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
    transform: translateX(0);
    transition: transform 150ms ease;
  }
  :global(.switch-root[data-state="checked"] .switch-thumb) {
    transform: translateX(19px);
    border-color: black;
  }

  .icon-button {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: white;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    cursor: pointer;
  }
  .icon-button:hover {
    background: #f3f4f6;
    color: #111827;
  }
  .icon-button :global(svg) {
    width: 18px;
    height: 18px;
  }

  :global(.popover-card) {
    background: var(--background);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px;
    box-shadow: var(--shadow-popover);
    max-width: 280px;
  }
  .popover-title {
    font-weight: 600;
    margin-bottom: 8px;
  }
  .field {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: 8px;
  }
  .field label {
    font-size: 0.9rem;
  }
  .field input {
    width: 120px;
    padding: 6px 8px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--background);
  }

  .buttons {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.8rem;
  }

  .close-icon {
    position: absolute;
    right: 0px;
    top: 0px;
    display: inline-flex;
    width: 24px;
    height: 24px;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    color: #6b7280;
  }
  /* .close-icon:hover {
    background-color: #f3f4f6; 
    color: #111827;
  } */
</style>
