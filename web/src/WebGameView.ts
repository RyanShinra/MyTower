/**
 * WebGameView - OO game rendering class for the MyTower web client.
 */

import { type Client } from 'graphql-ws';
import { createClient } from 'graphql-ws';
import { GraphQLClient } from 'graphql-request';

export class WebGameView {
    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;
    private animationFrameId: number | null = null;
    private frameCount: number = 0;

    // GraphQL clients
    private wsClient: Client;              // For subscriptions
    private gqlClient: GraphQLClient;      // For mutations/queries

    // Game state (will come from subscription)
    private currentSnapshot: any = null;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            throw new Error('Could not get 2D context from canvas');
        }
        this.context = ctx;

        // Initialize GraphQL clients
        this.wsClient = createClient({
            url: 'ws://localhost:8000/graphql'
        });

        this.gqlClient = new GraphQLClient('http://localhost:8000/graphql');

        // Start the render loop
        this.startRenderLoop();

        console.log('🎮 WebGameView initialized');
        console.log('📡 GraphQL clients ready');
    }

    private startRenderLoop(): void {
        const render = () => {
            this.draw();
            this.animationFrameId = requestAnimationFrame(render);
        };
        render();
    }

    private draw(): void {
        // Clear canvas
        this.context.fillStyle = '#f0f0f0'; // BACKGROUND_COLOR equivalent
        this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw "Hello World" text
        this.context.fillStyle = '#000000';
        this.context.font = '48px Arial';
        this.context.textAlign = 'center';
        this.context.textBaseline = 'middle';
        this.context.fillText(
            'Hello, MyTower!',
            this.canvas.width / 2,
            this.canvas.height / 2
        );

        // Draw a simple "building" outline
        this.drawSimpleBuilding();

        // Draw frame counter (proof it's animating)
        this.frameCount++;
        this.context.fillStyle = '#666';
        this.context.font = '14px monospace';
        this.context.textAlign = 'left';
        this.context.fillText(
            `Frame: ${this.frameCount}`,
            10,
            this.canvas.height - 10
        );
    }

    private drawSimpleBuilding(): void {
        const buildingWidth = 400;
        const buildingHeight = 600;
        const x = (this.canvas.width - buildingWidth) / 2;
        const y = (this.canvas.height - buildingHeight) / 2 + 100;

        // Building outline
        this.context.strokeStyle = '#333333';
        this.context.lineWidth = 2;
        this.context.strokeRect(x, y, buildingWidth, buildingHeight);

        // Draw some "floors"
        const floorHeight = 60;
        for (let i = 0; i < 10; i++) {
            const floorY = y + buildingHeight - (i * floorHeight);
            this.context.strokeRect(x, floorY, buildingWidth, floorHeight);
        }
    }

    // Public API for mutations (will be called from Svelte buttons)
    public async addFloor(floorType: string): Promise<void> {
        const mutation = `
      mutation AddFloor($floorType: FloorTypeGQL!) {
        addFloor(floorType: $floorType)
      }
    `;

        try {
            await this.gqlClient.request(mutation, { floorType });
            console.log(`✅ Added floor: ${floorType}`);
        } catch (error) {
            console.error('❌ Failed to add floor:', error);
        }
    }

    public cleanup(): void {
        if (this.animationFrameId !== null) {
            cancelAnimationFrame(this.animationFrameId);
        }

        // Close WebSocket connection
        this.wsClient.dispose();

        console.log('🧹 WebGameView cleaned up');
    }
}