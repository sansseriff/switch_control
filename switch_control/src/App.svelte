<script lang="ts">
  import svelteLogo from "./assets/svelte.svg";
  import viteLogo from "/vite.svg";
  import Counter from "./lib/Counter.svelte";
  // import { invoke } from "@tauri-apps/api";
  import GeneralButton from "./lib/GeneralButton.svelte";

  import TreeDiagram from "./lib/TreeDiagram.svelte";
  

  import type { ButtonState, TreeState } from "./types";
  import { onMount } from "svelte";
  import Menu from "./lib/Menu.svelte";

  import { tree } from "./state.svelte";
  import TreeAndButtons from "./lib/TreeAndButtons.svelte";
  import { reAssert } from "./api";
  

</script>



<main>


  <div class="left">
    <GeneralButton onclick={() => tree.reAssertTree()}>
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
    
    margin: 1rem;
  }

  .left {
    /* width: 50%; */
    background-color: white;
    border-radius: 8px;
    padding-top: 1rem;
    padding-bottom: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    width: 100%;
    /* margin-left: 2rem; */
    margin-right: 1rem;
    border: 1px solid rgb(237, 237, 237);
  }


  
</style>
