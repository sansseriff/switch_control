import type Tree from "./lib/TreeDiagram.svelte";
import type { TreeState } from "./types";

function fetchWithConfig(url: string, method: string, body?: any): Promise<any> {
    const headers = { 'Content-Type': 'application/json' };
    const controller = new AbortController();
    const signal = controller.signal;

    // Specify the base URL of the different server
    const baseUrl = "http://127.0.0.1:8000";

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


interface Channel {
    number: number;
}

interface Switch {
    number: number;
}





export function requestChannel(channe_request: Channel): Promise<TreeState> {
    return fetchWithConfig('/channel', 'POST', channe_request);
}


export function flipSwitch(switch_toggle_request: Switch): Promise<TreeState> {
    return fetchWithConfig('/switch', 'POST', switch_toggle_request);
}


export function getTreeState(): Promise<TreeState> {
    return fetchWithConfig('/tree', 'GET');
}

export function reset(): Promise<TreeState> {
    return fetchWithConfig('/reset', 'GET');
}

export function reAssert(): Promise<TreeState> {
    return fetchWithConfig('/re_assert', 'GET');
}