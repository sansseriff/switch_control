import type { SwitchState } from "./types";
import { reset } from "./api";

class Tree{

   st: SwitchState = $state({
        R1: false,
        R2: false,
        R3: false,
        R4: false,
        R5: false,
        R6: false,
        R7: false,
      });

  constructor() {
  }

  resetTree() {
    reset().then((ss: SwitchState) => {
      console.log("new state: ", ss);
      tree.st = ss;
    });
  }
}


export const tree = new Tree();