// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * ElevatorRenderer - Responsible for drawing elevators
 * Matches Python's ElevatorRenderer
 */

import { Blocks } from '../units/Blocks';
import { PIXELS_PER_BLOCK } from './constants';
import { CoordinateTransform } from './CoordinateTransform';
import type { ElevatorSnapshotGQL } from '../generated/graphql';

export class ElevatorRenderer {
  private transform: CoordinateTransform;
  
  // Elevator dimensions (should match Python config)
  private readonly ELEVATOR_HEIGHT = 1.0;  // blocks
  private readonly ELEVATOR_WIDTH = 1.0;   // blocks

  constructor(
    private context: CanvasRenderingContext2D,
    canvasHeight: number
  ) {
    this.transform = new CoordinateTransform(canvasHeight);
  }

  public drawElevator(elevator: ElevatorSnapshotGQL): void {
    // World space (z): elevator position in blocks
    const elevatorTopZ = Blocks.from(elevator.verticalPosition);
    
    // Screen space (y): convert to pixels
    const elevatorTopY = this.transform.worldToScreen(elevatorTopZ);
    const elevatorLeftX = elevator.horizontalPosition * PIXELS_PER_BLOCK;
    
    // Dimensions
    const width = this.ELEVATOR_WIDTH * PIXELS_PER_BLOCK;
    const height = this.ELEVATOR_HEIGHT * PIXELS_PER_BLOCK;

    // Draw elevator car
    this.drawElevatorCar(elevatorLeftX, elevatorTopY.value, width, height, elevator.doorOpen);
    
    // Draw passenger count if any
    if (elevator.passengerCount > 0) {
      this.drawPassengerCount(elevatorLeftX, elevatorTopY.value, width, height, elevator.passengerCount);
    }
  }

  private drawElevatorCar(
    x: number,
    y: number,
    width: number,
    height: number,
    doorOpen: boolean
  ): void {
    const color = doorOpen ? '#c8c850' : '#3232c8';
    this.context.fillStyle = color;
    this.context.fillRect(x, y, width, height);
  }

  private drawPassengerCount(
    x: number,
    y: number,
    width: number,
    height: number,
    count: number
  ): void {
    this.context.fillStyle = '#ffffff';
    this.context.font = '12px monospace';
    this.context.textAlign = 'center';
    this.context.textBaseline = 'middle';
    this.context.fillText(
      `${count}`,
      x + width / 2,
      y + height / 2
    );
  }
}