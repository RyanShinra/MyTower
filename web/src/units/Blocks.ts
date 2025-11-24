// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * Blocks - Building grid coordinate system
 * Matches Python's Blocks class
 */

import type { BlocksValue } from './types';
import { METERS_PER_BLOCK, PIXELS_PER_BLOCK, BLOCK_FLOAT_TOLERANCE } from './constants';
import { Pixels } from './Pixels';
import { Meters } from './Meters';

export class Blocks {
  private readonly _value: BlocksValue;

  private constructor(value: number) {
    if (!Number.isFinite(value)) {
      throw new Error(`Blocks value must be finite, got ${value}`);
    }
    this._value = value as BlocksValue;
  }

  /**
   * Factory method - only way to create Blocks
   */
  public static from(value: number): Blocks {
    return new Blocks(value);
  }

  /**
   * Get raw numeric value (use sparingly!)
   */
  public get value(): number {
    return this._value;
  }

  /**
   * Convert to Pixels for rendering
   */
  public toPixels(): import('./Pixels').Pixels {
    return Pixels.from(this._value * PIXELS_PER_BLOCK);
  }

  /**
   * Convert to Meters for physics
   */
  public toMeters(): import('./Meters').Meters {
    return Meters.from(this._value * METERS_PER_BLOCK);
  }

  // Math operations
  public add(other: Blocks): Blocks {
    return Blocks.from(this._value + other._value);
  }

  public sub(other: Blocks): Blocks {
    return Blocks.from(this._value - other._value);
  }

  public mul(scalar: number): Blocks {
    return Blocks.from(this._value * scalar);
  }

  public div(scalar: number): Blocks {
    if (scalar === 0) {
      throw new Error('Cannot divide Blocks by zero');
    }
    return Blocks.from(this._value / scalar);
  }

  // Comparison
  public equals(other: Blocks): boolean {
    return Math.abs(this._value - other._value) < BLOCK_FLOAT_TOLERANCE;
  }

  public lessThan(other: Blocks): boolean {
    return this._value < other._value;
  }

  public greaterThan(other: Blocks): boolean {
    return this._value > other._value;
  }

  public abs(): Blocks {
    return Blocks.from(Math.abs(this._value));
  }

  public toString(): string {
    return `Blocks(${this._value})`;
  }
}