<script lang="ts">
  import { createDropdownMenu, melt } from "@melt-ui/svelte";
  import GeneralButton from "./GeneralButton.svelte";

  interface Props {
    editChannelLabels: () => void;
    defaultChannelLabels: () => void;
  }
  let { editChannelLabels, defaultChannelLabels }: Props = $props();

  const {
    elements: { menu, item, trigger, arrow },
  } = createDropdownMenu({ positioning: { placement: "bottom-end" } });

  function handleClick() {}
</script>

<button
  onclick={handleClick}
  use:melt={$trigger}
  class="menu-button light"
  aria-label="dot menu"
>
  <svg
    height="0.9rem"
    width="0.9rem"
    viewBox="0 0 15 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="4.5" cy="5" r="5" fill="var(--dot-color)" />
    <circle cx="4.5" cy="21.5" r="5" fill="var(--dot-color)" />
    <circle cx="4.5" cy="38" r="5" fill="var(--dot-color)" />
  </svg>
</button>

<div class="menu" use:melt={$menu}>
  <div class="arrow" use:melt={$arrow}></div>
  <div
    class="item"
    use:melt={$item}
    role="menuitem"
    tabindex="0"
    onclick={editChannelLabels}
  >
    Edit Channel Labels
  </div>
  <div
    class="item"
    use:melt={$item}
    role="menuitem"
    tabindex="0"
    onclick={defaultChannelLabels}
  >
    Default Channel Numbers
  </div>
</div>

<style>
  .menu {
    box-sizing: border-box;
    background-color: white;
    border-radius: 4px;
    border: 1.5px solid #dfe2e9;
    position: relative; /* Ensure the menu is positioned */
    z-index: 1; /* Set a base z-index for the menu */
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

  .item {
    font-family: Arial, Helvetica, sans-serif;
    background-color: white;
    border-radius: 5px;
    margin: 0.1rem;
    padding: 0.5rem;
    position: relative; /* Ensure the items are positioned */
    z-index: 3; /* Ensure the items are above the arrow */
  }

  .item:hover {
    background-color: rgb(245, 245, 245);
    cursor: pointer;
  }

  :global(:root) {
    --dot-color: #585858; /* Default color */
  }

  .menu-button {
    box-sizing: border-box;
    background: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.7rem;
    height: 1.7rem;
    border-radius: 10%;
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

  .menu-button svg {
    display: block;
  }

  .menu-button:focus {
    outline: none;
  }

  /* svg: {
    padding-top: 0.1rem;
  } */
</style>
