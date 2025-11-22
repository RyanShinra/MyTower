// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * Unit conversion constants
 * Matches Python's primitive_constants.py
 */

export const PIXELS_PER_METER = 15;
export const METERS_PER_BLOCK = 3.2;
export const PIXELS_PER_BLOCK = PIXELS_PER_METER * METERS_PER_BLOCK; // 48

export const BLOCK_FLOAT_TOLERANCE = 0.01 / METERS_PER_BLOCK;
export const METRIC_FLOAT_TOLERANCE = 0.01;  // 1cm tolerance