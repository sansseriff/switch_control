import type Tree from "./lib/TreeDiagram.svelte";
import type { TreeState, ButtonLabelState } from "./types"; // Add ButtonLabelState
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

// Define the structure for the initialization response
interface InitializationResponse {
    tree_state: TreeState;
    button_labels: ButtonLabelState;
}

// Define the structure for button labels payload/response
interface ButtonLabelsPayload {
    label_0: string;
    label_1: string;
    label_2: string;
    label_3: string;
    label_4: string;
    label_5: string;
    label_6: string;
    label_7: string;
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

// Add function to get button labels
export function getButtonLabels(): Promise<ButtonLabelsPayload> {
    return fetchWithConfig('/button_labels', 'GET');
}

// Add function to update button labels
export function updateButtonLabels(labels: ButtonLabelsPayload): Promise<ButtonLabelsPayload> {
    return fetchWithConfig('/button_labels', 'POST', labels);
}


export function reset(verification: Verification): Promise<TreeState> {
    return fetchWithConfig('/reset', 'POST', verification);
}

export function reAssert(verification: Verification): Promise<TreeState> {
    return fetchWithConfig('/re_assert', 'POST', verification);
}

// Modify initialize to return the combined structure
export async function initialize(): Promise<InitializationResponse> {
    return fetchWithConfig('/initialize', 'GET');
    // if (!response.ok) {
    //     throw new Error('Failed to initialize');
    // }
}