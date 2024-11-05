import type { TreeState, SwitchState } from "./types";
import { reset, flipSwitch, reAssert, requestChannel } from "./api";

class Tree{

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

  resetTree() {
    reset().then((ss: TreeState) => {
      this.st = ss;
    });
  }

  reAssertTree() {
    reAssert().then((ss: TreeState) => {
      this.st = ss;
    });
  }

  toggle(key: string) {
    // key is "R1", "R2", etc.
    // convert to idx
    let idx = parseInt(key.slice(1));

    flipSwitch({ number: idx }).then((ss: TreeState) => {
      // console.log("new state: ", ss);
      // console.log("ss actiavted ", ss.activated_channel)
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

  toChannel(idx: number) {
    requestChannel({ number: idx }).then((ss: TreeState) => {
      tree.st = ss;
      // console.log("ss actiavted ", ss.activated_channel)
      this.updateButtons();
    });
  }
}


export const tree = new Tree();