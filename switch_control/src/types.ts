


export interface ButtonState {
    name: string;
    proxy_name: string;
    idx: number;
    value: boolean;
  }


// let switch_state = {
//     R1: true,
//     R2: true,
//     R3: true,
//     R4: true,
//     R5: true,
//     R6: true,
//     R7: true,
//   };

export interface SwitchState {
    [key: string]: boolean;
    R1: boolean;
    R2: boolean;
    R3: boolean;
    R4: boolean;
    R5: boolean;
    R6: boolean;
    R7: boolean;
  }
