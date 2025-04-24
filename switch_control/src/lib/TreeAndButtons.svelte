<script lang="ts">
  import { tree } from "../state.svelte";
  // Remove unused imports if any: requestChannel, flipSwitch, reset
  import { getTreeState } from "../api"; // Keep getTreeState for now, though init handles it
  import { onMount } from "svelte";
  import type { TreeState, ButtonLabelState } from "../types"; // Import ButtonLabelState
  import TreeDiagram from "./TreeDiagram.svelte";
  // Remove ButtonState import if no longer needed locally
  // import type { ButtonState } from "../types";
  import GeneralButton from "./GeneralButton.svelte";
  import DotMenu from "./DotMenu.svelte";
  import ProtectedButton from "./ProtectedButton.svelte";

  // Remove local buttons_state, derive from tree.button_labels instead
  // let buttons_state: ButtonState[] = $state([...]);

  // Reactive proxy names for editing mode
  let proxy_labels = $state({ ...tree.button_labels });

  let button_mode = $state(true);

  function editChannelLabels() {
    // Initialize proxy labels with current labels when entering edit mode
    proxy_labels = { ...tree.button_labels };
    button_mode = false;
  }

  function defaultChannelLabels() {
    // Reset proxy labels and save default labels to backend
    const defaultLabels: ButtonLabelState = {
      label_0: "Ch 1",
      label_1: "Ch 2",
      label_2: "Ch 3",
      label_3: "Ch 4",
      label_4: "Ch 5",
      label_5: "Ch 6",
      label_6: "Ch 7",
      label_7: "Ch 8",
    };
    proxy_labels = { ...defaultLabels }; // Update local edit state
    tree.saveButtonLabels(defaultLabels); // Save to backend and update global state
    button_mode = true; // Exit edit mode
  }

  function clearAll() {
    // Clear only the proxy labels used for editing
    proxy_labels = {
      label_0: "",
      label_1: "",
      label_2: "",
      label_3: "",
      label_4: "",
      label_5: "",
      label_6: "",
      label_7: "",
    };
  }

  function finishChannelEdit() {
    // Prepare payload from proxy_labels
    const labelsToSave: ButtonLabelState = { ...proxy_labels };

    // Check if all proxy labels are empty; if so, revert to defaults
    const all_empty = Object.values(labelsToSave).every(
      (label) => label === "",
    );

    if (all_empty) {
      defaultChannelLabels(); // This already saves defaults and exits edit mode
    } else {
      // Save the edited labels from proxy_labels
      tree.saveButtonLabels(labelsToSave);
      button_mode = true; // Exit edit mode
    }
  }

  // Use tree.init() which now fetches both tree state and labels
  onMount(() => {
    tree.init().catch((error) => {
      console.error("Initialization failed:", error);
      // Handle initialization error (e.g., show message to user)
    });
  });

  // Helper to get the default name based on index
  function getDefaultName(index: number): string {
    return `Ch ${index + 1}`;
  }
</script>

<div class="container">
  <div class="tree"><TreeDiagram tree_state={tree.st} /></div>
  <div class="buttons">
    {#each { length: 8 } as _, idx}
      {@const labelKey = `label_${idx}` as keyof ButtonLabelState}
      <div class="spacer">
        {#if button_mode}
          <ProtectedButton
            onVerifiedClick={(verification) =>
              tree.toChannel(idx, verification)}
            width_rem={5}
            highlighted={tree.button_colors[idx]}
          >
            <!-- Display label from global state -->
            {tree.button_labels[labelKey]}
          </ProtectedButton>
        {:else}
          <input
            class="light"
            type="text"
            id={`name-${idx}`}
            name={`name-${idx}`}
            size="10"
            placeholder={getDefaultName(idx)}
            bind:value={proxy_labels[labelKey]}
          />
        {/if}
      </div>
    {/each}
  </div>
  <!-- ... rest of the component ... -->
  <div class="button-spacer">
    <DotMenu {editChannelLabels} {defaultChannelLabels}></DotMenu>
    {#if !button_mode}
      <div class="button-group">
        <GeneralButton onclick={clearAll} width_rem={5}>
          Clear All
        </GeneralButton>
        <GeneralButton onclick={finishChannelEdit} width_rem={5}>
          Finish
        </GeneralButton>
      </div>
    {/if}
  </div>
</div>

<style>
  /* ... existing styles ... */

  .button-group {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-top: 0rem;
    /* padding-left: 0.5rem; */
    height: 4.28rem;
    padding-bottom: 0rem;
    /* justify-content: space-between; */
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

  .light {
    color: #6b7280;
    /* background-color: #f8fafb; */
    border: 1.5px solid #dfe2e9;
  }

  .light:hover {
    color: #181d25;
    background-color: #f5f6f8;
  }

  .light::placeholder {
    color: #ccc;
  }

  .button-spacer {
    padding-left: 0.6rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    /* min-width: 7rem; */
  }

  .container {
    display: flex;
    /* flex-direction: row; */

    margin: auto;
    height: 315px;
  }

  .buttons {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-top: 0rem;
    padding-left: 0.5rem;
    padding-bottom: 0rem;
    /* justify-content: space-between; */
  }

  .tree {
    padding-top: 0.45rem;
    padding-bottom: 0.3rem;
  }
</style>
