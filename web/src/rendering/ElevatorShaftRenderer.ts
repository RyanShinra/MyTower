// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * ElevatorShaftRenderer - Responsible for drawing elevator shafts
 * Draws shafts based on elevator bank min/max floor data
 * Matches Python's ElevatorBankRenderer logic
 */

import { PIXELS_PER_BLOCK } from './constants';
import { CoordinateTransform } from './CoordinateTransform';
import { Blocks } from '../units/Blocks';
import type { ElevatorBankSnapshotGQL } from '../generated/graphql';

export class ElevatorShaftRenderer {
  private transform: CoordinateTransform;

  // Shaft dimensions
  private readonly SHAFT_WIDTH = 1.0; // blocks (matches elevator width)
  private readonly SHAFT_COLOR = '#d0d0d0'; // Light gray
  private readonly SHAFT_OUTLINE_COLOR = '#a0a0a0'; // Darker gray outline

  constructor(
    private context: CanvasRenderingContext2D,
    private canvasHeight: number
  ) {
    this.transform = new CoordinateTransform(canvasHeight);
  }

  public drawShafts(elevatorBanks: ReadonlyArray<ElevatorBankSnapshotGQL>): void {
    for (const bank of elevatorBanks) {
      this.drawShaft(bank);
    }
  }

  private drawShaft(bank: ElevatorBankSnapshotGQL): void {
    // Calculate shaft dimensions based on min/max floors
    // Following Python's logic: shaft_height = (max_floor - min_floor + 1) blocks
    const shaftHeightBlocks = bank.maxFloor - bank.minFloor + 1;
    const shaftHeight = shaftHeightBlocks * PIXELS_PER_BLOCK;

    // Shaft top is at max_floor position
    const shaftTopZ = Blocks.from(bank.maxFloor);
    const shaftTopY = this.transform.worldToScreen(shaftTopZ);

    // Horizontal position
    const x = bank.horizontalPosition * PIXELS_PER_BLOCK;
    const width = this.SHAFT_WIDTH * PIXELS_PER_BLOCK;

    // Draw shaft background
    this.context.fillStyle = this.SHAFT_COLOR;
    this.context.fillRect(x, shaftTopY.value, width, shaftHeight);

    // Draw shaft outline
    this.context.strokeStyle = this.SHAFT_OUTLINE_COLOR;
    this.context.lineWidth = 1;
    this.context.strokeRect(x, shaftTopY.value, width, shaftHeight);
  }
}
