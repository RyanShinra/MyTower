// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * WebGameView - Main game coordinator
 * Matches Python's DesktopView architecture
 */

import { createClient, type Client } from 'graphql-ws';
import { GraphQLClient } from 'graphql-request';
import { BACKGROUND_COLOR } from './rendering/constants';
import { FloorRenderer } from './rendering/FloorRenderer';
import { ElevatorRenderer } from './rendering/ElevatorRenderer';
import { PersonRenderer } from './rendering/PersonRenderer';
import { UIRenderer } from './rendering/UIRenderer';

// Import generated types
import type { 
  BuildingSnapshotGql,
  FloorTypeGql 
} from './generated/graphql';

export class WebGameView {
  private canvas: HTMLCanvasElement;
  private context: CanvasRenderingContext2D;
  private animationFrameId: number | null = null;
  private frameCount: number = 0;

  // GraphQL clients
  private wsClient: Client;
  private gqlClient: GraphQLClient;
  
  // Renderers (Single Responsibility Principle!)
  private floorRenderer: FloorRenderer;
  private elevatorRenderer: ElevatorRenderer;
  private personRenderer: PersonRenderer;
  private uiRenderer: UIRenderer;
  
  // Game state
  private currentSnapshot: BuildingSnapshotGql | null = null;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Could not get 2D context from canvas');
    }
    this.context = ctx;

    // Initialize renderers
    const canvasHeight = canvas.height;
    this.floorRenderer = new FloorRenderer(this.context, canvasHeight);
    this.elevatorRenderer = new ElevatorRenderer(this.context, canvasHeight);
    this.personRenderer = new PersonRenderer(this.context, canvasHeight);
    this.uiRenderer = new UIRenderer(this.context, canvasHeight);

    // Initialize GraphQL clients
    // Use environment variable if set, otherwise default to current hostname (production)
    // This allows local dev override via .env while production "just works"
    const SERVER_HOST = import.meta.env.VITE_SERVER_HOST || window.location.hostname;
    const SERVER_PORT = import.meta.env.VITE_SERVER_PORT || '8000';

    console.log(`[WEB] Connecting to game server at ${SERVER_HOST}:${SERVER_PORT}`);
    console.log(`[CHECK] Client info: ${navigator.userAgent}`);
    console.log(`[CHECK] Page protocol: ${window.location.protocol}`);

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const httpProtocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    const wsUrl = `${wsProtocol}//${SERVER_HOST}:${SERVER_PORT}/graphql`;
    
    console.log(`[CHECK] WebSocket URL: ${wsUrl}`);
    
    // Create WebSocket client with explicit configuration
    // Note: graphql-ws v6.x uses the modern 'graphql-transport-ws' protocol by default
    this.wsClient = createClient({ 
      url: wsUrl,
      // Handle WebSocket connection errors and closures BEFORE subscribing
      on: {
        connecting: () => {
          console.log('[CONNECT] WebSocket connecting...');
        },
        opened: (socket: any) => {
          console.log('[OK] WebSocket opened successfully');
          console.log(`[CHECK] Socket readyState: ${socket?.readyState}`);
          console.log(`[CHECK] Socket protocol: ${socket?.protocol}`);
          console.log(`[CHECK] Socket url: ${socket?.url}`);
        },
        connected: (socket: any, payload: any) => {
          console.log('[OK] WebSocket connected and acknowledged');
          console.log(`[CHECK] Connection payload:`, payload);
        },
        ping: (received: boolean, payload: any) => {
          console.log(`[PING] Ping ${received ? 'received' : 'sent'}`, payload);
        },
        pong: (received: boolean, payload: any) => {
          console.log(`[PONG] Pong ${received ? 'received' : 'sent'}`, payload);
        },
        message: (message: any) => {
          console.log(' WebSocket message:', message);
        },
        error: (error: any) => {
          console.error('[ERROR] WebSocket connection error:', error);
          console.error('[CHECK] Error type:', typeof error);
          console.error('[CHECK] Error constructor:', error?.constructor?.name);
          if (error instanceof Event) {
            console.error('[CHECK] Event type:', error.type);
            console.error('[CHECK] Event target:', error.target);
          }
          if (error instanceof CloseEvent) {
            console.error('[CHECK] Close code:', error.code);
            console.error('[CHECK] Close reason:', error.reason);
            console.error('[CHECK] Was clean:', error.wasClean);
          }
          this.uiRenderer.showConnectionError('Connection to game server failed.');
          this.currentSnapshot = null;
        },
        closed: (event: any) => {
          console.warn('[WS] WebSocket connection closed');
          if (event) {
            console.warn('[CHECK] Close event code:', event.code);
            console.warn('[CHECK] Close event reason:', event.reason);
            console.warn('[CHECK] Was clean:', event.wasClean);
          }
          this.uiRenderer.showConnectionError('Connection to game server lost.');
          this.currentSnapshot = null;
        },
      },
    });
    
    this.gqlClient = new GraphQLClient(`${httpProtocol}//${SERVER_HOST}:${SERVER_PORT}/graphql`);

    // Start subscription and rendering
    this.subscribeToBuilding();
    this.startRenderLoop();
    
    console.log('[GAME] WebGameView initialized with typed units system');
  }

  private subscribeToBuilding(): void {
    console.log(' Starting subscription to building state stream...');
    
    const subscription = `
      subscription BuildingStateStream {
        buildingStateStream(intervalMs: 50) {
          time
          money
          floors {
            floorNumber
            floorType
            floorHeight
            leftEdgeBlock
            floorWidth
            personCount
            floorColor { red green blue }
            floorboardColor { red green blue }
          }
          elevators {
            id
            verticalPosition
            horizontalPosition
            destinationFloor
            state
            nominalDirection
            doorOpen
            passengerCount
          }
          people {
            personId
            currentFloorNum
            currentVerticalPosition
            currentHorizontalPosition
            destinationFloorNum
            destinationHorizontalPosition
            state
            waitingTime
            madFraction
            drawColor { red green blue }
          }
        }
      }
    `;

    let messageCount = 0;
    this.wsClient.subscribe(
      { query: subscription },
      {
        next: (result: any) => {
          messageCount++;
          if (messageCount === 1) {
            console.log('[OK] First subscription message received!');
          }
          if (messageCount % 100 === 0) {
            console.log(`[INFO] Received ${messageCount} subscription messages`);
          }
          this.currentSnapshot = result.data?.buildingStateStream;
        },
        error: (error: any) => {
          console.error('[ERROR] Subscription error:', error);
          console.error('[CHECK] Error details:', JSON.stringify(error, null, 2));
          this.uiRenderer.showConnectionError('Subscription to game server failed.');
          this.currentSnapshot = null;
        },
        complete: () => {
          console.log('[i] Subscription completed');
          console.log(`[INFO] Total messages received: ${messageCount}`);
        }
      }
    );
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
    this.context.fillStyle = BACKGROUND_COLOR;
    this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

    if (!this.currentSnapshot) {
      this.uiRenderer.drawWaitingMessage();
      return;
    }

    // Delegate to specialized renderers
    this.drawFloors();
    this.drawElevators();
    this.drawPeople();
    this.drawUI();
  }

  private drawFloors(): void {
    if (!this.currentSnapshot) return;
    for (const floor of this.currentSnapshot.floors) {
      this.floorRenderer.drawFloor(floor);
    }
  }

  private drawElevators(): void {
    if (!this.currentSnapshot) return;
    for (const elevator of this.currentSnapshot.elevators) {
      this.elevatorRenderer.drawElevator(elevator);
    }
  }

  private drawPeople(): void {
    if (!this.currentSnapshot) return;
    for (const person of this.currentSnapshot.people) {
      this.personRenderer.drawPerson(person);
    }
  }

  private drawUI(): void {
    if (!this.currentSnapshot) return;
    this.frameCount++;
    this.uiRenderer.drawGameStats(this.currentSnapshot.time, this.currentSnapshot.money);
    this.uiRenderer.drawFrameCounter(this.frameCount);
  }

  public async addFloor(floorType: FloorTypeGql): Promise<void> {
    const mutation = `
      mutation AddFloor($floorType: FloorTypeGQL!) {
        addFloor(floorType: $floorType)
      }
    `;
    
    try {
      await this.gqlClient.request(mutation, { floorType });
      console.log(`[OK] Added floor: ${floorType}`);
    } catch (error) {
      console.error('[ERROR] Failed to add floor:', error);
    }
  }

  public cleanup(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }
    this.wsClient.dispose();
    console.log('[CLEAN] WebGameView cleaned up');
  }
}