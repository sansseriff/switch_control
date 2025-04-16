import type { TreeState, SwitchState } from "./types";
import { reset, flipSwitch, reAssert, requestChannel } from "./api";
import type { Verification } from "./types";
import { initialize } from "./api";

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

  button_colors = $state([false, false, false, false, false, false, false, false]);

  constructor() {
  }

  init() {
    initialize().then((ss: TreeState) => {
      this.st = ss;
      this.updateButtons();
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
    this.button_colors[this.st.activated_channel] = true;
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
}

export const tree = new Tree();