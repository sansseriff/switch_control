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
    <Dialog.Overlay class="bg-white" />
    <Dialog.Content
      class="rounded-md bg-background shadow-popover data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 outline-hidden fixed left-[50%] top-[50%] z-50 w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] border p-4 sm:max-w-[490px] md:w-full"
    >
      <Dialog.Title
        class="flex w-full items-center justify-left text-lg font-semibold tracking-tight"
      >
        Is the cryoamp turned on?
      </Dialog.Title>
      <Separator.Root class="bg-muted -mx-5 mb-3 mt-3 block h-px" />
      <Dialog.Description class="text-foreground-alt text-sm mb-4">
        If the cryoamp is powered, triggering the switch will damage it.
      </Dialog.Description>
      <!-- <div class="flex flex-col items-start gap-1 pb-11 pt-7"></div> -->
      <div class="flex w-full justify-end">
        <div class="spacer mx-3">
          <GeneralButton
            onclick={() => {
              isOpen = false;
            }}>Cancel</GeneralButton
          >
        </div>
        <div class="spacer mx-3">
          <GeneralButton danger={true} onclick={handleVerifiedClick}
            >Trigger</GeneralButton
          >
        </div>
      </div>
      <Dialog.Close
        class="focus-visible:ring-foreground focus-visible:ring-offset-background focus-visible:outline-hidden absolute right-5 top-5 rounded-md focus-visible:ring-2 focus-visible:ring-offset-2 active:scale-[0.98]"
      >
        <div>
          <X class="text-foreground size-5" />
          <span class="sr-only">Close</span>
        </div>
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
