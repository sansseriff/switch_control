<script lang="ts">
  import { tree } from "../state.svelte";
  import type { Verification } from "../types";
  import VerifiedIconButton from "./VerifiedIconButton.svelte";

  interface Props {
    name: string;
  }
  let { name = "R1" }: Props = $props();

  function handleVerifiedClick(verification: Verification) {
    tree.toggle(name, verification);
  }
</script>

<div class="container">
  <div class="label">{name}</div>
  <VerifiedIconButton
    ariaLabel="switch_toggle"
    onVerifiedClick={handleVerifiedClick}
  ></VerifiedIconButton>
</div>

<style>
  .container {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: auto;
  }

  .label {
    box-sizing: border-box;
    margin-left: 2rem;
    display: inline-flex;
    align-items: center;
    justify-content: right;
    border-radius: 2rem;
    width: 3.3rem;
    height: 1.6rem;
    padding-right: 0.2rem;
    padding-top: 0.1rem;
    font-size: 200;
    background-color: rgb(246, 246, 246);
    border: 1.5px solid rgb(235, 235, 235);
    position: relative;
    box-shadow: 4px 4px 5px rgba(0, 0, 0, 0.05);
  }
</style>
