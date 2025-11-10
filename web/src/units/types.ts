/**
 * Branded type pattern for compile-time unit safety
 * 
 * These types prevent mixing units at compile time.
 * The unique symbol makes each type nominally distinct.
 */

declare const BlocksBrand: unique symbol;
declare const MetersBrand: unique symbol;
declare const PixelsBrand: unique symbol;

export type BlocksValue = number & { readonly [BlocksBrand]: typeof BlocksBrand };
export type MetersValue = number & { readonly [MetersBrand]: typeof MetersBrand };
export type PixelsValue = number & { readonly [PixelsBrand]: typeof PixelsBrand };