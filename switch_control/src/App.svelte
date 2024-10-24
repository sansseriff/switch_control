<script lang="ts">
  import svelteLogo from "./assets/svelte.svg";
  import viteLogo from "/vite.svg";
  import Counter from "./lib/Counter.svelte";
  // import { invoke } from "@tauri-apps/api";
  import GeneralButton from "./lib/GeneralButton.svelte";

  import TreeDiagram from "./lib/TreeDiagram.svelte";
  

  import type { ButtonState, SwitchState } from "./types";
  import { onMount } from "svelte";
  import Menu from "./lib/Menu.svelte";

  import { tree } from "./state.svelte";
  import TreeAndButtons from "./lib/TreeAndButtons.svelte";

  

</script>


<!-- <GeneralButtom onclick={() => resetTree()}>Set Labels</GeneralButtom> -->
<main>
  <!-- <div class="left-bar">
    <Menu onclick={() => console.log("dsfsd")}></Menu>
  </div> -->

  <div class="left">
    
    <GeneralButton onclick={() => console.log("clicked")}>
      Re-Assert
    </GeneralButton>

    <GeneralButton onclick={() => tree.resetTree()}>Reset</GeneralButton>
  </div>

  <TreeAndButtons></TreeAndButtons>
</main>

<style>

  .left-bar {
    display: flex;
    flex-direction: column;
    /* justify-content: center; */
    align-items: center;
    padding-top: 0.5rem;
    padding: 0.5rem;
    padding-bottom: 1rem;
    background-color: rgb(228, 228, 228);
  }
  

  

  main {
    display: flex;
    flex-direction: row;
    padding: 0;
    margin: 0;
    background-color: rgb(248, 248, 248);
  }

  .left {
    /* width: 50%; */
    padding-top: 1rem;
    padding-bottom: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    width: 40%;
  }

  /* .right {
    display: flex;
    flex-direction: row;
    justify-content: left;
    padding-top: 0.1rem;
  } */

  
</style>
