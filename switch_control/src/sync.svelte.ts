import { createSyncRuntime, useSyncState } from "lab-link/svelte";
import type { AppState } from "./types";

function websocketUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const isLocalDevServer = ["5173", "1420"].includes(window.location.port);
  const host = isLocalDevServer
    ? `${window.location.hostname || "localhost"}:8854`
    : window.location.host;
  return `${protocol}//${host}/sync/ws`;
}

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
