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

  let title_label = $state("Title Here");
  // Dynamic width for the title (h2/input) so it expands with text
  let titleWidthPx = $state(160);
  let measureEl: HTMLElement | null = null;

  function recomputeTitleWidth() {
    // Use placeholder text when empty so the control doesn't collapse
    const text = (title_label && title_label.trim() !== "")
      ? title_label
      : "Title Here";
    if (!measureEl) return;
    // Update the hidden measurement element's text then read its width
    measureEl.textContent = text;
    // Include a small ceil to avoid sub-pixel clipping
    const measured = Math.ceil(measureEl.offsetWidth);
    // Minimum width similar to prior ~5rem default for stability
    const rootFs = parseFloat(getComputedStyle(document.documentElement).fontSize || "16");
    const minPx = 5 * (Number.isNaN(rootFs) ? 16 : rootFs);
    titleWidthPx = Math.max(minPx, measured);
  }

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
  // Ensure initial width is computed once fonts/styles have applied
  recomputeTitleWidth();

      // start inactivity monitor after init
      resetInactivityTimer();
      // listen for user activity
      window.addEventListener("mousemove", onActivity);
      window.addEventListener("keydown", onActivity);
      window.addEventListener("pointerdown", onActivity);
      window.addEventListener("scroll", onActivity, { passive: true });
  window.addEventListener("resize", recomputeTitleWidth);
    })();

    return () => {
      disposed = true;
      window.removeEventListener("mousemove", onActivity);
      window.removeEventListener("keydown", onActivity);
      window.removeEventListener("pointerdown", onActivity);
      window.removeEventListener("scroll", onActivity);
  window.removeEventListener("resize", recomputeTitleWidth);
      if (inactivityTimer) clearTimeout(inactivityTimer);
    };
  });

  function resetInactivityTimer() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
      isCryoCheckOpen = true;
    }, inactivityMs);
  }

  // Recompute width reactively when text or mode changes
  $effect(() => {
    title_label;
    tree.button_mode;
    // Use a microtask to let DOM/text update before measuring
    queueMicrotask(recomputeTitleWidth);
  });
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
    <div class="title-holder">
      {#if tree.button_mode}
        <h2 class="input-label" style={`width: ${titleWidthPx}px`}>{title_label}</h2>
      {:else}
        <input
          class="input-label light"
          type="text"
          size="10"
          placeholder={"Title Here"}
          bind:value={title_label}
          style={`width: ${titleWidthPx}px`}
        />
      {/if}

      <div class="top-group">
        <div class="icon-holder">
          {#if tree.cryo_mode}
            <ThermometerCold size={25} style="color: #4d79ff;" />
          {:else}
            <ThermometerSimple size={25} style="color: black;" />
          {/if}
        </div>
      </div>
    </div>

    <div class="else">
      {#if isLoading}
        <div class="loading-screen">
          <p>Loading...</p>
        </div>
      {:else}
        <div class="inside">
          <TreeAndButtons></TreeAndButtons>
          <div class="title-spacer"></div>
          <!-- <div class="title-holder"></div> -->
        </div>
        <div class="spacer">
          <div class="bottom-group">
            <TooltipIcon
              label={"Edit Configuration"}
              onclick={() => (tree.button_mode = false)}
            >
              <PencilSimple size={25} />
            </TooltipIcon>
            <TooltipIcon
              label={"New Configuration"}
              onclick={() => (isMenuOpen = true)}
            >
              <Plus size={25} />
            </TooltipIcon>
          </div>
        </div>
        <!-- </div> -->
      {/if}
    </div>
  </div>

  <MenuDialog bind:isOpen={isMenuOpen} />
  <CryoCheck bind:isOpen={isCryoCheckOpen} />
  <!-- Hidden measurement element to compute exact width including padding/border -->
  <span
    class="input-label measure"
    aria-hidden="true"
    bind:this={measureEl}
  >{title_label}</span>
</main>

<style>
  h2 {
    color: rgb(152, 152, 152);
  }
  .top-group {
    /* width: 100%;
    height: 100%; */
  }

  .icon-holder {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1.8rem;
    height: 1.8rem;
    border-radius: 0.375rem;
    color: rgb(127, 127, 127);
    margin-bottom: 0.3rem;
    margin-top: 0.3rem;
    background-color: transparent;
    border: none;
    padding: 0;
  }

  .bottom-group {
    width: 100%;
    display: flex;
    flex-direction: column;
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
    justify-content: flex-end;
    align-items: center;
    /* width: 2.8rem; */
    height: 100%;
    box-sizing: border-box;
    margin: 0;
    padding-bottom: 0.3rem;
    padding-top: 0.3rem;
    margin-left: 0.2rem;
    margin-right: 0.2rem;
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
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-start;
    padding: 0;
    width: 100%;
    background-color: white;
    /* height: 100%; */
  }

  .title-holder {
    /* height: 4rem; */
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    /* margin: 0.2rem; */
    margin: 0;
    padding: 0;
  }

  .else {
    display: flex;
    flex-direction: row;
    /* justify-content: space-between; */
    align-items: center;
    flex: 1;
    min-width: 0;
    padding: auto;
    width: 100%;
  }

  input {
    all: unset;
    cursor: text;
    text-align: left;
    display: inline-block;
    cursor: text;
    appearance: none;

    box-sizing: border-box;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.25rem;

  padding-left: 0.2rem;
  padding-right: 0.2rem;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
    height: 1.7rem;

    width: 5rem;
    font-family: Arial, Helvetica, sans-serif;
  }

  

  .light:hover {
    color: #181d25;
    background-color: #f5f6f8;
  }

  .input-label {
    /* Make input and h2 occupy identical geometry so text doesn't jump when toggling */
    box-sizing: border-box;
    display: inline-flex;
    align-items: center;
  /* Keep as a single line and avoid flexbox shrinking */
  white-space: nowrap;
  flex: 0 0 auto;

    /* Typography unified for both input and h2 */
    font-family: Arial, Helvetica, sans-serif;
    font-size: large;
    font-weight: 500;

    /* Sizing + vertical centering */
    height: 2rem;
    line-height: 2rem;

    /* Padding matches input so inner text position is identical */
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    padding-right: 0.2rem;
    padding-left: 0.5rem;

    /* Remove default h2 top/bottom margins while preserving the left offset */
    margin: 0;
    margin-left: 0.25rem;

    /* Reserve space for the editable border even in display mode */
    border: 1.5px solid transparent;
    border-radius: 0.25rem;
  }

  .light {
    color: #6b7280;
  /* Always show the border in edit mode */
   border: 1.5px solid #dfe2e9; /* slightly stronger than #dfe2e9 */
    background-color: #ffffff;
  }

  .inside {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    /* justify-content: space-between;
    align-items: flex-start; */
    /* width: 100%; */
    /* margin: auto; */
    flex: 1 1 auto;
    min-width: 0;
    height: 100%;
  }

  .title-spacer {
    height: 2.5rem;
  }

  /* Hidden measurement element used to size the title precisely */
  .measure {
    position: absolute;
    visibility: hidden;
    white-space: pre;
    left: -9999px;
    top: -9999px;
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
