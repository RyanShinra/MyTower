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
    const SERVER_HOST = '192.168.50.59'; 
    this.wsClient = createClient({ url: `ws://${SERVER_HOST}:8000/graphql` });
    this.gqlClient = new GraphQLClient(`http://${SERVER_HOST}:8000/graphql`);

    // Start
    this.subscribeToBuilding();
    this.startRenderLoop();
    
    console.log('🎮 WebGameView initialized with typed units system');
  }

  private subscribeToBuilding(): void {
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

    this.wsClient.subscribe(
      { query: subscription },
      {
        next: (result: any) => {
          this.currentSnapshot = result.data?.buildingStateStream;
        },
        error: (error: any) => {
          console.error('❌ Subscription error:', error);
        },
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
      console.log(`✅ Added floor: ${floorType}`);
    } catch (error) {
      console.error('❌ Failed to add floor:', error);
    }
  }

  public cleanup(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }
    this.wsClient.dispose();
    console.log('🧹 WebGameView cleaned up');
  }
}