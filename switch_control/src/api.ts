import type Tree from "./lib/TreeDiagram.svelte";
import type { TreeState } from "./types";
import type { Verification } from "./types";


function isPywebview() {
    return typeof window.QObject !== 'undefined';
}



function fetchWithConfig(url: string, method: string, body?: any): Promise<any> {
    const headers = { 'Content-Type': 'application/json' };
    const controller = new AbortController();
    const signal = controller.signal;

    // Specify the base URL of the different server

    const isWebView = isPywebview();
    console.log("isWebView: ", isWebView);

    const baseUrl = isWebView ? "http://localhost:8854" : "";

    const config: RequestInit = {
        method,
        signal,
        headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    return fetch(`${baseUrl}${url}`, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // console.log("returning!")
            return response.json();
        });
}


interface ChannelRequest {
    number: number;
    verification: Verification;
}

interface ToggleRequest {
    number: number;
    verification: Verification;
}





export function requestChannel(channel_request: ChannelRequest): Promise<TreeState> {
    return fetchWithConfig('/channel', 'POST', channel_request);
}


export function flipSwitch(switch_toggle_request: ToggleRequest): Promise<TreeState> {
    return fetchWithConfig('/switch', 'POST', switch_toggle_request);
}


export function getTreeState(): Promise<TreeState> {
    return fetchWithConfig('/tree', 'GET');
}

export function reset(verification: Verification): Promise<TreeState> {
    return fetchWithConfig('/reset', 'POST', verification);
}

export function reAssert(verification: Verification): Promise<TreeState> {
    return fetchWithConfig('/re_assert', 'POST', verification);
}

export async function initialize(): Promise<TreeState> {

    return fetchWithConfig('/initialize', 'GET');
    // if (!response.ok) {
    //     throw new Error('Failed to initialize');
    // }
}