<!-- Copyright (c) 2025 Ryan Osterday. All rights reserved. -->
<!-- See LICENSE file for details. -->

<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { WebGameView } from "./WebGameView";
    import type { FloorTypeGQL } from "./generated/graphql";

    let canvas: HTMLCanvasElement;
    let gameView: WebGameView | null = null;
    // Track the most recently created elevator bank for adding elevators
    // Note: Currently only supports adding elevators to the most recent bank
    // TODO: Support multiple banks with dropdown selection
    let currentElevatorBankId: string | null = null;

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

    // Handler for adding floors
    async function handleAddFloor(floorType: FloorTypeGQL) {
        if (!gameView) {
            console.warn("⚠️ Game view not ready yet");
            return;
        }

        try {
            await gameView.addFloor(floorType);
            console.log(`✅ Added ${floorType} floor`);
        } catch (error) {
            console.error(`❌ Failed to add ${floorType} floor:`, error);
        }
    }

    // Handler for adding elevator bank
    async function handleAddElevatorBank() {
        if (!gameView) {
            console.warn("⚠️ Game view not ready yet");
            return;
        }

        try {
            // Create elevator bank with default parameters:
            // - hCell=3: Horizontal position (center-ish of typical building)
            // - minFloor=0: Ground floor (lobby level)
            // - maxFloor=20: Serves up to 20 floors (typical mid-rise building)
            // TODO: Make these configurable via UI inputs
            const bankId = await gameView.addElevatorBank(3, 0, 20);
            currentElevatorBankId = bankId; // Store for adding elevators
            console.log(`✅ Added elevator bank: ${bankId}`);
        } catch (error) {
            console.error("❌ Failed to add elevator bank:", error);
        }
    }

    // Handler for adding elevator to bank
    async function handleAddElevator() {
        if (!gameView) {
            console.warn("⚠️ Game view not ready yet");
            return;
        }

        if (!currentElevatorBankId) {
            console.warn(
                "⚠️ No elevator bank exists. Create a bank first!",
            );
            return;
        }

        try {
            const elevatorId = await gameView.addElevator(
                currentElevatorBankId,
            );
            console.log(`✅ Added elevator: ${elevatorId}`);
        } catch (error) {
            console.error("❌ Failed to add elevator:", error);
        }
    }

    // Handler for adding person
    async function handleAddPerson() {
        if (!gameView) {
            console.warn("⚠️ Game view not ready yet");
            return;
        }

        try {
            // Spawn test person with fixed parameters:
            // - floor=0: Ground floor (lobby level)
            // - block=2.0: Horizontal position 2 blocks from left edge
            // - destFloor=2: Destination is floor 2
            // - destBlock=2: Destination horizontal position
            // TODO: Add UI inputs for customizable spawn parameters or randomize
            const personId = await gameView.addPerson(0, 2.0, 2, 2);
            console.log(`✅ Added person: ${personId}`);
        } catch (error) {
            console.error("❌ Failed to add person:", error);
        }
    }
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
            <button onclick={() => handleAddFloor("LOBBY")}>Lobby</button>
            <button onclick={() => handleAddFloor("OFFICE")}>Office</button>
            <button onclick={() => handleAddFloor("RETAIL")}>Retail</button>
            <button onclick={() => handleAddFloor("RESTAURANT")}>
                Restaurant
            </button>
            <button onclick={() => handleAddFloor("APARTMENT")}>
                Apartment
            </button>
            <button onclick={() => handleAddFloor("HOTEL")}>Hotel</button>
        </div>

        <div class="button-group">
            <h3>Elevators</h3>
            <button onclick={handleAddElevatorBank}>Add Elevator Bank</button>
            <button onclick={handleAddElevator}>Add Elevator</button>
        </div>

        <div class="button-group">
            <h3>People</h3>
            <button onclick={handleAddPerson}>Add Person</button>
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
