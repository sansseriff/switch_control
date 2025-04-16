<script lang="ts">
  import { Tween } from "svelte/motion";
  import { cubicInOut } from "svelte/easing";
  import type { TreeState } from "../types";
  import TreeSwitchOverlay from "./TreeSwitchOverlay.svelte";

  interface Props {
    tree_state: TreeState;
  }

  let { tree_state }: Props = $props();

  const tweens = Array.from(
    { length: 7 },
    () => new Tween(1, { duration: 300, easing: cubicInOut }),
  );

  const colors = $state(Array.from({ length: 7 }, () => "black"));

  let tweenR1 = tweens[0];
  let tweenR2 = tweens[1];
  let tweenR3 = tweens[2];
  let tweenR4 = tweens[3];
  let tweenR5 = tweens[4];
  let tweenR6 = tweens[5];
  let tweenR7 = tweens[6];

  let colorR1 = $derived(colors[0]);
  let colorR2 = $derived(colors[1]);
  let colorR3 = $derived(colors[2]);
  let colorR4 = $derived(colors[3]);
  let colorR5 = $derived(colors[4]);
  let colorR6 = $derived(colors[5]);
  let colorR7 = $derived(colors[6]);

  let showOverlay = $state(false); // State to track visibility of the overlay
  let overlayPosition = $state({ top: 0, left: 0 }); // State to track position of the overlay
  let switch_name = $state("R1");

  function updateScale(tree_state: TreeState) {
    // const state = buttons_state[3].value; // Assuming idx 3 corresponds to R4_top
    Object.entries(tree_state).forEach(([key, value], index) => {
      if (index < tweens.length) {
        tweens[index].target = value.pos ? -1 : 1;
      }

      if (index < colors.length) {
        if (value.color) {
          colors[index] = "#534deb";
        } else {
          colors[index] = "black";
        }
      }
    });
  }

  $effect(() => {
    updateScale(tree_state);
  });

  function handleMouseEnter(event, switchId: number) {
    showOverlay = true;
    const rect = event.target.getBoundingClientRect();
    overlayPosition = {
      top: rect.top + window.scrollY,
      left: rect.left + window.scrollX,
    };
    console.log("setting overlay switchId", switchId);
    switch_name = `R${switchId}`; // Example switch name
    console.log("setting overlay switch_name", switch_name);
  }

  function handleMouseLeave(event) {
    if (
      !event.relatedTarget ||
      (!event.relatedTarget.closest(".pos") &&
        !event.relatedTarget.closest("circle"))
    ) {
      showOverlay = false;
    }
  }

  function handleFigureMouseLeave(event) {
    if (
      !event.relatedTarget ||
      (!event.relatedTarget.closest(".pos") &&
        !event.relatedTarget.closest("circle"))
    ) {
      showOverlay = false;
    }
  }

  function handleOverlayMouseEnter() {
    showOverlay = true;
  }

  function handleOverlayMouseLeave(event) {
    if (
      !event.relatedTarget ||
      (!event.relatedTarget.closest(".pos") &&
        !event.relatedTarget.closest("circle"))
    ) {
      showOverlay = false;
    }
  }
</script>

<svg
  role="img"
  aria-label="tree diagram"
  viewBox="0 0 681 1094"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  onmouseleave={(e) => handleFigureMouseLeave(e)}
>
  <g id="Group 36">
    <g id="Group 36_2">
      <circle
        id="Ellipse 37"
        cx="658.5"
        cy="1071.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 38"
        cx="658.5"
        cy="922.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 39"
        cx="658.5"
        cy="772.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 40"
        cx="658.5"
        cy="622.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 41"
        cx="658.5"
        cy="472.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 42"
        cx="658.5"
        cy="322.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 46"
        cx="470.5"
        cy="97.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 47"
        cx="470.5"
        cy="397.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 48"
        cx="470.5"
        cy="697.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 50"
        cx="282.5"
        cy="847.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 51"
        cx="282.5"
        cy="247.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 52"
        cx="94.5"
        cy="547.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 49"
        cx="470.5"
        cy="997.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 43"
        cx="658.5"
        cy="172.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
      <circle
        id="Ellipse 44"
        cx="658.5"
        cy="22.5"
        r="22"
        fill="#D9D9D9"
        stroke="#EBEBEB"
      />
    </g>
    <g id="Group 37" opacity="1">
      <path
        id="Vector 80"
        d="M94.5 548H10"
        stroke={colorR1}
        stroke-width="20"
        stroke-linecap="round"
      />
      <!-- <path id="R4_bottom" d="M471 997.5C471 1017.26 478.849 1036.21 492.821 1050.18C506.792 1064.15 525.741 1072 545.5 1072L659 1072" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R4_top"
        d="M471 997.5C471 977.741 478.849 958.792 492.821 944.821C506.792 930.849 525.741 923 545.5 923L659 923"
        stroke={colorR4}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="471px 997.5px"
        transform="scale(1, {tweenR4.current})"
      />
      <!-- <path id="R5_bottom" d="M471 697.5C471 717.259 478.849 736.208 492.821 750.179C506.792 764.151 525.741 772 545.5 772L659 772" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R5_top"
        d="M471 697.5C471 677.741 478.849 658.792 492.821 644.821C506.792 630.849 525.741 623 545.5 623L659 623"
        stroke={colorR5}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="471px 697.5px"
        transform="scale(1, {tweenR5.current})"
      />
      <!-- <path id="R6_bottom" d="M471 397.5C471 417.259 478.849 436.208 492.821 450.179C506.792 464.151 525.741 472 545.5 472L659 472" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R6_top"
        d="M471 397.5C471 377.741 478.849 358.792 492.821 344.821C506.792 330.849 525.741 323 545.5 323L659 323"
        stroke={colorR6}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="471px 397.5px"
        transform="scale(1, {tweenR6.current})"
      />
      <!-- <path id="R7_bottom" d="M471 97.5C471 117.259 478.849 136.208 492.821 150.179C506.792 164.151 525.741 172 545.5 172L659 172" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R7_top"
        d="M471 97.5C471 77.7414 478.849 58.792 492.821 44.8205C506.792 30.8491 525.741 23 545.5 23L659 23"
        stroke={colorR7}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="471px 97.5px"
        transform="scale(1, {tweenR7.current})"
      />
      <!-- <path id="R2_bottom" d="M283 848L283 924C283 943.759 290.849 962.708 304.821 976.679C318.792 990.651 337.741 998.5 357.5 998.5L471 998.5" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R2_top"
        d="M283 848L283 772.499C283 752.741 290.849 733.792 304.821 719.82C318.792 705.849 337.741 698 357.5 698L471 698"
        stroke={colorR2}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="283px 848px"
        transform="scale(1, {tweenR2.current})"
      />
      <!-- <path id="R3_bottom" d="M283 248L283 324C283 343.759 290.849 362.708 304.821 376.679C318.792 390.651 337.741 398.5 357.5 398.5L471 398.5" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R3_top"
        d="M283 248L283 172.499C283 152.741 290.849 133.792 304.821 119.82C318.792 105.849 337.741 97.9999 357.5 97.9999L471 97.9999"
        stroke={colorR3}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="283px 248px"
        transform="scale(1, {tweenR3.current})"
      />
      <!-- <path id="R1_bottom" d="M95 549.007L95 774.321C95 794.079 102.849 813.029 116.821 827C130.792 840.972 149.741 848.821 169.5 848.821L283 848.821" stroke="black" stroke-width="19" stroke-linecap="round"/> -->
      <path
        id="R1_top"
        d="M95 549.006L95 322.007C95 302.248 102.849 283.299 116.821 269.328C130.792 255.356 149.741 247.507 169.5 247.507L283 247.507"
        stroke={colorR1}
        stroke-width="19"
        stroke-linecap="round"
        transform-origin="95px 549.007px"
        transform="scale(1, {tweenR1.current})"
      />
    </g>
    <g id="Group 38" opacity="0.1">
      <path
        id="Vector 80_2"
        d="M94.5 548H10"
        stroke="black"
        stroke-width="20"
        stroke-linecap="round"
        opacity="0.1"
      />
      <path
        id="R4_bottom_2"
        d="M471 997.5C471 1017.26 478.849 1036.21 492.821 1050.18C506.792 1064.15 525.741 1072 545.5 1072L659 1072"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R4_top_2"
        d="M471 997.5C471 977.741 478.849 958.792 492.821 944.821C506.792 930.849 525.741 923 545.5 923L659 923"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R5_bottom_2"
        d="M471 697.5C471 717.259 478.849 736.208 492.821 750.179C506.792 764.151 525.741 772 545.5 772L659 772"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R5_top_2"
        d="M471 697.5C471 677.741 478.849 658.792 492.821 644.821C506.792 630.849 525.741 623 545.5 623L659 623"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R6_bottom_2"
        d="M471 397.5C471 417.259 478.849 436.208 492.821 450.179C506.792 464.151 525.741 472 545.5 472L659 472"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R6_top_2"
        d="M471 397.5C471 377.741 478.849 358.792 492.821 344.821C506.792 330.849 525.741 323 545.5 323L659 323"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R7_bottom_2"
        d="M471 97.5C471 117.259 478.849 136.208 492.821 150.179C506.792 164.151 525.741 172 545.5 172L659 172"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R7_top_2"
        d="M471 97.5C471 77.7414 478.849 58.792 492.821 44.8205C506.792 30.8491 525.741 23 545.5 23L659 23"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R2_bottom_2"
        d="M283 848L283 924C283 943.759 290.849 962.708 304.821 976.679C318.792 990.651 337.741 998.5 357.5 998.5L471 998.5"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R2_top_2"
        d="M283 848L283 772.499C283 752.741 290.849 733.792 304.821 719.82C318.792 705.849 337.741 698 357.5 698L471 698"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R3_bottom_2"
        d="M283 248L283 324C283 343.759 290.849 362.708 304.821 376.679C318.792 390.651 337.741 398.5 357.5 398.5L471 398.5"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R3_top_2"
        d="M283 248L283 172.499C283 152.741 290.849 133.792 304.821 119.82C318.792 105.849 337.741 97.9999 357.5 97.9999L471 97.9999"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R1_bottom_2"
        d="M95 549.007L95 774.321C95 794.079 102.849 813.029 116.821 827C130.792 840.972 149.741 848.821 169.5 848.821L283 848.821"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
      <path
        id="R1_top_2"
        d="M95 549.006L95 322.007C95 302.248 102.849 283.299 116.821 269.328C130.792 255.356 149.741 247.507 169.5 247.507L283 247.507"
        stroke="black"
        stroke-width="19"
        stroke-linecap="round"
      />
    </g>
  </g>
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 46"
    cx="470.5"
    cy="97.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 7)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 47"
    cx="470.5"
    cy="397.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 6)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 48"
    cx="470.5"
    cy="697.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 5)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 50"
    cx="282.5"
    cy="847.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 2)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 51"
    cx="282.5"
    cy="247.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 3)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 52"
    cx="94.5"
    cy="547.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 1)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
  <circle
    role="img"
    aria-label="sensor"
    id="Ellipse 49"
    cx="470.5"
    cy="997.5"
    r="100"
    fill="black"
    opacity="0.0"
    onmouseenter={(e) => handleMouseEnter(e, 4)}
    onmouseleave={(e) => handleMouseLeave(e)}
  />
</svg>

{#if showOverlay}
  <div
    class="pos"
    style="position: absolute; top: {overlayPosition.top +
      15}px; left: {overlayPosition.left - 15}px"
  >
    <TreeSwitchOverlay name={switch_name}></TreeSwitchOverlay>
  </div>
{/if}

<style>
  svg {
    /* width: 115%; */
    height: 300px;
  }

  path {
    vector-effect: non-scaling-stroke;
    stroke-width: 5.5;
  }
</style>
