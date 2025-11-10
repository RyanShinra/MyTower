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
    <canvas bind:this={canvas} width={1024} height={768}></canvas>

    <div class="info">
        <h1>MyTower Web</h1>
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
</style>
