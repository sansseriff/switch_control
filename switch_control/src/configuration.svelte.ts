import type { ButtonLabelState } from "./types";
import { updateButtonLabels, updateSettings, type InitializationResponse } from "./api";
import { tree } from "./tree_state.svelte";

class Configuration {
  // Persisted UI configuration
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

  // Title shown at the top of the UI
  title_label: string = $state("Title Here");

  // Editing mode for configuration (labels/title)
  is_editing: boolean = $state(false);

  hydrateFromInitialize(resp: InitializationResponse) {
    if (resp.button_labels) this.button_labels = resp.button_labels;
    if (resp.settings?.title_label !== undefined) {
      this.title_label = resp.settings.title_label ?? "Title Here";
    }
  }

  async saveLabels(labels: ButtonLabelState) {
    const saved = await updateButtonLabels(labels);
    this.button_labels = saved;
  }

  // Save title alongside current tree settings (cryo voltages, etc.)
  async saveTitle() {
    // Compose a settings payload using current tree settings plus title
    const payload: any = {
      cryo_mode: tree.cryo_mode,
      cryo_voltage: tree.cryo_voltage,
      regular_voltage: tree.regular_voltage,
      tree_memory_mode: tree.tree_memory_mode,
      title_label: this.title_label,
    };
    const saved = await updateSettings(payload);
    // If backend echoes back the title, keep in sync
    if ((saved as any)?.title_label !== undefined) {
      this.title_label = (saved as any).title_label;
    }
  }

  // Convenience method to save everything together
  async saveAll(labels: ButtonLabelState) {
    await Promise.all([this.saveLabels(labels), this.saveTitle()]);
  }
}

export const config = new Configuration();
