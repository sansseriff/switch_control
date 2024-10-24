<script lang="ts">
    import { createDropdownMenu, melt } from '@melt-ui/svelte'
    import GeneralButton from './GeneralButton.svelte';
    const {
      elements: { menu, item, trigger, arrow }
    } = createDropdownMenu()



    interface MyProps {
        onclick: () => void;
    }
    let { onclick }: MyProps = $props();


    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter" || event.key === " ") {
            console.log("onclick: ", onclick)
            onclick();
        }
    }
  </script>
  

  <div class="hamburger" use:melt={$trigger} onclick={onclick} onkeydown={handleKeyDown} role="button" tabindex="0">
    <svg
        class="h-5.5 w-6 my-1 mr-1"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.2"
    >
        <path d="M3 12h18M3 6h18M3 18h18" />
    </svg>
</div>
  <div use:melt={$menu}>
    <div use:melt={$item}>Option 1</div>
    <div use:melt={$item}>Option 2</div>
    <div use:melt={$item}>Option 3</div>
    <div use:melt={$arrow} />
  </div>


  <style>
    .hamburger {
        width: 1.7rem;
        height: 1.7rem;
        /* display: flex; */
        border: 1px solid rgba(0, 0, 0, 0.075);
        
        border-radius: 3px;
        padding-top: 2px;
        padding-bottom: 2px;
        padding-left: 4px;
        padding-right: 4px;
        color: var(--text-color);

    }

    .hamburger:hover {
        cursor: pointer;
        background-color: rgba(0, 0, 0, 0.075);
    }
</style>