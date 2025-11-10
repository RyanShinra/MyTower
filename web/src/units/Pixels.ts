/**
 * Pixels - Screen space coordinate
 * Matches Python's Pixels class
 */

import type { PixelsValue } from './types';
import { PIXELS_PER_METER, PIXELS_PER_BLOCK } from './constants';
import { Blocks } from './Blocks';
import { Meters } from './Meters';

export class Pixels {
  private readonly _value: PixelsValue;

  private constructor(value: number) {
    // Pixels are always integers
    if (!Number.isFinite(value)) {
      throw new Error(`Pixels value must be finite, got ${value}`);
    }
    const intValue = Math.round(value);
    this._value = intValue as PixelsValue;
  }

  public static from(value: number): Pixels {
    return new Pixels(value);
  }

  public get value(): number {
    return this._value;
  }

  public toBlocks(): import('./Blocks').Blocks {
    return Blocks.from(this._value / PIXELS_PER_BLOCK);
  }

  public toMeters(): import('./Meters').Meters {
    const metersPerPixel = 1 / PIXELS_PER_METER;
    return Meters.from(this._value * metersPerPixel);
  }

  public add(other: Pixels): Pixels {
    return Pixels.from(this._value + other._value);
  }

  public sub(other: Pixels): Pixels {
    return Pixels.from(this._value - other._value);
  }

  public mul(scalar: number): Pixels {
    return Pixels.from(this._value * scalar);
  }

  public div(scalar: number): Pixels {
    return Pixels.from(this._value / scalar);
  }

  public abs(): Pixels {
    return Pixels.from(Math.abs(this._value));
  }

  public toString(): string {
    return `Pixels(${this._value})`;
  }
}