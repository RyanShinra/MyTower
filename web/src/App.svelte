<!-- Copyright (c) 2025 Ryan Osterday. All rights reserved. -->
<!-- See LICENSE file for details. -->

<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { WebGameView } from "./WebGameView";

    let canvas: HTMLCanvasElement;
    let gameView: WebGameView | null = null;

    onMount(() => {
        // Create the game view once canvas is mounted
        gameView = new WebGameView(canvas);
        console.log("🎮 WebGameView initialized");
    });

    onDestroy(() => {
        // Cleanup when component unmounts
        gameView?.cleanup();
        console.log("🧹 WebGameView cleaned up");
    });
</script>

<div class="game-container">
    <canvas bind:this={canvas} width={650} height={600}></canvas>

    <div class="info">
        <h1>MyTower Web</h1>
    </div>

    <div class="controls">
        <h2>Controls</h2>

        <div class="button-group">
            <h3>Add Floor</h3>
            <button>Lobby</button>
            <button>Office</button>
            <button>Retail</button>
            <button>Restaurant</button>
            <button>Apartment</button>
            <button>Hotel</button>
        </div>

        <div class="button-group">
            <h3>Elevators</h3>
            <button>Add Elevator Bank</button>
            <button>Add Elevator</button>
        </div>

        <div class="button-group">
            <h3>People</h3>
            <button>Add Person</button>
        </div>
    </div>
</div>

<style>
    .game-container {
        position: relative;
        width: 100%;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        background: #1a1a1a;
    }

    canvas {
        border: 2px solid #444;
        background: #f0f0f0;
    }

    .info {
        position: absolute;
        top: 20px;
        left: 20px;
        color: white;
        font-family:
            system-ui,
            -apple-system,
            sans-serif;
    }

    h1 {
        margin: 0;
        font-size: 24px;
    }

    p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.8;
    }

    .controls {
        position: absolute;
        top: 20px;
        right: 20px;
        color: white;
        font-family:
            system-ui,
            -apple-system,
            sans-serif;
        background: rgba(0, 0, 0, 0.8);
        padding: 15px;
        border-radius: 8px;
        min-width: 200px;
    }

    .controls h2 {
        margin: 0 0 15px 0;
        font-size: 20px;
        border-bottom: 2px solid #444;
        padding-bottom: 8px;
    }

    .button-group {
        margin-bottom: 20px;
    }

    .button-group h3 {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    button {
        display: block;
        width: 100%;
        margin-bottom: 6px;
        padding: 8px 12px;
        background: #333;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
    }

    button:hover {
        background: #444;
        border-color: #666;
    }

    button:active {
        background: #555;
        transform: scale(0.98);
    }
</style>
