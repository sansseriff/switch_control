import type { TreeState, SwitchState, ButtonLabelState } from "./types"; // Import ButtonLabelState
import { reset, flipSwitch, reAssert, requestChannel, updateButtonLabels, preemptiveAmpShutoff, updateSettings } from "./api"; // Import updateButtonLabels
import type { Verification } from "./types";
import { initialize } from "./api";
import type { InitializationResponse } from "./api"; // Import InitializationResponse

class Tree {

  st: TreeState = $state({
    R1: { pos: false, color: false },
    R2: { pos: false, color: false },
    R3: { pos: false, color: false },
    R4: { pos: false, color: false },
    R5: { pos: false, color: false },
    R6: { pos: false, color: false },
    R7: { pos: false, color: false },
    activated_channel: 0
  });

  // Add state for button labels
  button_labels: ButtonLabelState = $state({
    label_0: "Ch 1",
    label_1: "Ch 2",
    label_2: "Ch 3",
    label_3: "Ch 4",
    label_4: "Ch 5",
    label_5: "Ch 6",
    label_6: "Ch 7",
    label_7: "Ch 8",
  });

  button_colors = $state([false, false, false, false, false, false, false, false]);

  // settings
  cryo_mode: boolean = $state(false);
  tree_memory_mode: boolean = $state(false);
  cryo_voltage: number = $state(2.0);
  regular_voltage: number = $state(2.0);

  constructor() {
  }

  // Update init to handle the combined response
  init() {
    return initialize().then((response: InitializationResponse) => {
      this.st = response.tree_state;
      this.button_labels = response.button_labels; // Store labels
      // Initialize settings
      if (response.settings) {
        this.cryo_mode = response.settings.cryo_mode;
        this.cryo_voltage = response.settings.cryo_voltage;
        this.regular_voltage = response.settings.regular_voltage;
        this.tree_memory_mode = response.settings.tree_memory_mode;
      }

      console.log("Initialized with settings:", {
        cryo_mode: this.cryo_mode,
        cryo_voltage: this.cryo_voltage,
        regular_voltage: this.regular_voltage,
        tree_memory_mode: this.tree_memory_mode
      });
      this.updateButtons();
      return response; // Return the full response if needed
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
      verification: verification
    }).then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
    });
    // this.st[key].pos = !tree.st[key].pos;
    // update buttons can't go here because it will be called before the state is updated
  }

  updateButtons() {
    this.button_colors = this.button_colors.map((color) => false);
    // console.log(this.st.activated_channel)
    // Ensure activated_channel is within bounds before highlighting
    if (this.st.activated_channel >= 0 && this.st.activated_channel < this.button_colors.length) {
      this.button_colors[this.st.activated_channel] = true;
    } else {
      console.warn("Activated channel index out of bounds:", this.st.activated_channel);
    }
    // console.log("after updating: ", this.st.activated_channel)
    // $state.snapshot(this.button_colors)
    // console.log(this.button_colors)
  }

  toChannel(idx: number, verification: Verification) {
    requestChannel({
      number: idx,
      verification: verification
    }).then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
    });
  }

  preemptiveAmpShutoff() {
    preemptiveAmpShutoff()
  }

  // Add method to save button labels
  saveButtonLabels(labels: ButtonLabelState) {
    updateButtonLabels(labels).then((savedLabels: ButtonLabelState) => {
      this.button_labels = savedLabels; // Update state with saved labels from response
      console.log("Button labels saved successfully.");
    }).catch(error => {
      console.error("Failed to save button labels:", error);
      // Optionally revert changes or show an error message to the user
    });
  }

  // Save settings to backend and update local state
  saveSettings() {
    const payload = {
      cryo_mode: this.cryo_mode,
      cryo_voltage: this.cryo_voltage,
      regular_voltage: this.regular_voltage,
      tree_memory_mode: this.tree_memory_mode
    };
    updateSettings(payload).then((saved) => {
      this.cryo_mode = saved.cryo_mode;
      this.cryo_voltage = saved.cryo_voltage;
      this.regular_voltage = saved.regular_voltage;
      console.log("Settings saved successfully.");
    }).catch((error) => {
      console.error("Failed to save settings:", error);
    });
  }
}

export const tree = new Tree();