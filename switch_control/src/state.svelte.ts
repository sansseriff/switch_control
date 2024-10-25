import type { SwitchState } from "./types";
import { reset, flipSwitch } from "./api";

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

  toggle(key: string) {
    // key is "R1", "R2", etc.
    // convert to idx
    let idx = parseInt(key.slice(1));

    flipSwitch({ number: idx }).then((ss: SwitchState) => {
      console.log("new state: ", ss);
      tree.st = ss;
    });
    tree.st[key] = !tree.st[key];
  }
}


export const tree = new Tree();