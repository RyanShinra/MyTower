/**
 * PersonRenderer - Responsible for drawing people
 * Matches Python's PersonRenderer
 */

import { Blocks } from '../units/Blocks';
import { PERSON_RADIUS, PIXELS_PER_BLOCK } from './constants';
import { CoordinateTransform } from './CoordinateTransform';
import type { ColorGql, PersonSnapshotGql } from '../generated/graphql';

export class PersonRenderer {
  private transform: CoordinateTransform;

  constructor(
    private context: CanvasRenderingContext2D,
    canvasHeight: number
  ) {
    this.transform = new CoordinateTransform(canvasHeight);
  }

  /**
   * Calculate Y position (screen space) for a person at given vertical position
   * Matches Python: apparent_floor = vert_position - 1.0
   */
  private calculateYPosition(verticalPosition: number): number {
    // Person's feet are at the bottom of their block
    const apparentFloor = verticalPosition - 1.0;
    const zBottom = Blocks.from(apparentFloor);
    
    // Center vertically within the floor
    const halfFloorHeight = Blocks.from(0.5);
    const zCentered = zBottom.add(halfFloorHeight);
    
    return this.transform.worldToScreen(zCentered).value;
  }

  /**
   * Calculate X position (screen space) for a person at given horizontal position
   */
  private calculateXPosition(horizontalPosition: number): number {
    const xLeft = horizontalPosition * PIXELS_PER_BLOCK;
    const blockHalfWidth = PIXELS_PER_BLOCK / 2;
    return xLeft + blockHalfWidth;
  }

  public drawPerson(person: PersonSnapshotGql): void {
    // Calculate screen positions
    const x = this.calculateXPosition(person.currentHorizontalPosition);
    const y = this.calculateYPosition(person.currentVerticalPosition);
    
    // Calculate destination for debugging
    const destX = this.calculateXPosition(person.destinationHorizontalPosition);
    const destY = this.calculateYPosition(person.destinationFloorNum);

    // TODO: Remove this once we have proper state management
    // Skip drawing if at destination (demo purposes)
    if (Math.abs(x - destX) < 1 && Math.abs(y - destY) < 1) {
      return;
    }

    // Draw destination marker
    this.drawDestinationMarker(destX, destY);
    
    // Draw person as circle
    this.drawPersonCircle(x, y, person.drawColor);
  }

  private drawDestinationMarker(x: number, y: number): void {
    this.context.fillStyle = '#666';
    this.context.font = '24px Consolas';
    this.context.textAlign = 'center';
    this.context.textBaseline = 'middle';
    this.context.fillText('X', x, y);
  }

  private drawPersonCircle(
    x: number,
    y: number,
    color: ColorGql
  ): void {
    this.context.fillStyle = `rgb(${color.red}, ${color.green}, ${color.blue})`;
    this.context.beginPath();
    this.context.arc(x, y, PERSON_RADIUS, 0, 2 * Math.PI);
    this.context.fill();
  }
}