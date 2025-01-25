


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
