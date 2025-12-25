// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * FloorRenderer - Responsible for drawing floors
 * Matches Python's FloorRenderer
 */

import { Blocks } from '../units/Blocks';
import { FLOORBOARD_HEIGHT, PIXELS_PER_BLOCK } from './constants';
import { CoordinateTransform } from './CoordinateTransform';
import type { ColorGQL, FloorSnapshotGQL } from '../generated/graphql';

export class FloorRenderer {
  private transform: CoordinateTransform;

  constructor(
    private context: CanvasRenderingContext2D,
    canvasHeight: number
  ) {
    this.transform = new CoordinateTransform(canvasHeight);
  }

  /**
   * Calculate the bottom position (in world space) of a floor.
   * Floors are 1-indexed, so floor 1 starts at z=0.
   */
  private calculateFloorBottom(floorNumber: number): Blocks {
    return Blocks.from(floorNumber - 1);
  }

  public drawFloor(floor: FloorSnapshotGQL): void {
    // World space (z): positions in blocks from ground
    const floorBottomZ = this.calculateFloorBottom(floor.floorNumber);
    const floorHeight = Blocks.from(floor.floorHeight);
    const floorTopZ = floorBottomZ.add(floorHeight);

    // Screen space (y): convert to pixels from top of canvas
    const floorTopY = this.transform.worldToScreen(floorTopZ);
    
    // Dimensions in pixels
    const leftX = floor.leftEdgeBlock * PIXELS_PER_BLOCK;
    const width = floor.floorWidth * PIXELS_PER_BLOCK;
    const height = floorHeight.toPixels().value;

    // Draw floor background
    this.drawFloorBackground(leftX, floorTopY.value, width, height, floor.floorColor);
    
    // Draw floorboard line at top
    this.drawFloorboard(leftX, floorTopY.value, width, floor.floorboardColor);
    
    // Draw floor number
    this.drawFloorNumber(floor.floorNumber, leftX, floorTopY.value);
  }

  private drawFloorBackground(
    x: number,
    y: number,
    width: number,
    height: number,
    color: ColorGQL
  ): void {
    this.context.fillStyle = `rgb(${color.red}, ${color.green}, ${color.blue})`;
    this.context.fillRect(x, y, width, height);
  }

  private drawFloorboard(
    x: number,
    y: number,
    width: number,
    color: ColorGQL
  ): void {
    this.context.fillStyle = `rgb(${color.red}, ${color.green}, ${color.blue})`;
    this.context.fillRect(x, y, width, FLOORBOARD_HEIGHT);
  }

  private drawFloorNumber(floorNumber: number, x: number, y: number): void {
    this.context.fillStyle = '#000000';
    this.context.font = '18px Helvetica';
    this.context.textAlign = 'left';
    this.context.textBaseline = 'top';
    this.context.fillText(`Floor ${floorNumber}`, x + 8, y + 12);
  }
}