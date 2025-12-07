// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * UIRenderer - Responsible for drawing UI overlays
 * Matches Python's UI drawing logic
 */

export class UIRenderer {
  constructor(
    private context: CanvasRenderingContext2D,
    private canvasHeight: number
  ) {}

  public drawGameStats(time: number, money: number): void {
    this.drawTime(time);
    this.drawMoney(money);
  }

  public drawFrameCounter(frameCount: number): void {
    this.context.fillStyle = '#666';
    this.context.font = '14px monospace';
    this.context.textAlign = 'left';
    this.context.textBaseline = 'top';
    this.context.fillText(
      `Frame: ${frameCount}`,
      10,
      this.canvasHeight - 30
    );
  }

  public showConnectionError(message: string): void {
    this.context.fillStyle = '#ff0000';
    this.context.font = '24px Helvetica';
    this.context.textAlign = 'center';
    this.context.textBaseline = 'middle';
    const centerX = this.context.canvas.width / 2;
    const centerY = this.canvasHeight / 2;
    this.context.fillText(message, centerX, centerY);
  }

  public drawWaitingMessage(): void {
    this.context.fillStyle = '#666';
    this.context.font = '24px Helvetica';
    this.context.textAlign = 'center';
    this.context.textBaseline = 'middle';
    
    const centerX = this.context.canvas.width / 2;
    const centerY = this.canvasHeight / 2;
    
    this.context.fillText(
      'Waiting for game server...',
      centerX,
      centerY
    );

    this.context.font = '16px Helvetica';
    this.context.fillText(
      'Make sure MyTower is running in hybrid or headless mode',
      centerX,
      centerY + 40
    );
  }

  private drawTextWithBackground(text: string, x: number, y: number): void {
    const padding = 5;

    // Set up font and text alignment for measurement
    this.context.font = '20px Arial';
    this.context.textAlign = 'left';
    this.context.textBaseline = 'top';

    // Measure text for background sizing
    const textMetrics = this.context.measureText(text);
    const textWidth = textMetrics.width;
    const textHeight = textMetrics.actualBoundingBoxAscent + textMetrics.actualBoundingBoxDescent;

    // Draw translucent black background
    this.context.fillStyle = 'rgba(0, 0, 0, 0.5)';
    this.context.fillRect(
      x - padding,
      y - padding,
      textWidth + (padding * 2),
      textHeight + (padding * 2)
    );

    // Draw white text
    this.context.fillStyle = '#FFFFFF';
    this.context.fillText(text, x, y);
  }

  private drawTime(time: number): void {
    const hours = Math.floor(time / 3600) % 24;
    const minutes = Math.floor(time / 60) % 60;
    const seconds = Math.floor(time) % 60;
    const timeStr = `Time: ${this.pad(hours)}:${this.pad(minutes)}:${this.pad(seconds)}`;

    this.drawTextWithBackground(timeStr, 10, 10);
  }

  private drawMoney(money: number): void {
    const moneyStr = `Money: $${money.toLocaleString()}`;

    this.drawTextWithBackground(moneyStr, 10, 40);
  }

  private pad(num: number): string {
    return num.toString().padStart(2, '0');
  }
}