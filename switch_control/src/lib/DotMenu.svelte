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
    width= "0.9rem"
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
  }

  


  .item {
    font-family: Arial, Helvetica, sans-serif;
    background-color: white;
    border-radius: 5px;
    margin: 0.1rem;
    padding: 0.5rem;
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
    padding-top: 0.24rem;
    padding-left: 0.45rem;
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
