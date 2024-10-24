<script lang="ts">
  import { createDropdownMenu, melt } from "@melt-ui/svelte";
  import GeneralButton from "./GeneralButton.svelte";
  const {
    elements: { menu, item, trigger, arrow },
  } = createDropdownMenu();
  // You can define any script logic here if needed
  function handleClick() {
    // Handle the click event, e.g., open a menu
    console.log("Menu button clicked");
  }
</script>

<button
  on:click={handleClick}
  use:melt={$trigger}
  class="menu-button"
  aria-label="dot menu"
>
  <svg
    height="1.0rem"
    viewBox="0 0 10 43"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="5" cy="5" r="5" fill="var(--dot-color)" />
    <circle cx="5" cy="21.5" r="5" fill="var(--dot-color)" />
    <circle cx="5" cy="38" r="5" fill="var(--dot-color)" />
  </svg>
</button>

<div class="menu" use:melt={$menu}>
    <div class="item" use:melt={$item} on:m-click={(e) => console.log('Item 1!')}>Option 1</div>
    <div class="item" use:melt={$item} on:m-click={(e) => console.log('Item 2!')}>Option 2</div>
</div>


<style>


  .menu {
    box-sizing: border-box;
    background-color: white;
    border-radius: 4px;
    border: 1px solid rgb(210, 210, 210);
    
    
  }
  .item {
    font-family:Arial, Helvetica, sans-serif;
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
    border: 1px solid rgb(244, 244, 244);
    background-color: rgb(252, 252, 252);
    border-radius: 10%;
  }

  .menu-button svg {
    display: block;
    
  }

  .menu-button:focus {
    outline: none;
  }

  .menu-button:hover {
    background-color: rgba(0, 0, 0, 0.075);
    border: 1px solid rgb(221, 221, 221);
  }
</style>
