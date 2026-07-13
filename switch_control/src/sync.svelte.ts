import { AuthClient } from "lab-link/auth";
import { createSyncRuntime, useSyncState } from "lab-link/svelte";
import type { AppState } from "./types";

export function serverBaseUrl() {
  return window.location.origin;
}

function websocketUrl() {
  const base = new URL(serverBaseUrl());
  const protocol = base.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${base.host}/sync/ws`;
}

export const authClient = new AuthClient({ baseUrl: serverBaseUrl() });

export const runtime = createSyncRuntime<AppState>({
  url: websocketUrl(),
  commandTimeoutMs: 60_000,
});

export const appState = useSyncState<AppState>(runtime);

let initialSnapshot: Promise<AppState> | undefined;

export function waitForInitialState(): Promise<AppState> {
  const snapshot = runtime.snapshot();
  if (snapshot) return Promise.resolve(snapshot);
  if (!initialSnapshot) {
    initialSnapshot = new Promise((resolve) => {
      const unsubscribe = runtime.onSnapshot(({ data }) => {
        unsubscribe();
        resolve(data);
      });
    });
  }
  return initialSnapshot;
}
