<script lang="ts">
  import type { Verification } from "../types";
  import VerificationDialog from "./VerificationDialog.svelte";

  interface Props {
    onVerifiedClick: (verification: Verification) => void;
    className?: string;
    ariaLabel?: string;
  }

  let {
    onVerifiedClick,
    className = "",
    ariaLabel = "button",
  }: Props = $props();

  let isOpen = $state(false);
</script>

<button
  class="clicker"
  aria-label={ariaLabel}
  onclick={() => {
    isOpen = true;
  }}
>
  <svg
    width="1.2rem"
    height="1.2rem"
    viewBox="0 0 30 47"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M16.6796 0.875337C15.8985 0.0942886 14.6322 0.0942886 13.8512 0.875337L1.12325 13.6033C0.342197 14.3843 0.342197 15.6506 1.12325 16.4317C1.90429 17.2127 3.17062 17.2127 3.95167 16.4317L15.2654 5.11798L26.5791 16.4317C27.3601 17.2127 28.6265 17.2127 29.4075 16.4317C30.1886 15.6506 30.1886 14.3843 29.4075 13.6033L16.6796 0.875337ZM13.8512 46.0373C14.6322 46.8183 15.8985 46.8183 16.6796 46.0373L29.4075 33.3093C30.1886 32.5283 30.1886 31.262 29.4075 30.4809C28.6265 29.6999 27.3601 29.6999 26.5791 30.4809L15.2654 41.7946L3.95167 30.4809C3.17062 29.6999 1.9043 29.6999 1.12325 30.4809C0.342198 31.262 0.342198 32.5283 1.12325 33.3093L13.8512 46.0373ZM13.2654 2.28955L13.2654 44.623L17.2654 44.623L17.2654 2.28955L13.2654 2.28955Z"
      fill="rgba(170, 170, 170, 1)"
      stroke="rgba(170, 170, 170, 1)"
      stroke-width="1.6"
    />
  </svg>
</button>

<VerificationDialog bind:isOpen {onVerifiedClick}></VerificationDialog>

<style>
  button {
    box-sizing: border-box;
    background: none;
    border: none;
  }

  .clicker {
    position: absolute;
    box-sizing: border-box;
    border-radius: 100%;
    width: 1.6rem;
    height: 1.6rem;

    background-color: rgb(246, 246, 246);
    border: 1.5px solid rgb(244, 244, 244);
    box-shadow: 4px 4px 5px rgba(0, 0, 0, 0.05);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    pointer-events: auto;
  }

  .clicker:hover {
    background-color: rgb(255, 255, 255);
    border: 1.5px solid rgb(244, 244, 244);
  }

  .clicker:active {
    transform: scale(0.95);
  }
</style>
