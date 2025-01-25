<script lang="ts">
  import type { Snippet } from "svelte";
  import { createTooltip, melt } from "@melt-ui/svelte";
  import type { CreateTooltipProps } from "@melt-ui/svelte";
  import { fade } from "svelte/transition";

  interface Props {
    onclick: (event: MouseEvent) => void;
    children: Snippet;
    width_rem?: number;
    highlighted?: boolean;
    danger?: boolean;
    info?: string;
  }

  let {
    onclick,
    children,
    width_rem = 6.5,
    highlighted = false,
    danger = false,
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
    elements: { trigger, content, arrow },
    states: { open },
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
</script>

<button
  class="button light"
  use:melt={$trigger}
  class:highlighted
  class:danger
  {onclick}
  style="width: {width_rem}rem"
>
  {@render children()}
</button>

{#if $open}
  <div
    use:melt={$content}
    transition:fade={{ duration: 100 }}
    class="info-container"
  >
    <div class="arrow" use:melt={$arrow}></div>
    <p class="info-content">{info}</p>
  </div>
{/if}

<style>
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
    cursor: pointer;
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
    /* color: #181d25; */
    background-color: #f5f6f8;
  }

  .highlighted {
    /* background-color: #eef1f7; */
    border: 2.3px solid #534deb;
    color: #534deb;
  }

  .danger {
    border: 2.3px solid #f87171;
    color: #f87171;
  }

  .danger:hover {
    background-color: #ffeded;
  }

  .highlighted:hover {
    background-color: #efeeff;
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
