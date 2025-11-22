// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * Coordinate transformation utilities
 * 
 * MyTower uses two coordinate systems:
 * - Z-axis (world space): Origin at ground level, increases upward (Blocks)
 * - Y-axis (screen space): Origin at top of canvas, increases downward (Pixels)
 * 
 * Matches the Python rendering architecture.
 */

import { Blocks } from '../units/Blocks';
import { Pixels } from '../units/Pixels';

export class CoordinateTransform {
  private canvasHeight: Pixels;

  constructor(canvasHeight: number) {
    this.canvasHeight = Pixels.from(canvasHeight);
  }

  /**
   * Convert world space Z coordinate to screen space Y coordinate
   * 
   * @param z - Position in world space (blocks from ground)
   * @returns Y position in screen space (pixels from top of canvas)
   */
  public worldToScreen(z: Blocks): Pixels {
    const zPixels = z.toPixels();
    return this.canvasHeight.sub(zPixels);
  }

  /**
   * Convert screen space Y coordinate to world space Z coordinate
   * 
   * @param y - Position in screen space (pixels from top)
   * @returns Z position in world space (blocks from ground)
   */
  public screenToWorld(y: Pixels): Blocks {
    const zPixels = this.canvasHeight.sub(y);
    return zPixels.toBlocks();
  }
}