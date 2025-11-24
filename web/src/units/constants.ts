/**
 * Unit conversion constants
 * Matches Python's primitive_constants.py
 */

export const PIXELS_PER_METER = 14;
export const METERS_PER_BLOCK = 3.2;
export const PIXELS_PER_BLOCK = PIXELS_PER_METER * METERS_PER_BLOCK; // 48

export const BLOCK_FLOAT_TOLERANCE = 0.01 / METERS_PER_BLOCK;
export const METRIC_FLOAT_TOLERANCE = 0.01;  // 1cm tolerance