declare module "svelte-qrcode" {
  import { SvelteComponent } from "svelte";

  export default class QrCode extends SvelteComponent<{
    value: string;
    size?: number;
    padding?: number;
    color?: string;
    background?: string;
    errorCorrection?: "L" | "M" | "Q" | "H";
  }> {}
}
