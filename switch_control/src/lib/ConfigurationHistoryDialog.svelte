<script lang="ts">
  import { Dialog } from "bits-ui";
  import { XIcon } from "phosphor-svelte";
  import { config } from "../configuration.svelte";
  import type { ConfigurationHistoryItem } from "../types";
  import GeneralButton from "./GeneralButton.svelte";
  import "../dialog.css";

  interface Props {
    isOpen: boolean;
  }

  let { isOpen = $bindable() }: Props = $props();
  let items = $state<ConfigurationHistoryItem[]>([]);
  let selectedId = $state<number | null>(null);
  let isLoading = $state(false);
  let isApplying = $state(false);
  let error = $state("");
  let wasOpen = false;

  $effect(() => {
    if (isOpen && !wasOpen) void refresh();
    wasOpen = isOpen;
  });

  async function refresh() {
    isLoading = true;
    error = "";
    selectedId = null;
    try {
      items = await config.history();
    } catch (cause) {
      items = [];
      error = messageFor(cause, "Could not load configuration history.");
    } finally {
      isLoading = false;
    }
  }

  async function applySelected() {
    if (selectedId === null || isApplying) return;
    isApplying = true;
    error = "";
    try {
      await config.load(selectedId);
      config.is_editing = false;
      isOpen = false;
    } catch (cause) {
      error = messageFor(cause, "Could not load that configuration.");
    } finally {
      isApplying = false;
    }
  }

  function messageFor(cause: unknown, fallback: string) {
    return cause instanceof Error ? cause.message : fallback;
  }

  function displayDate(value: string) {
    const date = new Date(value);
    return Number.isNaN(date.valueOf()) ? value : date.toLocaleString();
  }
</script>

<Dialog.Root bind:open={isOpen}>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content class="history-dialog">
      <Dialog.Title>Label history</Dialog.Title>
      <Dialog.Description>
        Select a stashed configuration by title and saved time.
      </Dialog.Description>

      <div class="history-list" aria-label="Saved configurations">
        {#if isLoading}
          <p class="status">Loading history…</p>
        {:else if items.length === 0}
          <p class="status">No configurations have been stashed yet.</p>
        {:else}
          {#each items as item (item.id)}
            <button
              type="button"
              class="history-item"
              class:selected={selectedId === item.id}
              aria-pressed={selectedId === item.id}
              onclick={() => (selectedId = item.id)}
              ondblclick={applySelected}
            >
              <span class="history-title">{item.title_label || "Untitled"}</span
              >
              <time datetime={item.created_at}
                >{displayDate(item.created_at)}</time
              >
            </button>
          {/each}
        {/if}
      </div>

      {#if error}<p class="error" role="alert">{error}</p>{/if}

      <div class="actions">
        <GeneralButton onclick={() => (isOpen = false)}>Cancel</GeneralButton>
        <GeneralButton
          onclick={applySelected}
          highlighted={selectedId !== null}
        >
          {isApplying ? "Loading…" : "Load"}
        </GeneralButton>
      </div>

      <Dialog.Close>
        <div class="close-icon">
          <XIcon />
          <span class="sr-only">Close</span>
        </div>
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<style>
  :global(.history-dialog) {
    max-width: min(490px, calc(100% - 2rem));
  }

  .history-list {
    min-height: 8rem;
    max-height: min(22rem, 55vh);
    overflow-y: auto;
    border: 1px solid #e2e5ea;
    border-radius: 0.375rem;
    background: #fafafa;
  }

  .history-item {
    all: unset;
    box-sizing: border-box;
    display: flex;
    width: 100%;
    flex-direction: column;
    gap: 0.2rem;
    padding: 0.7rem 0.8rem;
    cursor: pointer;
    border-bottom: 1px solid #e8eaee;
  }

  .history-item:last-child {
    border-bottom: 0;
  }
  .history-item:hover {
    background: #f2f2f8;
  }
  .history-item:focus-visible {
    outline: 2px solid #534deb;
    outline-offset: -2px;
  }
  .history-item.selected {
    background: #efeeff;
    box-shadow: inset 3px 0 #534deb;
  }

  .history-title {
    color: #22252b;
    font-size: 0.925rem;
    font-weight: 600;
    overflow-wrap: anywhere;
  }

  time {
    color: #747983;
    font-size: 0.78rem;
  }
  .status {
    margin: 0;
    padding: 2.5rem 1rem;
    text-align: center;
    color: #747983;
  }
  .error {
    margin: 0.65rem 0 0;
    color: #b42318;
    font-size: 0.82rem;
  }
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1rem;
  }
</style>
