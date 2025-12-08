// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * ElevatorShaftRenderer - Responsible for drawing elevator shafts
 * Infers shaft positions from elevator horizontal positions
 */

import { PIXELS_PER_BLOCK } from './constants';
import type { ElevatorSnapshotGql } from '../generated/graphql';

export class ElevatorShaftRenderer {
  // Shaft dimensions
  private readonly SHAFT_WIDTH = 1.0; // blocks (matches elevator width)
  private readonly SHAFT_COLOR = '#d0d0d0'; // Light gray
  private readonly SHAFT_OUTLINE_COLOR = '#a0a0a0'; // Darker gray outline

  constructor(
    private context: CanvasRenderingContext2D,
    private canvasHeight: number
  ) {}

  public drawShafts(elevators: ReadonlyArray<ElevatorSnapshotGql>): void {
    // Group elevators by horizontal position to identify shafts
    const shaftPositions = new Set<number>();

    for (const elevator of elevators) {
      shaftPositions.add(elevator.horizontalPosition);
    }

    // Draw a shaft for each unique horizontal position
    for (const hPos of shaftPositions) {
      this.drawShaft(hPos);
    }
  }

  private drawShaft(horizontalPosition: number): void {
    const x = horizontalPosition * PIXELS_PER_BLOCK;
    const y = 0; // Start at top of canvas
    const width = this.SHAFT_WIDTH * PIXELS_PER_BLOCK;
    const height = this.canvasHeight; // Full height

    // Draw shaft background
    this.context.fillStyle = this.SHAFT_COLOR;
    this.context.fillRect(x, y, width, height);

    // Draw shaft outline
    this.context.strokeStyle = this.SHAFT_OUTLINE_COLOR;
    this.context.lineWidth = 1;
    this.context.strokeRect(x, y, width, height);
  }
}
