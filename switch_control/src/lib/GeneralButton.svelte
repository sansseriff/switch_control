<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    onclick: (event: MouseEvent) => void;
    children: Snippet;
    width_rem?: number;
    highlighted?: boolean;
    danger?: boolean;
    info?: string;
  }

  let {
    onclick,
    children,
    width_rem = 6.5,
    highlighted = false,
    danger = false,
    info = "",
  }: Props = $props();
</script>

<button
  class="button light"
  class:highlighted
  class:danger
  {onclick}
  style="width: {width_rem}rem"
>
  {@render children()}
</button>

<style>
  .button {
    cursor: pointer;
    all: unset;
    display: inline-block;
    cursor: pointer;
    appearance: none;

    box-sizing: border-box;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.25rem;
    height: 1.7rem;

    /* width: 6.5rem; */
    text-align: center;
    font-family: Arial, Helvetica, sans-serif;
  }

  .light {
    color: #6b7280;
    /* background-color: #f8fafb; */
    border: 1.5px solid #dfe2e9;
  }

  .light:hover {
    /* color: #181d25; */
    background-color: #f5f6f8;
  }

  .highlighted {
    /* background-color: #eef1f7; */
    border: 2.3px solid #534deb;
    color: #534deb;
  }

  .danger {
    border: 2.3px solid #f87171;
    color: #f87171;
  }

  .danger:hover {
    background-color: #ffeded;
  }

  .highlighted:hover {
    background-color: #efeeff;
  }
</style>
