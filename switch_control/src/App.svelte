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
  import ProtectedButton from "./lib/ProtectedButton.svelte";
  // console.log("import.meta.env.SKIP_LOADING ", import.meta.env.SKIP_LOADING);
  let isLoading = $state(import.meta.env.SKIP_LOADING !== "true");

  onMount(async () => {
    // await new Promise((resolve) => setTimeout(resolve, 1));
    await tree.init();
    // even though I don't use the ouptut of tree.init(), its important that
    // that it returns a promise. Because awaiting that promise delays the
    // setting of isLoading to false. If isLoading is set to false too soon,
    // then the onMount function in contained components will trigger
    // api calls to get_tree before the tree is initialized. Causing an error.
    isLoading = false;
  });
</script>

<main>
  <!-- <div class="top-bar pywebview-drag-region"></div>
  <div class="top-bar pywebview-drag-region"></div> -->

  <div class="main-content">
    <!-- <div class="bg-red-100">Is tailwind working?</div> -->
    {#if isLoading}
      <div class="loading-screen">
        <p>Loading...</p>
      </div>
    {:else}
      <div class="left">
        <ProtectedButton
          onInitialClick={() => tree.preemptiveAmpShutoff()}
          onVerifiedClick={(v) => tree.reAssertTree(v)}
          width_rem={5.5}
        >
          ReAssert
        </ProtectedButton>
        <ProtectedButton
          onInitialClick={() => tree.preemptiveAmpShutoff()}
          onVerifiedClick={(v) => tree.resetTree(v)}
          width_rem={5.5}
        >
          Reset
        </ProtectedButton>
      </div>
      <div class="right">
        <div class="inside"><TreeAndButtons></TreeAndButtons></div>
      </div>
    {/if}
  </div>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
  }

  /* .top-bar {
    top: 0;
    left: 0;
    width: 100%;
    height: 2.7rem;
    background-color: #ffffff;
    border-bottom: 1px solid rgb(237, 237, 237);
  } */

  .loading-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }

  .main-content {
    display: flex;
    flex-direction: row;
    padding: 0;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }

  .left {
    background-color: white;
    border-radius: 8px;
    box-sizing: border-box;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    margin: 1rem;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
    border: 1px solid rgb(237, 237, 237);
    flex: 5;
  }

  .right {
    display: flex;
    /* flex-direction: column; */
    justify-content: center;
    align-items: center;
    /* padding-top: 0.1rem; */
    border-radius: 8px;
    /* padding-left: 3.7rem; */
    padding: 1rem;
    margin: 1rem;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
    border: 1px solid rgb(237, 237, 237);
    background-color: white;

    flex: 10;
  }

  .inside {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: auto;
  }

  /* Media query for smaller screens */
  @media (max-width: 768px) {
    .main-content {
      flex-direction: column;
      height: auto;
    }

    .left {
      flex-direction: row;
      margin-bottom: 0.5rem;
      padding: 0.5rem;
      gap: 1rem;
      padding-top: 2rem;
      padding-bottom: 2rem;
    }

    .right {
      margin-top: 0.5rem;
      width: auto;
      padding-top: 2rem;
      padding-bottom: 2rem;
    }
  }
</style>
