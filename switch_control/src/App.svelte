<script lang="ts">
  import { Gear } from "phosphor-svelte";
  import { ClockCountdown } from "phosphor-svelte";
  import { Plus } from "phosphor-svelte";
  import { PencilSimple } from "phosphor-svelte";
  import { ThermometerSimple, ThermometerCold } from "phosphor-svelte";

  import { onMount } from "svelte";

  import { tree } from "./state.svelte";
  import TreeAndButtons from "./lib/TreeAndButtons.svelte";
  import MenuDialog from "./lib/MenuDialog.svelte";
  import TooltipIcon from "./lib/TooltipIcon.svelte";
  import CryoCheck from "./lib/CryoCheck.svelte";

  let isLoading = $state(import.meta.env.SKIP_LOADING !== "true");
  let isMenuOpen = $state(false);
  let isCryoCheckOpen = $state(false);
  let inactivityMs = 8 * 60 * 60 * 1000; // 8 hours in milliseconds
  let inactivityTimer: any = null;

  onMount(() => {
    let disposed = false;
    const onActivity = () => resetInactivityTimer();

    (async () => {
      // await new Promise((resolve) => setTimeout(resolve, 1));
      await tree.init();
      // even though I don't use the ouptut of tree.init(), its important that
      // that it returns a promise. Because awaiting that promise delays the
      // setting of isLoading to false. If isLoading is set to false too soon,
      // then the onMount function in contained components will trigger
      // api calls to get_tree before the tree is initialized. Causing an error.
      if (disposed) return;
      isLoading = false;

      // start inactivity monitor after init
      resetInactivityTimer();
      // listen for user activity
      window.addEventListener("mousemove", onActivity);
      window.addEventListener("keydown", onActivity);
      window.addEventListener("pointerdown", onActivity);
      window.addEventListener("scroll", onActivity, { passive: true });
    })();

    return () => {
      disposed = true;
      window.removeEventListener("mousemove", onActivity);
      window.removeEventListener("keydown", onActivity);
      window.removeEventListener("pointerdown", onActivity);
      window.removeEventListener("scroll", onActivity);
      if (inactivityTimer) clearTimeout(inactivityTimer);
    };
  });

  function resetInactivityTimer() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
      isCryoCheckOpen = true;
    }, inactivityMs);
  }
</script>

<main>
  <!-- <div class="top-bar pywebview-drag-region"></div>
  <div class="top-bar pywebview-drag-region"></div> -->
  <div class="top-menu-section">
    <TooltipIcon label={"Runtime settings"} onclick={() => (isMenuOpen = true)}>
      <Gear size={25} />
    </TooltipIcon>
    <TooltipIcon label={"Label history"} onclick={() => {}}>
      <ClockCountdown size={25} />
    </TooltipIcon>
  </div>

  <div class="main-content">
    {#if isLoading}
      <div class="loading-screen">
        <p>Loading...</p>
      </div>
    {:else}
      <!-- <div class="left">
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
      </div> -->
      <!-- <div class="rright"> -->
      <div class="spacer"></div>
      <div class="inside"><TreeAndButtons></TreeAndButtons></div>
      <div class="spacer">
        <div class="top-group">
          <div class="icon-holder">
            {#if tree.cryo_mode}
              <ThermometerCold size={25} style="color: #4d79ff;" />
            {:else}
              <ThermometerSimple size={25} style="color: black;" />
            {/if}
          </div>
        </div>

        <div class="bottom-group">
          <TooltipIcon
            label={"New Configuration"}
            onclick={() => (isMenuOpen = true)}
          >
            <Plus size={25} />
          </TooltipIcon>
          <TooltipIcon
            label={"Edit Configuration"}
            onclick={() => (isMenuOpen = true)}
          >
            <PencilSimple size={25} />
          </TooltipIcon>
        </div>
      </div>
      <!-- </div> -->
    {/if}
  </div>

  <MenuDialog bind:isOpen={isMenuOpen} />
  <CryoCheck bind:isOpen={isCryoCheckOpen} />
</main>

<style>
  .icon-holder {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1.8rem;
    height: 1.8rem;
    border-radius: 0.375rem;
    color: rgb(127, 127, 127);
    margin-bottom: 0.3rem;
    background-color: transparent;
    border: none;
    padding: 0;
  }

  .top-menu-section {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    padding: 0.6rem 0.3rem;
    /* background-color: #f5f5f5; */
    border-right: 1px solid #e2e2e2;
    width: 2.8rem;
    background-color: #fafafa;
  }

  .spacer {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    width: 2.8rem;
    height: 100%;
    margin: 0.3rem;
    padding-bottom: 0.3rem;
    padding-top: 0.3rem;
  }

  main {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    height: 100vh;
    display: flex;
    flex-direction: row;
    background-color: white;
  }

  /* icon-holder styles moved into TooltipIcon */

  .loading-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }

  .main-content {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    padding: 0;
    width: 100%;
    background-color: white;
    /* padding: 3rem; */
  }

  /* .rright {
    
  } */

  .inside {
    display: flex;
    flex-direction: row;
    /* justify-content: space-between;
    align-items: flex-start; */
    width: 100%;
    margin: auto;
  }

  /* Media query for smaller screens */
  @media (max-width: 500px) {
    main {
      flex-direction: column;
      height: 100vh;
    }

    .main-content {
      flex-direction: column;
      height: auto;
    }

    .top-menu-section {
      width: 100%;
      flex-direction: row;
      padding: 0.3rem 0.3rem;
      border-left: none;
      border-bottom: 1px solid #e2e2e2;
      height: 2.8rem;
      padding-left: 0.6rem;
      align-items: center;
      justify-content: left;
    }
  }
</style>
