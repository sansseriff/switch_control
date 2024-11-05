<script lang="ts">
  import { tree } from "../state.svelte";
  import { requestChannel, flipSwitch, getTreeState, reset } from "../api";
  import { onMount } from "svelte";
  import type { TreeState } from "../types";
  import TreeDiagram from "./TreeDiagram.svelte";
  import type { ButtonState } from "../types";
  import GeneralButton from "./GeneralButton.svelte";
  import DotMenu from "./DotMenu.svelte";

  let buttons_state: ButtonState[] = $state([
    { name: "Ch 1", proxy_name: "", default_name: "Ch 1", idx: 0, value: true },
    { name: "Ch 2", proxy_name: "", default_name: "Ch 2", idx: 1, value: true },
    { name: "Ch 3", proxy_name: "", default_name: "Ch 3", idx: 2, value: true },
    { name: "Ch 4", proxy_name: "", default_name: "Ch 4", idx: 3, value: true },
    { name: "Ch 5", proxy_name: "", default_name: "Ch 5", idx: 4, value: true },
    { name: "Ch 6", proxy_name: "", default_name: "Ch 6", idx: 5, value: true },
    { name: "Ch 7", proxy_name: "", default_name: "Ch 7", idx: 6, value: true },
    { name: "Ch 8", proxy_name: "", default_name: "Ch 8", idx: 7, value: true },
  ]);

  let button_mode = $state(true);
  let button_colors = $state([false, false, false, false, false, false, false, false]);

  function toChannel(idx: number) {
    requestChannel({ number: idx }).then((ss: TreeState) => {
      // console.log("new state: ", ss);

      button_colors.forEach((color, i) => {
        // console.log("i: ", i);
        // console.log("idx: ", idx);
        button_colors[i] = i === idx;
        // console.log("color: ", button_colors[i]);
      });

      // console.log("button colors: ", button_colors);

      tree.st = ss;
    });
  }

  function editChannelLabels() {
    button_mode=false;
  }

  function defaultChannelLabels() {
    button_mode = true;
    buttons_state.forEach((button) => {
      button.name = button.default_name;
    });
  }

  function clearAll() {
    buttons_state.forEach((button) => {
      button.proxy_name = "";
    });
  }

  function finishChannelEdit() {
    buttons_state.forEach((button) => {
      button.name = button.proxy_name;
    });

    // if all buttons are empty, reset to default
    let all_empty = true;
    buttons_state.forEach((button) => {
      if (button.proxy_name !== "") {
        all_empty = false;
      }
    });
    if (all_empty) {
      defaultChannelLabels();
    }

    button_mode = true;
  }

  onMount(() => {
    getTreeState().then((ss: TreeState) => {
      tree.st = ss;
    });
  });
</script>

<div class="container">
  <div class="tree"><TreeDiagram tree_state={tree.st} /></div>
  <div class="buttons">
    {#each buttons_state as button, idx}
      <div class="spacer">

        <!-- if button_mode -->
        {#if button_mode}
          <GeneralButton onclick={() => toChannel(button.idx)} width_rem={5} highlighted={button_colors[idx]}>
            {button.name}
          </GeneralButton>
        {:else}
          <input class="light" type="text" id="name" name="name" size="10" placeholder={button.default_name} bind:value={button.proxy_name}/>
        {/if}

      </div>
    {/each}
  </div>
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
  .button-group {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-top: 0.0rem;
    /* padding-left: 0.5rem; */
    height: 4.28rem;
    padding-bottom: 0.0rem;
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
    font-family:Arial, Helvetica, sans-serif;
  }

  .light {
    color: #6b7280; 
    background-color: #f8fafb;
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
    min-width: 7rem;
  }
  .spacer {
    /* padding-top: 0.44rem; */
    /* padding-bottom: 0.88rem; */
  }
  .container {
    display: flex;
    flex-direction: row;
    justify-content: left;
    padding-top: 0.1rem;
    border: 1px solid rgb(237, 237, 237);
    background-color: white;
    border-radius: 8px;
    padding-left: 5rem;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }

  .buttons {
    display: flex;
    flex-direction: column;
    justify-content:space-between;
    padding-top: 0.0rem;
    padding-left: 0.5rem;
    padding-bottom: 0.0rem;
    /* justify-content: space-between; */
  }

  .switches {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding-top: 0.1rem;
    padding-left: 0.5rem;
  }

  .row_spacer {
    padding-left: 1rem;
    display: flex;
    flex-direction: row;
    justify-content: center;
  }

  .tree {
    padding-top: 0.45rem;
    padding-bottom: 0.3rem;
  }

  .id {
    width: 2rem;
    text-align: center;
    font-family: Arial, Helvetica, sans-serif;
  }
</style>
