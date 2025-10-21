import type { TreeState, SwitchState } from "./types";
import { reset, flipSwitch, reAssert, requestChannel, preemptiveAmpShutoff, updateSettings, initialize } from "./api";
import type { Verification } from "./types";
import type { InitializationResponse } from "./api";

class Tree {
  st: TreeState = $state({
    R1: { pos: false, color: false },
    R2: { pos: false, color: false },
    R3: { pos: false, color: false },
    R4: { pos: false, color: false },
    R5: { pos: false, color: false },
    R6: { pos: false, color: false },
    R7: { pos: false, color: false },
    activated_channel: 0,
  });

  button_colors = $state([false, false, false, false, false, false, false, false]);

  // settings
  cryo_mode: boolean = $state(false);
  tree_memory_mode: boolean = $state(false);
  cryo_voltage: number = $state(2.0);
  regular_voltage: number = $state(2.0);

  // UI editing state has been moved to configuration store

  constructor() {}

  // Initialize tree state and settings (labels/title handled by configuration)
  init() {
    return initialize().then((response: InitializationResponse) => {
      this.st = response.tree_state;
      // Initialize settings
      if (response.settings) {
        this.cryo_mode = response.settings.cryo_mode;
        this.cryo_voltage = response.settings.cryo_voltage;
        this.regular_voltage = response.settings.regular_voltage;
        this.tree_memory_mode = response.settings.tree_memory_mode;
      }
      this.updateButtons();
      return response; // caller may pass to configuration.hydrateFromInitialize
    });
  }

  resetTree(verification: Verification) {
    reset(verification).then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
    });
  }

  reAssertTree(verification: Verification) {
    reAssert(verification).then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
    });
  }

  toggle(key: string, verification: Verification) {
    // key is "R1", "R2", etc.
    // convert to idx
    let idx = parseInt(key.slice(1));

    flipSwitch({
      number: idx,
      verification: verification,
    }).then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
    });
  }

  updateButtons() {
    this.button_colors = this.button_colors.map(() => false);
    if (this.st.activated_channel >= 0 && this.st.activated_channel < this.button_colors.length) {
      this.button_colors[this.st.activated_channel] = true;
    }
  }

  toChannel(idx: number, verification: Verification) {
    requestChannel({
      number: idx,
      verification: verification,
    }).then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
    });
  }

  preemptiveAmpShutoff() {
    preemptiveAmpShutoff();
  }

  // Save settings to backend and update local state
  saveSettings() {
    const payload = {
      cryo_mode: this.cryo_mode,
      cryo_voltage: this.cryo_voltage,
      regular_voltage: this.regular_voltage,
      tree_memory_mode: this.tree_memory_mode,
    };
    updateSettings(payload)
      .then((saved) => {
        this.cryo_mode = saved.cryo_mode;
        this.cryo_voltage = saved.cryo_voltage;
        this.regular_voltage = saved.regular_voltage;
      })
      .catch((error) => {
        console.error("Failed to save settings:", error);
      });
  }
}

export const tree = new Tree();
