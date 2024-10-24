<script lang="ts">
  import { tree } from "../state.svelte";
  import { requestChannel, flipSwitch, getTreeState, reset } from "../api";
  import { onMount } from "svelte";
  import type { SwitchState } from "../types";
  import TreeDiagram from "./TreeDiagram.svelte";
  import type { ButtonState } from "../types";
  import GeneralButton from "./GeneralButton.svelte";
  import DotMenu from "./DotMenu.svelte";

  let buttons_state: ButtonState[] = [
    { name: "Ch 1", proxy_name: "", idx: 0, value: true },
    { name: "Ch 2", proxy_name: "", idx: 1, value: true },
    { name: "Ch 3", proxy_name: "", idx: 2, value: true },
    { name: "Ch 4", proxy_name: "", idx: 3, value: true },
    { name: "Ch 5", proxy_name: "", idx: 4, value: true },
    { name: "Ch 6", proxy_name: "", idx: 5, value: true },
    { name: "Ch 7", proxy_name: "", idx: 6, value: true },
    { name: "Ch 8", proxy_name: "", idx: 7, value: true },
  ];

  function toggle(key: string) {
    // key is "R1", "R2", etc.
    // convert to idx
    let idx = parseInt(key.slice(1));

    flipSwitch({ number: idx }).then((ss: SwitchState) => {
      console.log("new state: ", ss);
      tree.st = ss;
    });
    tree.st[key] = !tree.st[key];
  }

  function toChannel(idx: number) {
    requestChannel({ number: idx }).then((ss: SwitchState) => {
      console.log("new state: ", ss);
      tree.st = ss;
    });
  }

  onMount(() => {
    getTreeState().then((ss: SwitchState) => {
      // console.log("new state in onmount: ", ss);
      tree.st = ss;
    });
  });
</script>

<div class="container">
  <div class="tree"><TreeDiagram switch_state={tree.st} /></div>
  <div class="buttons">
    {#each buttons_state as button}
      <div class="spacer">
        <GeneralButton onclick={() => toChannel(button.idx)}>
          {button.name}
        </GeneralButton>

        <!-- <input type="text" id="name" name="name" size="10" /> -->
      </div>
    {/each}
  </div>
  <div class="button-spacer">
    <DotMenu></DotMenu>
  </div>
  
</div>

<style>

  .button-spacer {
    padding-left: 0.6rem;
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
    border: 1px solid rgb(223, 223, 223);
    background-color: white;
    border-radius: 8px;
    padding: 1rem;
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
