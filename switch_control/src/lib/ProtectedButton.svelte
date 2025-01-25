<script lang="ts">
  import type { Snippet } from "svelte";
  import { createTooltip, melt } from "@melt-ui/svelte";
  import type { CreateTooltipProps } from "@melt-ui/svelte";
  import { fade } from "svelte/transition";
  import type { Verification } from "../types";
  import { createDialog } from "@melt-ui/svelte";
  import { flyAndScale } from "../flyAndScale";
  import X from "phosphor-svelte/lib/X";
  import GeneralButton from "./GeneralButton.svelte";
  import { fromStore } from "svelte/store";

  interface Props {
    onVerifiedClick: (verification: Verification) => void;
    children: Snippet;
    width_rem?: number;
    highlighted?: boolean;
    info?: string;
  }

  let {
    onVerifiedClick,
    children,
    width_rem = 6.5,
    highlighted = false,
    info = "",
  }: Props = $props();

  // this is so much code just to deactivate the tooltip
  // https://www.melt-ui.com/docs/controlled
  const handleOpen: CreateTooltipProps["onOpenChange"] = ({ curr, next }) => {
    if (!info) {
      return curr;
    }
    return next;
  };

  let {
    elements: {
      trigger: trigger_tooltip,
      content: content_tooltip,
      arrow: arrow_tooltip,
    },
    states: { open: open_tooltip },
  } = createTooltip({
    positioning: {
      placement: "bottom-start",
    },
    onOpenChange: handleOpen,
    openDelay: 500,
    closeDelay: 100,
    closeOnPointerDown: false,
    forceVisible: true,
  });

  function handleVerifiedClick() {
    const verification = {
      verified: true,
      timestamp: Date.now(),
      userConfirmed: true, // Dialog already provides confirmation
    };
    onVerifiedClick(verification);
  }

  const {
    elements: {
      trigger,
      overlay,
      content,
      title,
      description,
      close,
      portalled,
    },
    states: { open },
  } = createDialog({
    role: "alertdialog",
    forceVisible: true,
  });
</script>

<button
  class="button light"
  use:melt={$trigger_tooltip}
  use:melt={$trigger}
  class:highlighted
  style="width: {width_rem}rem"
>
  {@render children()}
</button>

{#if $open_tooltip}
  <div
    use:melt={$content_tooltip}
    transition:fade={{ duration: 100 }}
    class="info-container"
  >
    <div class="arrow" use:melt={$arrow_tooltip}></div>
    <p class="info-content">{info}</p>
  </div>
{/if}

{#if $open}
  <div use:melt={$portalled}>
    <div use:melt={$overlay} class="overlay"></div>
    <div
      class="content"
      transition:flyAndScale={{
        duration: 150,
        y: 8,
        start: 0.96,
      }}
      use:melt={$content}
    >
      <h2 use:melt={$title} class="title">Is the cryoamp turned on?</h2>
      <p use:melt={$description} class="description">
        If the cryoamp is powered, triggering the switch will damage it.
      </p>

      <div class="actions">
        <GeneralButton onclick={() => open.set(false)}>Cancel</GeneralButton>
        <GeneralButton highlighted={true} onclick={handleVerifiedClick}
          >Trigger</GeneralButton
        >
        <!-- <button use:melt={$close} class="secondary"> Cancel </button>
        <button use:melt={$close} class="primary"> Continue </button> -->
      </div>

      <button use:melt={$close} aria-label="Close" class="close">
        <X />
      </button>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    z-index: 50;

    background-color: rgba(0, 0, 0, 0.355);
  }

  .content {
    position: fixed;
    left: 50%;
    top: 50%;

    z-index: 50;

    max-height: 85vh;
    width: 90vw;
    max-width: 450px;

    transform: translate(-50%, -50%);

    border-radius: 0.375rem;

    background-color: white;

    padding: 1.5rem;

    box-shadow:
      0 10px 15px -3px rgb(0, 0, 0, 0.1),
      0 4px 6px -4px rgb(0, 0, 0, 0.05);
  }

  .title {
    margin: 0;

    font-size: 1.125rem;
    line-height: 1.75rem;
    font-weight: 500;

    color: black;
  }

  .description {
    margin-bottom: 1.25rem;
    margin-top: 0.5rem;

    line-height: 1.5;

    color: gray;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;

    margin-top: 1.5rem;
  }

  .actions button {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    height: 2rem;

    border-radius: 0.25rem;

    padding: 0 1rem;

    font-weight: 500;
    line-height: 1;
  }

  /* .actions button.secondary {
    background-color: rgb(var(--color-zinc-100) / 1);

    color: rgb(var(--color-zinc-600) / 1);
  }

  .actions button.primary {
    background-color: rgb(var(--color-magnum-100) / 1);

    color: rgb(var(--color-magnum-900) / 1);
  } */

  .close {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    position: absolute;
    right: 10px;
    top: 10px;

    appearance: none;

    height: 1.5rem;
    width: 1.5rem;

    border-radius: 9999px;

    color: gray;
  }

  .close:hover {
    background-color: lightblue;
  }

  .close:focus {
    box-shadow: 0px 0px 0px 3px rgb(0, 0, 0, 0.1);
  }

  .arrow {
    box-sizing: content-box;
    border-left: 1.5px solid #dfe2e9;
    border-top: 1.5px solid #dfe2e9;
    position: absolute;
    transform: translateY(-1.5px) translateX(1.5px) rotate(45deg) !important;
    z-index: 2;
    padding-left: 0.08rem;
    padding-top: 0.08rem;
  }

  .info-container {
    background-color: white;
    border: 1.5px solid #eceef2;
    box-shadow: 2px 2px 3px rgba(0, 0, 0, 0.04);
    padding: 0rem 0rem;
    border-radius: 0.3rem;
  }

  .info-content {
    padding: 0.5rem 0.5rem;
    margin: 0rem 0rem;
  }

  .button {
    all: unset;
    display: inline-block;
    cursor: pointer;
    appearance: none;

    box-sizing: border-box;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.25rem;

    padding-left: 0rem;
    padding-right: 0rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    height: 1.7rem;

    /* width: 6.5rem; */
    text-align: center;
    font-family: Arial, Helvetica, sans-serif;
  }

  .light {
    color: #6b7280;
    /* background-color: #f8fafb; */
    border: 1.5px solid #dfe2e9;
  }

  .light:hover {
    color: #181d25;
    background-color: #f5f6f8;
  }

  .highlighted {
    /* background-color: #eef1f7; */
    border: 2.3px solid #534deb;
    color: #534deb;
  }

  .dark {
    color: #6b7280;
    border-color: #6b7280;
    background-color: #f9fafb;
  }

  .dark:hover {
    background-color: #f3f4f6;
  }
</style>
