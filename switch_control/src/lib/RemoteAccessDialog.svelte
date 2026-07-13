<script lang="ts">
  import { Dialog } from "bits-ui";
  import { CheckIcon, CopyIcon, XIcon } from "phosphor-svelte";
  import QrCode from "svelte-qrcode";
  import { runtime } from "../sync.svelte";
  import "../dialog.css";

  interface Props {
    isOpen: boolean;
  }

  interface ServerInfo {
    hostname: string;
    ipaddr: string;
    ipaddrs: string[];
    port: number;
    passphrase: string;
    invite: string;
    invite_expires_at: string;
  }

  let { isOpen = $bindable() }: Props = $props();
  let urls = $state<string[]>([]);
  let selected = $state(0);
  let isLoading = $state(false);
  let error = $state("");
  let copiedUrl = $state("");
  let passphrase = $state("");
  let wasOpen = false;

  const accessUrl = $derived(urls[selected] ?? "");

  $effect(() => {
    if (isOpen && !wasOpen) void loadServerInfo();
    wasOpen = isOpen;
  });

  async function loadServerInfo() {
    isLoading = true;
    error = "";
    copiedUrl = "";
    try {
      const ack = await runtime.sendCommand<ServerInfo>("get_server_info");
      if (!ack.result) throw new Error("The server returned no network information.");
      const addresses = ack.result.ipaddrs?.length
        ? ack.result.ipaddrs
        : [ack.result.ipaddr];
      passphrase = ack.result.passphrase;
      urls = addresses.map(
        (ipaddr) =>
          `http://${ipaddr}:${ack.result!.port}/#invite=${encodeURIComponent(ack.result!.invite)}`,
      );
      selected = 0;
      if (addresses.every((ipaddr) => ipaddr.startsWith("127."))) {
        error = "No network address was found. Connect this computer to the same network as the remote device.";
      }
    } catch (cause) {
      urls = [];
      passphrase = "";
      error = cause instanceof Error
        ? cause.message
        : "Could not discover remote-access addresses.";
    } finally {
      isLoading = false;
    }
  }

  async function copyValue(value: string) {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = value;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
      }
      copiedUrl = value;
      window.setTimeout(() => {
        if (copiedUrl === value) copiedUrl = "";
      }, 1600);
    } catch {
      error = "Could not copy the value. Select and copy it manually.";
    }
  }
</script>

<Dialog.Root bind:open={isOpen}>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content class="remote-dialog">
      <Dialog.Title>Remote access</Dialog.Title>
      <Dialog.Description>
        On a phone or tablet connected to the same network, scan the QR code
        or open one of the addresses below.
      </Dialog.Description>

      <div class="warning" role="note">
        Each QR code or copied address works once and expires after five
        minutes. The passphrase remains available for manual login. This local
        HTTP connection is not encrypted, so use it only on a trusted network.
      </div>

      {#if isLoading}
        <div class="status">Finding network addresses…</div>
      {:else if accessUrl}
        <div class="qr-frame">
          <QrCode
            value={accessUrl}
            size={176}
            padding={8}
            errorCorrection="M"
          />
        </div>

        <div class="passphrase-row">
          <span>Passphrase</span>
          <code>{passphrase}</code>
          <button
            type="button"
            class="copy-button"
            onclick={() => copyValue(passphrase)}
            aria-label="Copy remote-access passphrase"
            title="Copy passphrase"
          >
            {#if copiedUrl === passphrase}
              <CheckIcon size={18} />
            {:else}
              <CopyIcon size={18} />
            {/if}
          </button>
        </div>

        <div class="url-list" aria-label="Available remote addresses">
          {#each urls as url, index (url)}
            <div class="url-row" class:selected={selected === index}>
              <button
                type="button"
                class="url-select"
                onclick={() => (selected = index)}
                aria-pressed={selected === index}
                title="Show QR code for this address"
              >
                {url}
              </button>
              <button
                type="button"
                class="copy-button"
                onclick={() => copyValue(url)}
                aria-label={`Copy ${url}`}
                title="Copy address"
              >
                {#if copiedUrl === url}
                  <CheckIcon size={18} />
                {:else}
                  <CopyIcon size={18} />
                {/if}
              </button>
            </div>
          {/each}
        </div>
      {/if}

      {#if error}
        <p class="error-message" role="alert">{error}</p>
      {/if}

      <div class="dialog-actions">
        {#if accessUrl}
          <a href={accessUrl} target="_blank" rel="noreferrer">Open address</a>
        {/if}
        <button type="button" class="done-button" onclick={() => (isOpen = false)}>
          Done
        </button>
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
  .warning {
    margin-bottom: 0.8rem;
    border: 1px solid #f2d29a;
    border-radius: 0.35rem;
    background: #fff8e8;
    color: #76551d;
    padding: 0.55rem 0.65rem;
    font-size: 0.78rem;
    line-height: 1.35;
  }

  .status {
    display: flex;
    min-height: 10rem;
    align-items: center;
    justify-content: center;
    color: var(--foreground-alt);
    font-size: 0.875rem;
  }

  .qr-frame {
    display: flex;
    justify-content: center;
    margin: 0.25rem 0 0.8rem;
  }

  .qr-frame :global(img),
  .qr-frame :global(canvas) {
    border: 1px solid var(--border-input);
    border-radius: 0.4rem;
  }

  .url-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    max-height: 7.2rem;
    overflow-y: auto;
  }

  .passphrase-row {
    display: grid;
    grid-template-columns: auto 1fr 2.2rem;
    align-items: center;
    min-width: 0;
    margin-bottom: 0.55rem;
    border: 1.5px solid var(--border-input);
    border-radius: 0.35rem;
    color: var(--foreground-alt);
    font-size: 0.76rem;
  }

  .passphrase-row > span {
    padding-left: 0.6rem;
  }

  .passphrase-row code {
    overflow: hidden;
    padding: 0.45rem 0.5rem;
    color: var(--foreground);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.84rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-align: center;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .url-row {
    display: flex;
    align-items: center;
    min-width: 0;
    border: 1.5px solid var(--border-input);
    border-radius: 0.35rem;
    background: var(--background);
  }

  .url-row.selected {
    border-color: #534deb;
    box-shadow: 0 0 0 1px rgba(83, 77, 235, 0.12);
  }

  .url-select {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    padding: 0.5rem 0.6rem;
    color: var(--foreground);
    text-align: left;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .copy-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.2rem;
    height: 2.2rem;
    flex: 0 0 auto;
    color: var(--foreground-alt);
    border-left: 1px solid var(--border-input);
  }

  .url-select:hover,
  .copy-button:hover {
    background: var(--muted);
  }

  .error-message {
    margin: 0.65rem 0 0;
    color: #b42318;
    font-size: 0.78rem;
  }

  .dialog-actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.55rem;
    margin-top: 0.9rem;
  }

  .dialog-actions a,
  .done-button {
    box-sizing: border-box;
    border: 1.5px solid #dfe2e9;
    border-radius: 0.25rem;
    padding: 0.38rem 0.7rem;
    color: #6b7280;
    font-size: 0.82rem;
    line-height: 1;
    text-decoration: none;
  }

  .dialog-actions a:hover,
  .done-button:hover {
    background: #f5f6f8;
  }

  @media (max-height: 570px) {
    .qr-frame :global(img),
    .qr-frame :global(canvas) {
      width: 96px !important;
      height: 96px !important;
    }

    .warning {
      margin-bottom: 0.45rem;
    }
  }
</style>
