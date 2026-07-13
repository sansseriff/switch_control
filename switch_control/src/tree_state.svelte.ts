import type { Settings, TreeState, Verification } from "./types";
import { appState, runtime, waitForInitialState } from "./sync.svelte";

const defaultTree: TreeState = {
  R1: { pos: false, color: false },
  R2: { pos: false, color: false },
  R3: { pos: false, color: false },
  R4: { pos: false, color: false },
  R5: { pos: false, color: false },
  R6: { pos: false, color: false },
  R7: { pos: false, color: false },
  activated_channel: 0,
};

const defaultSettings: Settings = {
  cryo_mode: false,
  cryo_voltage: 2.5,
  regular_voltage: 5.0,
  tree_memory_mode: false,
  title_label: "Title Here",
  pulse_generator_kind: "dev",
  pulse_generator_ip: null,
};

class Tree {
  get st(): TreeState {
    return appState.tree_state ?? defaultTree;
  }

  get settings(): Settings {
    return appState.settings ?? defaultSettings;
  }

  get cryo_mode() { return this.settings.cryo_mode; }
  get tree_memory_mode() { return this.settings.tree_memory_mode; }
  get cryo_voltage() { return this.settings.cryo_voltage; }
  get regular_voltage() { return this.settings.regular_voltage; }

  get button_colors(): boolean[] {
    return Array.from(
      { length: 8 },
      (_, index) => index === this.st.activated_channel,
    );
  }

  init() {
    return waitForInitialState();
  }

  async resetTree(verification: Verification) {
    await runtime.sendCommand("reset_tree", { verification });
  }

  async reAssertTree(verification: Verification) {
    await runtime.sendCommand("re_assert_tree", { verification });
  }

  async toggle(key: string, verification: Verification) {
    await runtime.sendCommand("toggle_switch", {
      number: Number.parseInt(key.slice(1), 10),
      verification,
    });
  }

  async toChannel(number: number, verification: Verification) {
    await runtime.sendCommand("request_channel", { number, verification });
  }

  async preemptiveAmpShutoff() {
    await runtime.sendCommand("preemptive_amp_shutoff");
  }

  async saveSettings(changes: Partial<Settings> = {}) {
    await runtime.sendCommand("update_settings", {
      settings: { ...this.settings, ...changes },
    });
  }
}

export const tree = new Tree();
