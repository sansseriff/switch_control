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
  import { reAssert, initialize } from "./api";

  let isLoading = $state(true);

  // onMount(async () => {
  //   try {
  //     await initialize();
  //     isLoading = false;
  //   } catch (error) {
  //     console.error('Error:', error);
  //   }
  // });

  onMount(async () => {
    try {
      // this delay is needed for the webview to gain certain
      // features that let it be identified as a webview in 
      // api.ts
      await new Promise(resolve => setTimeout(resolve, 100));
      await initialize();
      isLoading = false;
    } catch (error) {
      console.error('Error:', error);
    }
  });
</script>

<main>
  {#if isLoading}
    <div class="loading-screen">
      <p>Loading...</p>
    </div>
  {:else}
  <div class="left">
    <GeneralButton
      onclick={() => tree.reAssertTree()}
      info="Re-send pulses for current configuration">Re-Assert</GeneralButton
    >

    <GeneralButton
      info="Reset all switches to default position"
      onclick={() => tree.resetTree()}>Reset</GeneralButton
    >
  </div>

  <TreeAndButtons></TreeAndButtons>

  {/if}
</main>

<style>

  .loading-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
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
