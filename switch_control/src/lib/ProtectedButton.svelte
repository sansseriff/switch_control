<script lang="ts">
  import type { Snippet } from "svelte";
  import type { Verification } from "../types";
  import VerificationDialog from "./VerificationDialog.svelte";

  interface Props {
    onVerifiedClick: (verification: Verification) => void;
    children: Snippet;
    width_rem?: number;
    highlighted?: boolean;
    info?: string;
  }

  let isOpen = $state(false);

  let {
    onVerifiedClick,
    children,
    width_rem = 6.5,
    highlighted = false,
    info = "",
  }: Props = $props();
</script>

<button
  class="button light m-3"
  aria-label="switch_toggle"
  onclick={() => {
    isOpen = true;
  }}
  class:highlighted
  style="width: {width_rem}rem"
>
  {@render children()}
</button>

<VerificationDialog bind:isOpen {onVerifiedClick}></VerificationDialog>

<style>
  .button {
    all: unset;
    display: inline-block;
    cursor: pointer;
    appearance: none;

    box-sizing: border-box;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.25rem;

    padding-left: 0rem;
    padding-right: 0rem;
    padding-top: 0.17rem;
    padding-bottom: 0.25rem;
    height: 1.7rem;

    /* width: 6.5rem; */
    text-align: center;
    font-family: Arial, Helvetica, sans-serif;
  }

  .light {
    color: #6b7280;
    border: 1.5px solid #dfe2e9;
  }

  .light:hover {
    color: #181d25;
    background-color: #f5f6f8;
  }

  .highlighted {
    border: 2.3px solid #534deb;
    color: #534deb;
  }
</style>
