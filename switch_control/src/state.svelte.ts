import type { TreeState, SwitchState } from "./types";
import { reset, flipSwitch, reAssert } from "./api";

class Tree{

   st: TreeState = $state({
        R1: { pos: false, color: false },
        R2: { pos: false, color: false },
        R3: { pos: false, color: false },
        R4: { pos: false, color: false },
        R5: { pos: false, color: false },
        R6: { pos: false, color: false },
        R7: { pos: false, color: false },
      });

  constructor() {
  }

  resetTree() {
    reset().then((ss: TreeState) => {
      tree.st = ss;
    });
  }

  reAssertTree() {
    reAssert().then((ss: TreeState) => {
      tree.st = ss;
    });
  }

  toggle(key: string) {
    // key is "R1", "R2", etc.
    // convert to idx
    let idx = parseInt(key.slice(1));

    flipSwitch({ number: idx }).then((ss: TreeState) => {
      // console.log("new state: ", ss);
      tree.st = ss;
    });
    tree.st[key].pos = !tree.st[key].pos;
  }
}


export const tree = new Tree();