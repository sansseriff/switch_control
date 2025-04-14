<script lang="ts">
  import type { Snippet } from "svelte";
  import { fade } from "svelte/transition";
  import type { Verification } from "../types";
  import { createDialog } from "@melt-ui/svelte";
  import { flyAndScale } from "../flyAndScale";
  import X from "phosphor-svelte/lib/X";
  import GeneralButton from "./GeneralButton.svelte";
  import { Dialog, Label, Separator } from "bits-ui";
  import { on } from "svelte/events";

  // using regular css because tailwind has limited support on older browsers
  import "../dialog.css" 

  interface Props {
    isOpen: any;
    onVerifiedClick: (v: Verification) => void;
  }

  let { isOpen = $bindable(), onVerifiedClick }: Props = $props();

  function handleVerifiedClick() {
    isOpen = false;
    const verification = {
      verified: true,
      timestamp: Date.now(),
      userConfirmed: true, // Dialog already provides confirmation
    };
    onVerifiedClick(verification);
  }
</script>

<Dialog.Root bind:open={isOpen}>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>
        Is the cryoamp turned on?
      </Dialog.Title>
      <!-- <Separator.Root /> -->
      <Dialog.Description>
        If the cryoamp is powered, triggering the switch will damage it.
      </Dialog.Description>
      <div class="button-container">
        <div class="spacer">
          <GeneralButton
            onclick={() => {
              isOpen = false;
            }}>Cancel</GeneralButton
          >
        </div>
        <div class="spacer">
          <GeneralButton danger={true} onclick={handleVerifiedClick}
            >Trigger</GeneralButton
          >
        </div>
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

