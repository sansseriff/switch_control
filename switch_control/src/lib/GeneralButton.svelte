<script lang="ts">
    import type { Snippet } from "svelte";
    // import { createEventDispatcher } from 'svelte';
    // export let uiStateStore;
    // import { ui_state } from "../../state/uiState.svelte";
  
    interface Props {
      onclick: (event: MouseEvent) => void;
      children: Snippet;
      width_rem?: number;
    }
  
    let { onclick, children, width_rem = 6.5 }: Props = $props();

  </script>
  
  
  <button class="button light" {onclick} style="width: {width_rem}rem">
    {@render children()}
  </button>
  
  
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

    padding-left: 1rem;
    padding-right: 1rem; 
    padding-top: 0.25rem; 
    padding-bottom: 0.25rem; 
    height: 1.7rem;
    
    /* width: 6.5rem; */
    text-align: center;
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

  .dark {
    color: #6b7280; 
    border-color: #6b7280; 
    background-color: #f9fafb; 
  }

  .dark:hover {
    background-color: #f3f4f6; 
  }
  </style>
  