export interface ButtonState {
  name: string;
  proxy_name: string;
  idx: number;
  value: boolean;
  default_name: string;
}

export interface Verification {
  verified: boolean;
  timestamp: number;
  userConfirmed: boolean;
}

export interface SwitchState {
  pos: boolean;
  color: boolean;
}

export interface TreeState {
  [key: string]: SwitchState | number;
  R1: SwitchState;
  R2: SwitchState;
  R3: SwitchState;
  R4: SwitchState;
  R5: SwitchState;
  R6: SwitchState;
  R7: SwitchState;
  activated_channel: number;
}

export interface ButtonLabelState {
  label_0: string;
  label_1: string;
  label_2: string;
  label_3: string;
  label_4: string;
  label_5: string;
  label_6: string;
  label_7: string;
}

export interface ButtonState {
  name: string;
  proxy_name: string;
  default_name: string;
  idx: number;
  value: boolean;
}

// Backend settings model
export interface Settings {
  cryo_mode: boolean;
  cryo_voltage: number;
  regular_voltage: number;
  tree_memory_mode: boolean;
}
