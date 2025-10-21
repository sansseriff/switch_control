<script lang="ts">
  import { Dialog } from "bits-ui";
  import X from "phosphor-svelte/lib/X";
  import GeneralButton from "./GeneralButton.svelte";
  import { tree } from "../tree_state.svelte";
  // base dialog styles
  import "../dialog.css";

  interface Props {
    isOpen: any;
  }

  let { isOpen = $bindable() }: Props = $props();

  function chooseMode(cryo: boolean) {
    tree.cryo_mode = cryo;
    tree.saveSettings();
    isOpen = false;
  }

  const cryoLabel = $derived(
    tree.cryo_mode ? "Stay in Cryo Mode" : "Enter Cryo Mode",
  );
  const roomLabel = $derived(
    tree.cryo_mode ? "Enter Room Temp Mode" : "Stay in Room Temp Mode",
  );
</script>

<Dialog.Root bind:open={isOpen}>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Would you like to update the temperature mode?</Dialog.Title
      >
      <Dialog.Description>
        Choose the temperature mode you want the system to use.
      </Dialog.Description>

      <div class="buttons">
        <GeneralButton onclick={() => chooseMode(true)} width_rem={12}
          >{cryoLabel}</GeneralButton
        >
        <div style="width: 8px;"></div>
        <GeneralButton onclick={() => chooseMode(false)} width_rem={12}
          >{roomLabel}</GeneralButton
        >
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
  .buttons {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.8rem;
  }
  .buttons :global(.button) {
    white-space: nowrap;
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
</style>
