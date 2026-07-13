<script lang="ts">
  import { Dialog } from "bits-ui";
  import type { AccessInvite } from "lab-link/auth";
  import { AuthError } from "lab-link/auth";
  import {
    ArrowClockwiseIcon,
    CheckIcon,
    CopyIcon,
    XIcon,
  } from "phosphor-svelte";
  import QrCode from "svelte-qrcode";
  import { appState, authClient, runtime } from "../sync.svelte";
  import "../dialog.css";

  interface Props {
    isOpen: boolean;
  }

  interface ServerInfo {
    hostname: string;
    ipaddr: string;
    ipaddrs: string[];
    port: number;
  }

  let { isOpen = $bindable() }: Props = $props();
  let urls = $state<string[]>([]);
  let selected = $state(0);
  let invite = $state<AccessInvite | null>(null);
  let isLoading = $state(false);
  let error = $state("");
  let copiedValue = $state("");
  let needsSetup = $state(false);
  let setupPassphrase = $state("");
  let setupConfirmation = $state("");
  let visiblePassphrase = $state("");
  let changingPassphrase = $state(false);
  let replacementPassphrase = $state("");
  let replacementConfirmation = $state("");
  let wasOpen = false;

  const accessUrl = $derived(urls[selected] ?? "");
  const lifecycleStatus = $derived.by(() => {
    if (!invite) return "idle";
    if (appState.remote_access?.invite_id === invite.id) {
      return appState.remote_access.invite_status;
    }
    return invite.status;
  });
  const accessIsActive = $derived(lifecycleStatus === "active");

  $effect(() => {
    if (isOpen && !wasOpen) void loadRemoteAccess();
    if (!isOpen && wasOpen) {
      setupPassphrase = "";
      setupConfirmation = "";
      visiblePassphrase = "";
      changingPassphrase = false;
      replacementPassphrase = "";
      replacementConfirmation = "";
    }
    wasOpen = isOpen;
  });

  async function loadRemoteAccess() {
    isLoading = true;
    error = "";
    copiedValue = "";
    try {
      const status = await authClient.status();
      needsSetup = !status.configured;
      if (needsSetup) {
        urls = [];
        invite = null;
        return;
      }
      if (
        !status.authorized ||
        !status.principal?.capabilities.some(
          (capability) => capability === "*" || capability === "manage_access",
        )
      ) {
        throw new Error(
          "This device can control the switches but cannot manage remote access.",
        );
      }
      await issueInvite();
    } catch (cause) {
      urls = [];
      invite = null;
      error = authMessage(cause);
    } finally {
      isLoading = false;
    }
  }

  async function issueInvite() {
    isLoading = true;
    error = "";
    copiedValue = "";
    try {
      if (invite && accessIsActive) {
        await authClient.revokeInvite(invite.id).catch(() => undefined);
      }
      const [serverAck, newInvite] = await Promise.all([
        runtime.sendCommand<ServerInfo>("get_server_info"),
        authClient.createInvite(5 * 60),
      ]);
      if (!serverAck.result) {
        await authClient.revokeInvite(newInvite.id).catch(() => undefined);
        throw new Error("The server returned no network information.");
      }
      const addresses = serverAck.result.ipaddrs?.length
        ? serverAck.result.ipaddrs
        : [serverAck.result.ipaddr];
      invite = newInvite;
      urls = addresses.map(
        (ipaddr) =>
          `http://${ipaddr}:${serverAck.result!.port}/#invite=${encodeURIComponent(newInvite.token)}`,
      );
      selected = 0;
      if (addresses.every((ipaddr) => ipaddr.startsWith("127."))) {
        error =
          "No network address was found. Connect this computer to the same network as the remote device.";
      }
    } catch (cause) {
      urls = [];
      invite = null;
      error = authMessage(cause);
    } finally {
      isLoading = false;
    }
  }

  async function completeSetup() {
    error = "";
    if (setupPassphrase.length < 12) {
      error = "Choose a master passphrase containing at least 12 characters.";
      return;
    }
    if (setupPassphrase !== setupConfirmation) {
      error = "The two passphrases do not match.";
      return;
    }
    isLoading = true;
    try {
      await authClient.setup(setupPassphrase, {
        remember: true,
        deviceName: "Switch Control host",
      });
      visiblePassphrase = setupPassphrase;
      setupPassphrase = "";
      setupConfirmation = "";
      needsSetup = false;
      await issueInvite();
    } catch (cause) {
      error = authMessage(cause);
    } finally {
      isLoading = false;
    }
  }

  async function changeMasterPassphrase() {
    error = "";
    if (replacementPassphrase.length < 12) {
      error = "Choose a master passphrase containing at least 12 characters.";
      return;
    }
    if (replacementPassphrase !== replacementConfirmation) {
      error = "The two passphrases do not match.";
      return;
    }
    isLoading = true;
    try {
      await authClient.changePassphrase(replacementPassphrase, true, true);
      visiblePassphrase = replacementPassphrase;
      replacementPassphrase = "";
      replacementConfirmation = "";
      changingPassphrase = false;
      urls = [];
      invite = null;
    } catch (cause) {
      error = authMessage(cause);
    } finally {
      isLoading = false;
    }
  }

  function authMessage(cause: unknown) {
    if (cause instanceof AuthError) return cause.message;
    return cause instanceof Error
      ? cause.message
      : "Could not prepare remote access.";
  }

  async function copyValue(value: string) {
    if (!value || (value.startsWith("http") && !accessIsActive)) return;
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
      copiedValue = value;
      window.setTimeout(() => {
        if (copiedValue === value) copiedValue = "";
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
        Connect a phone, tablet, or another computer on the same network.
      </Dialog.Description>

      {#if needsSetup && !isLoading}
        <div class="setup-panel">
          <h3>Choose a master passphrase</h3>
          <p>
            This is the recovery credential for remote access. It remains valid
            across restarts until you change it. Save it in your password
            manager or another safe place.
          </p>
          <label>
            Master passphrase
            <input
              type="password"
              autocomplete="new-password"
              bind:value={setupPassphrase}
              minlength="12"
            />
          </label>
          <label>
            Confirm passphrase
            <input
              type="password"
              autocomplete="new-password"
              bind:value={setupConfirmation}
              minlength="12"
              onkeydown={(event) => {
                if (event.key === "Enter") void completeSetup();
              }}
            />
          </label>
          <button type="button" class="primary-button" onclick={completeSetup}
            >Set up remote access</button
          >
        </div>
      {:else}
        <div class="warning" role="note">
          Each QR code or copied address works once and expires after five
          minutes. The master passphrase can always be used for manual login.
          This HTTP connection is not encrypted, so use it only on a trusted
          network.
        </div>

        {#if visiblePassphrase}
          <div class="passphrase-notice" role="status">
            <span>
              Save this master passphrase now. For security, it cannot be shown
              again.
            </span>
            <code>{visiblePassphrase}</code>
            <button
              type="button"
              class="copy-button"
              onclick={() => copyValue(visiblePassphrase)}
              aria-label="Copy master passphrase"
              title="Copy master passphrase"
            >
              {#if copiedValue === visiblePassphrase}
                <CheckIcon size={18} />
              {:else}
                <CopyIcon size={18} />
              {/if}
            </button>
          </div>
        {/if}

        {#if changingPassphrase}
          <div class="setup-panel change-panel">
            <h3>Change master passphrase</h3>
            <p>
              This signs out remembered devices and revokes active access links.
              Save the replacement before closing this window.
            </p>
            <label>
              New passphrase
              <input
                type="password"
                autocomplete="new-password"
                bind:value={replacementPassphrase}
                minlength="12"
              />
            </label>
            <label>
              Confirm new passphrase
              <input
                type="password"
                autocomplete="new-password"
                bind:value={replacementConfirmation}
                minlength="12"
                onkeydown={(event) => {
                  if (event.key === "Enter") void changeMasterPassphrase();
                }}
              />
            </label>
            <div class="change-actions">
              <button type="button" onclick={() => (changingPassphrase = false)}
                >Cancel</button
              >
              <button
                type="button"
                class="primary-button"
                onclick={changeMasterPassphrase}>Change passphrase</button
              >
            </div>
          </div>
        {/if}

        {#if isLoading && !changingPassphrase}
          <div class="status">Issuing a remote-access link…</div>
        {:else if accessUrl}
          <div class:inactive={!accessIsActive} class="access-layout">
            <div class="qr-column">
              <div class="qr-frame">
                <QrCode
                  value={accessUrl}
                  size={152}
                  padding={0}
                  errorCorrection="M"
                />
              </div>
              <span>
                {accessIsActive
                  ? "Scan the selected address"
                  : `This link is ${lifecycleStatus}`}
              </span>
            </div>

            <div class="access-details">
              <p class="passphrase-help">
                Manual login uses the persistent master passphrase. It is stored
                only as a hash and cannot be displayed here.
              </p>
              <div class="url-list" aria-label="Available remote addresses">
                {#each urls as url, index (url)}
                  <div class="url-row" class:selected={selected === index}>
                    <button
                      type="button"
                      class="url-select"
                      onclick={() => (selected = index)}
                      aria-pressed={selected === index}
                      disabled={!accessIsActive}
                      title="Show QR code for this address"
                    >
                      {url}
                    </button>
                    <button
                      type="button"
                      class="copy-button"
                      onclick={() => copyValue(url)}
                      disabled={!accessIsActive}
                      aria-label={`Copy ${url}`}
                      title="Copy address"
                    >
                      {#if copiedValue === url}
                        <CheckIcon size={18} />
                      {:else}
                        <CopyIcon size={18} />
                      {/if}
                    </button>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
      {/if}

      {#if error}
        <p class="error-message" role="alert">{error}</p>
      {/if}

      <div class="dialog-actions">
        {#if !needsSetup && !changingPassphrase}
          <button
            type="button"
            class="change-button"
            onclick={() => (changingPassphrase = true)}
            >Change master passphrase</button
          >
        {/if}
        {#if !needsSetup && !changingPassphrase}
          <button
            type="button"
            class="refresh-button"
            onclick={issueInvite}
            disabled={isLoading}
            title="Issue a new five-minute access link"
          >
            <ArrowClockwiseIcon size={16} />
            {isLoading ? "Issuing…" : "New access link"}
          </button>
          {#if accessUrl && accessIsActive}
            <a href={accessUrl} target="_blank" rel="noreferrer">Open address</a
            >
          {/if}
        {/if}
        <button
          type="button"
          class="done-button"
          onclick={() => (isOpen = false)}
        >
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
  :global([data-dialog-content].remote-dialog) {
    width: min(720px, calc(100vw - 2rem));
    max-width: min(720px, calc(100vw - 2rem));
  }

  .warning,
  .passphrase-notice {
    margin-bottom: 0.8rem;
    border: 1px solid #f2d29a;
    border-radius: 0.35rem;
    background: #fff8e8;
    color: #76551d;
    padding: 0.55rem 0.65rem;
    font-size: 0.78rem;
    line-height: 1.35;
  }

  .passphrase-notice {
    display: grid;
    grid-template-columns: 1fr auto 2.2rem;
    align-items: center;
    gap: 0.6rem;
  }

  .passphrase-notice code {
    color: var(--foreground);
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
  }

  .setup-panel {
    display: grid;
    gap: 0.7rem;
    margin-top: 0.9rem;
    border: 1px solid var(--border-input);
    border-radius: 0.45rem;
    padding: 1rem;
  }

  .setup-panel h3,
  .setup-panel p {
    margin: 0;
  }

  .setup-panel p,
  .passphrase-help {
    color: var(--foreground-alt);
    font-size: 0.78rem;
    line-height: 1.4;
  }

  .setup-panel label {
    display: grid;
    gap: 0.3rem;
    color: var(--foreground-alt);
    font-size: 0.78rem;
    font-weight: 600;
  }

  .setup-panel input {
    box-sizing: border-box;
    width: 100%;
    border: 1.5px solid var(--border-input);
    border-radius: 0.3rem;
    padding: 0.55rem 0.6rem;
    font: inherit;
  }

  .primary-button {
    justify-self: end;
    border-radius: 0.3rem;
    background: #534deb;
    color: white;
    padding: 0.52rem 0.75rem;
  }

  .change-panel {
    margin-bottom: 0.8rem;
  }

  .change-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }

  .change-actions button {
    border: 1.5px solid #dfe2e9;
    border-radius: 0.3rem;
    padding: 0.52rem 0.75rem;
  }

  .change-actions .primary-button {
    border-color: #534deb;
  }

  .status {
    display: flex;
    min-height: 10rem;
    align-items: center;
    justify-content: center;
    color: var(--foreground-alt);
    font-size: 0.875rem;
  }

  .access-layout {
    display: grid;
    grid-template-columns: 170px minmax(0, 1fr);
    align-items: center;
    gap: 1rem;
    min-width: 0;
  }

  .access-layout.inactive .qr-frame,
  .access-layout.inactive .url-list {
    filter: grayscale(1);
    opacity: 0.35;
  }

  .qr-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
  }

  .qr-column > span {
    color: var(--foreground-alt);
    font-size: 0.72rem;
  }

  .qr-frame {
    box-sizing: content-box;
    width: 152px;
    height: 152px;
    overflow: hidden;
    border: 8px solid white;
    border-radius: 0.4rem;
    outline: 1px solid var(--border-input);
    background: white;
  }

  .qr-frame :global(img) {
    display: block;
    width: 152px;
    height: 152px;
  }

  .access-details {
    min-width: 0;
  }

  .passphrase-help {
    margin: 0 0 0.55rem;
  }

  .url-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    max-height: 7.2rem;
    overflow-y: auto;
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

  .url-select:hover:not(:disabled),
  .copy-button:hover:not(:disabled) {
    background: var(--muted);
  }

  button:disabled {
    cursor: not-allowed;
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
  .change-button,
  .refresh-button,
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

  .refresh-button {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    margin-right: auto;
  }

  .dialog-actions a:hover,
  .change-button:hover,
  .refresh-button:hover:not(:disabled),
  .done-button:hover {
    background: #f5f6f8;
  }

  .refresh-button:disabled {
    cursor: wait;
    opacity: 0.55;
  }

  .change-button {
    margin-right: auto;
  }

  .change-button + .refresh-button {
    margin-right: 0;
  }

  @media (max-width: 580px) {
    .access-layout {
      grid-template-columns: 1fr;
    }

    .qr-column > span {
      display: none;
    }

    .passphrase-notice {
      grid-template-columns: 1fr 2.2rem;
    }

    .passphrase-notice > span {
      grid-column: 1 / -1;
    }
  }

  @media (max-height: 570px) {
    .warning {
      margin-bottom: 0.45rem;
    }
  }
</style>
