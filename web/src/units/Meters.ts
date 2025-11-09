/**
 * Meters - Physical SI measurement
 * Matches Python's Meters class
 */

import type { MetersValue } from './types';
import { METERS_PER_BLOCK, PIXELS_PER_METER, METRIC_FLOAT_TOLERANCE } from './constants';
import { Pixels } from './Pixels';
import { Blocks } from './Blocks';

export class Meters {
  private readonly _value: MetersValue;

  private constructor(value: number) {
    if (!Number.isFinite(value)) {
      throw new Error(`Meters value must be finite, got ${value}`);
    }
    this._value = value as MetersValue;
  }

  public static from(value: number): Meters {
    return new Meters(value);
  }

  public get value(): number {
    return this._value;
  }

  public toPixels(): import('./Pixels').Pixels {
    return Pixels.from(this._value * PIXELS_PER_METER);
  }

  public toBlocks(): import('./Blocks').Blocks {
    return Blocks.from(this._value * METERS_PER_BLOCK);
  }

  public add(other: Meters): Meters {
    return Meters.from(this._value + other._value);
  }

  public sub(other: Meters): Meters {
    return Meters.from(this._value - other._value);
  }

  public mul(scalar: number): Meters {
    return Meters.from(this._value * scalar);
  }

  public div(scalar: number): Meters {
    return Meters.from(this._value / scalar);
  }

  public equals(other: Meters): boolean {
    return Math.abs(this._value - other._value) < METRIC_FLOAT_TOLERANCE;
  }

  public abs(): Meters {
    return Meters.from(Math.abs(this._value));
  }

  public toString(): string {
    return `Meters(${this._value})`;
  }
}