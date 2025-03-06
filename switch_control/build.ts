import { $ } from "bun";

import Bun from "bun";
import path from "node:path";
import { readdir } from "node:fs/promises";
import { parseArgs } from "util";
import { existsSync } from "node:fs";
import { execSync, spawn } from "node:child_process";


const current_directory = import.meta.dir; // https://bun.sh/docs/api/import-meta

const dist_directory = path.join(current_directory, "/dist/");

const output_directory = path.join(current_directory, "../backend/backend/switch_web");


console.log('\x1b[33m >>>>> Building frontend... \x1b[0m');
await $`bun run build`;


console.log('\x1b[33m >>>>> Moving compiled javascript, css, & html to /backend/backend/switch_web/ \x1b[0m');

// Check if output directory exists and remove it first
if (existsSync(output_directory)) {
    console.log('\x1b[33m >>>>> Removing existing output directory... \x1b[0m');
    if (process.platform === "win32") {
        // rm -rf is not working in bun shell yet as of Bun 1.1.34
        execSync(`rmdir /S /Q ${output_directory}`, { stdio: 'inherit' });
    } else {
        await $`rm -rf ${output_directory}`;
    }
}

// Create output directory
console.log('\x1b[33m >>>>> Creating output directory... \x1b[0m');
if (process.platform === "win32") {
    execSync(`mkdir ${output_directory}`, { stdio: 'inherit' });
} else {
    await $`mkdir -p ${output_directory}`;
}

// Copy files
await $`cp -R ${path.join(dist_directory, "assets")} ${output_directory}`;
await $`cp ${path.join(dist_directory, "index.html")} ${output_directory}`;