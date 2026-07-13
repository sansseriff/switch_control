import type { ButtonLabelState } from "./types";
import { appState, runtime } from "./sync.svelte";

const defaultLabels: ButtonLabelState = {
  label_0: "Ch 1",
  label_1: "Ch 2",
  label_2: "Ch 3",
  label_3: "Ch 4",
  label_4: "Ch 5",
  label_5: "Ch 6",
  label_6: "Ch 7",
  label_7: "Ch 8",
};

class Configuration {
  is_editing = $state(false);

  get button_labels(): ButtonLabelState {
    return appState.button_labels ?? defaultLabels;
  }

  get title_label(): string {
    return appState.settings?.title_label ?? "Title Here";
  }

  async saveAll(labels: ButtonLabelState, titleLabel: string) {
    await runtime.sendCommand("update_configuration", {
      labels,
      title_label: titleLabel,
    });
  }
}

export const config = new Configuration();
