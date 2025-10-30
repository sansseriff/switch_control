<script lang="ts">
  import { Tooltip } from "bits-ui";
  import type { Snippet } from "svelte";

  interface Props {
    label: string;
    children: Snippet;
    onclick: () => void;
  }

  let { label, children, onclick }: Props = $props();
</script>

<Tooltip.Provider>
  <Tooltip.Root delayDuration={200}>
    <Tooltip.Trigger>
      <span class="tooltip-trigger">
        <button
          type="button"
          class="icon-holder"
          {onclick}
          aria-label={label}
          title={label}
        >
          {@render children()}
        </button>
      </span>
    </Tooltip.Trigger>
    <Tooltip.Content side={"right"} sideOffset={8}>
      <div class="tooltip-bubble">{label}</div>
    </Tooltip.Content>
  </Tooltip.Root>
</Tooltip.Provider>

<style>
  /* Trigger wrapper to center the button similarly to Tailwind's inline-flex utilities */
  .tooltip-trigger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .icon-holder {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1.8rem;
    height: 1.8rem;
    border-radius: 0.375rem;
    color: rgb(127, 127, 127);
    cursor: pointer;
    margin-bottom: 0.3rem;
    background-color: transparent;
    border: none;
    padding: 0;
  }

  .icon-holder:hover {
    background-color: #ededed;
    border-radius: 0.3rem;
  }

  .icon-holder:active {
    color: #000000;
  }

  .tooltip-bubble {
    display: flex; /* replaces flex + items-center + justify-center */
    align-items: center;
    justify-content: center;
    padding: 0.75rem; /* replaces p-3 */
    font-size: 0.875rem; /* replaces text-sm */
    font-weight: 500; /* replaces font-medium */
    border-radius: 0.375rem; /* replaces rounded-input */
    background-color: #ffffff; /* replaces bg-background */
    color: #111111;
    border: 1px solid #e5e7eb; /* replaces border + border-dark-10 */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
      0 4px 6px -4px rgba(0, 0, 0, 0.1); /* replaces shadow-popover */
    outline: none; /* replaces outline-hidden */
    z-index: 10; /* ensures bubble sits above nearby content */
  }

  @media (max-width: 500px) {
    .icon-holder {
      margin-bottom: 0;
      margin-right: 0.25rem;
    }
  }
</style>
