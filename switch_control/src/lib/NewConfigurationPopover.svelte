<script lang="ts">
  import { Dialog } from "bits-ui";
  import { PlusIcon } from "phosphor-svelte";
  import { config } from "../configuration.svelte";
  import "../dialog.css";

  interface Props {
    onStartEditing: () => void;
  }

  let { onStartEditing }: Props = $props();
  let isOpen = $state(false);
  let isSaving = $state(false);
  let error = $state("");

  async function stashAndEdit() {
    if (isSaving) return;
    isSaving = true;
    error = "";
    try {
      await config.stash();
      isOpen = false;
      onStartEditing();
    } catch (cause) {
      error =
        cause instanceof Error
          ? cause.message
          : "Could not stash the configuration.";
    } finally {
      isSaving = false;
    }
  }
</script>

<Dialog.Root bind:open={isOpen}>
  <Dialog.Trigger>
    <button
      type="button"
      class="icon-button"
      aria-label="New Configuration"
      title="New Configuration"
    >
      <PlusIcon size={25} />
    </button>
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content class="new-config-dialog">
      <Dialog.Title>New configuration</Dialog.Title>
      <Dialog.Description>
        Stash title and button labels and enter edit mode?
      </Dialog.Description>
      {#if error}<p class="error" role="alert">{error}</p>{/if}
      <div class="actions">
        <button type="button" onclick={() => (isOpen = false)}>No</button>
        <button type="button" class="yes" onclick={stashAndEdit}>
          {isSaving ? "Saving…" : "Yes"}
        </button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<style>
  .icon-button {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1.8rem;
    height: 1.8rem;
    margin-bottom: 0.3rem;
    padding: 0;
    cursor: pointer;
    color: rgb(127, 127, 127);
    background: transparent;
    border: 0;
    border-radius: 0.375rem;
  }
  .icon-button:hover {
    background: #ededed;
  }
  .icon-button:active {
    color: #000;
  }

  :global(.new-config-dialog) {
    max-width: min(25rem, calc(100% - 2rem));
  }
  p.error {
    margin: 0 0 0.5rem;
    color: #b42318;
    font-size: 0.78rem;
  }
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.45rem;
    margin-top: 0.8rem;
  }
  .actions button {
    min-width: 3.8rem;
    height: 1.7rem;
    cursor: pointer;
    color: #606673;
    background: white;
    border: 1.5px solid #dfe2e9;
    border-radius: 0.25rem;
  }
  .actions button:hover {
    background: #f5f6f8;
  }
  .actions .yes {
    color: #534deb;
    border-color: #534deb;
    font-weight: 600;
  }
  @media (max-width: 500px) {
    .icon-button {
      margin: 0 0.25rem 0 0;
    }
  }
</style>
