/**
 * Mobile Responsiveness Service - Phase 5 Task 8
 * Touch interactions, mobile layout, and responsive design patterns
 */

import { CraftNode } from './canvasNodeRenderer';
import { logger } from '@/utils/logger';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Touch event details
 */
export interface TouchEventDetails {
  timestamp: number;
  touches: TouchPoint[];
  centerX: number;
  centerY: number;
  distance: number; // for pinch
  angle: number; // for rotation
  scale: number; // for pinch zoom
  velocity: { x: number; y: number };
}

/**
 * Touch point
 */
export interface TouchPoint {
  id: number;
  x: number;
  y: number;
  previousX: number;
  previousY: number;
  deltaX: number;
  deltaY: number;
}

/**
 * Gesture type
 */
export type GestureType = 
  | 'tap'
  | 'double-tap'
  | 'long-press'
  | 'swipe'
  | 'pinch'
  | 'rotation'
  | 'pan';

/**
 * Gesture event
 */
export interface GestureEvent {
  type: GestureType;
  details: TouchEventDetails;
  timestamp: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

/**
 * Mobile layout mode
 */
export type LayoutMode = 
  | 'compact' // < 480px
  | 'tablet' // 480px - 768px
  | 'desktop' // > 768px
  | 'landscape'
  | 'portrait';

/**
 * Viewport info
 */
export interface ViewportInfo {
  width: number;
  height: number;
  mode: LayoutMode;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  pixelRatio: number;
}

/**
 * Mobile-optimized canvas settings
 */
export interface MobileCanvasSettings {
  touchDebounceMs: number;
  minimumTapDuration: number;
  maximumTapDuration: number;
  minimumPanDistance: number;
  minimumPinchScale: number;
  doubleTapInterval: number;
  longPressInterval: number;
}

/**
 * UI state for mobile
 */
export interface MobileUIState {
  showToolbar: boolean;
  toolbarPosition: 'top' | 'bottom' | 'floating';
  showPropertyPanel: boolean;
  propertyPanelMode: 'slide-over' | 'modal' | 'bottom-sheet';
  canvasFullscreen: boolean;
  showMinimap: boolean;
  hiddenElements: Set<string>;
}

// ============================================================================
// Touch Event Processing
// ============================================================================

class TouchTracker {
  private activeTouches: Map<number, TouchPoint> = new Map();
  private touchStartTime: number = 0;
  private previousTouchCount: number = 0;

  /**
   * Track touch start
   */
  onTouchStart(event: TouchEvent): TouchPoint[] {
    this.touchStartTime = Date.now();
    const points: TouchPoint[] = [];

    for (let i = 0; i < event.touches.length; i++) {
      const touch = event.touches[i];
      const point: TouchPoint = {
        id: touch.identifier,
        x: touch.clientX,
        y: touch.clientY,
        previousX: touch.clientX,
        previousY: touch.clientY,
        deltaX: 0,
        deltaY: 0,
      };

      this.activeTouches.set(touch.identifier, point);
      points.push(point);
    }

    this.previousTouchCount = event.touches.length;
    return points;
  }

  /**
   * Track touch move
   */
  onTouchMove(event: TouchEvent): TouchPoint[] {
    const points: TouchPoint[] = [];

    for (let i = 0; i < event.touches.length; i++) {
      const touch = event.touches[i];
      const existing = this.activeTouches.get(touch.identifier);

      if (existing) {
        const deltaX = touch.clientX - existing.x;
        const deltaY = touch.clientY - existing.y;

        existing.previousX = existing.x;
        existing.previousY = existing.y;
        existing.x = touch.clientX;
        existing.y = touch.clientY;
        existing.deltaX = deltaX;
        existing.deltaY = deltaY;
      }

      points.push(this.activeTouches.get(touch.identifier)!);
    }

    return points;
  }

  /**
   * Track touch end
   */
  onTouchEnd(event: TouchEvent): { points: TouchPoint[]; duration: number } {
    const points: TouchPoint[] = [];
    const duration = Date.now() - this.touchStartTime;

    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i];
      const point = this.activeTouches.get(touch.identifier);

      if (point) {
        points.push(point);
        this.activeTouches.delete(touch.identifier);
      }
    }

    this.previousTouchCount = event.touches.length;
    return { points, duration };
  }

  /**
   * Get active touches count
   */
  getActiveTouchCount(): number {
    return this.activeTouches.size;
  }

  /**
   * Clear all touches
   */
  clear(): void {
    this.activeTouches.clear();
    this.touchStartTime = 0;
  }
}

// ============================================================================
// Gesture Recognition
// ============================================================================

class GestureRecognizer {
  private touchTracker = new TouchTracker();
  private lastTapTime: number = 0;
  private lastTapPosition: { x: number; y: number } | null = null;
  private longPressTimer: NodeJS.Timeout | null = null;
  private settings: MobileCanvasSettings = {
    touchDebounceMs: 50,
    minimumTapDuration: 50,
    maximumTapDuration: 500,
    minimumPanDistance: 10,
    minimumPinchScale: 0.05,
    doubleTapInterval: 300,
    longPressInterval: 500,
  };

  /**
   * Recognize gestures from touch events
   */
  recognizeGesture(event: TouchEvent): GestureEvent | null {
    const touches = event.touches;

    // Clear long press timer if touch ended
    if (event.type === 'touchend' || event.type === 'touchcancel') {
      if (this.longPressTimer) {
        clearTimeout(this.longPressTimer);
        this.longPressTimer = null;
      }
    }

    switch (event.type) {
      case 'touchstart':
        return this.handleTouchStart(event);
      case 'touchmove':
        return this.handleTouchMove(event);
      case 'touchend':
        return this.handleTouchEnd(event);
    }

    return null;
  }

  /**
   * Handle touch start
   */
  private handleTouchStart(event: TouchEvent): GestureEvent | null {
    const points = this.touchTracker.onTouchStart(event);
    const center = this.calculateCenter(points);

    // Set up long press timer
    this.longPressTimer = setTimeout(() => {
      this.longPressTimer = null;
    }, this.settings.longPressInterval);

    return {
      type: 'tap',
      details: {
        timestamp: Date.now(),
        touches: points,
        centerX: center.x,
        centerY: center.y,
        distance: 0,
        angle: 0,
        scale: 1,
        velocity: { x: 0, y: 0 },
      },
      timestamp: Date.now(),
    };
  }

  /**
   * Handle touch move
   */
  private handleTouchMove(event: TouchEvent): GestureEvent | null {
    const points = this.touchTracker.onTouchMove(event);
    const center = this.calculateCenter(points);

    // Clear long press timer on move
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer);
      this.longPressTimer = null;
    }

    // Pinch with two fingers
    if (points.length === 2) {
      const distance = this.calculateDistance(points[0], points[1]);
      const previousDistance = this.calculateDistance(
        { ...points[0], x: points[0].previousX, y: points[0].previousY },
        { ...points[1], x: points[1].previousX, y: points[1].previousY }
      );
      const scale = distance / (previousDistance || 1);

      if (Math.abs(scale - 1) > this.settings.minimumPinchScale) {
        return {
          type: 'pinch',
          details: {
            timestamp: Date.now(),
            touches: points,
            centerX: center.x,
            centerY: center.y,
            distance,
            angle: 0,
            scale,
            velocity: { x: 0, y: 0 },
          },
          timestamp: Date.now(),
        };
      }
    }

    // Pan with one or more fingers
    if (points.length > 0) {
      const totalDelta = points.reduce(
        (sum, p) => ({
          x: sum.x + p.deltaX,
          y: sum.y + p.deltaY,
        }),
        { x: 0, y: 0 }
      );

      const avgDelta = {
        x: totalDelta.x / points.length,
        y: totalDelta.y / points.length,
      };

      if (Math.abs(avgDelta.x) + Math.abs(avgDelta.y) > this.settings.minimumPanDistance) {
        return {
          type: 'pan',
          details: {
            timestamp: Date.now(),
            touches: points,
            centerX: center.x,
            centerY: center.y,
            distance: 0,
            angle: 0,
            scale: 1,
            velocity: avgDelta,
          },
          timestamp: Date.now(),
        };
      }
    }

    return null;
  }

  /**
   * Handle touch end
   */
  private handleTouchEnd(event: TouchEvent): GestureEvent | null {
    const { points, duration } = this.touchTracker.onTouchEnd(event);
    const center = this.calculateCenter(points);

    // Tap detection
    if (points.length === 1 && duration < this.settings.maximumTapDuration) {
      const tapPoint = points[0];

      // Check for double tap
      if (
        this.lastTapPosition &&
        Date.now() - this.lastTapTime < this.settings.doubleTapInterval &&
        this.isNearby(this.lastTapPosition, { x: tapPoint.x, y: tapPoint.y }, 50)
      ) {
        this.lastTapTime = 0;
        this.lastTapPosition = null;

        return {
          type: 'double-tap',
          details: {
            timestamp: Date.now(),
            touches: points,
            centerX: center.x,
            centerY: center.y,
            distance: 0,
            angle: 0,
            scale: 1,
            velocity: { x: 0, y: 0 },
          },
          timestamp: Date.now(),
        };
      }

      this.lastTapTime = Date.now();
      this.lastTapPosition = { x: tapPoint.x, y: tapPoint.y };

      return {
        type: 'tap',
        details: {
          timestamp: Date.now(),
          touches: points,
          centerX: center.x,
          centerY: center.y,
          distance: 0,
          angle: 0,
          scale: 1,
          velocity: { x: 0, y: 0 },
        },
        timestamp: Date.now(),
      };
    }

    // Swipe detection (pan with velocity)
    if (points.length > 0 && duration > this.settings.minimumTapDuration) {
      const velocity = this.calculateVelocity(points, duration);
      const speed = Math.sqrt(velocity.x ** 2 + velocity.y ** 2);

      if (speed > 1) {
        let direction: 'up' | 'down' | 'left' | 'right' = 'right';
        const absDeltaX = Math.abs(points[0].x - points[0].previousX);
        const absDeltaY = Math.abs(points[0].y - points[0].previousY);

        if (absDeltaX > absDeltaY) {
          direction = points[0].x - points[0].previousX > 0 ? 'right' : 'left';
        } else {
          direction = points[0].y - points[0].previousY > 0 ? 'down' : 'up';
        }

        return {
          type: 'swipe',
          details: {
            timestamp: Date.now(),
            touches: points,
            centerX: center.x,
            centerY: center.y,
            distance: 0,
            angle: 0,
            scale: 1,
            velocity,
          },
          direction,
          timestamp: Date.now(),
        };
      }
    }

    return null;
  }

  /**
   * Calculate center point of touches
   */
  private calculateCenter(points: TouchPoint[]): { x: number; y: number } {
    if (points.length === 0) return { x: 0, y: 0 };

    const sum = points.reduce(
      (acc, p) => ({ x: acc.x + p.x, y: acc.y + p.y }),
      { x: 0, y: 0 }
    );

    return {
      x: sum.x / points.length,
      y: sum.y / points.length,
    };
  }

  /**
   * Calculate distance between two points
   */
  private calculateDistance(p1: { x: number; y: number }, p2: { x: number; y: number }): number {
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Calculate velocity from points
   */
  private calculateVelocity(points: TouchPoint[], duration: number): { x: number; y: number } {
    if (duration === 0) return { x: 0, y: 0 };

    const avgDelta = points.reduce(
      (sum, p) => ({
        x: sum.x + (p.x - p.previousX),
        y: sum.y + (p.y - p.previousY),
      }),
      { x: 0, y: 0 }
    );

    return {
      x: (avgDelta.x / points.length) / (duration / 1000),
      y: (avgDelta.y / points.length) / (duration / 1000),
    };
  }

  /**
   * Check if points are nearby
   */
  private isNearby(p1: { x: number; y: number }, p2: { x: number; y: number }, threshold: number): boolean {
    const distance = this.calculateDistance(p1, p2);
    return distance < threshold;
  }

  /**
   * Get settings
   */
  getSettings(): MobileCanvasSettings {
    return { ...this.settings };
  }

  /**
   * Update settings
   */
  updateSettings(settings: Partial<MobileCanvasSettings>): void {
    this.settings = { ...this.settings, ...settings };
  }
}

// ============================================================================
// Mobile Responsiveness Service
// ============================================================================

export class MobileResponsivityService {
  private gestureRecognizer = new GestureRecognizer();
  private viewportInfo: ViewportInfo | null = null;
  private uiState: MobileUIState = {
    showToolbar: true,
    toolbarPosition: 'bottom',
    showPropertyPanel: true,
    propertyPanelMode: 'slide-over',
    canvasFullscreen: false,
    showMinimap: false,
    hiddenElements: new Set(['minimap', 'console']),
  };
  private gestures: GestureEvent[] = [];
  private maxGestureHistorySize = 100;

  /**
   * Initialize mobile responsiveness
   */
  initialize(): void {
    try {
      this.updateViewportInfo();
      this.attachEventListeners();
      this.optimizeLayoutForViewport();
      logger.info('[MobileResponsive] Initialized');
    } catch (error) {
      logger.error('[MobileResponsive] Initialization failed', error);
    }
  }

  /**
   * Update viewport information
   */
  private updateViewportInfo(): void {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const isLandscape = width > height;

    let mode: LayoutMode = 'desktop';
    if (width < 480) {
      mode = 'compact';
    } else if (width < 768) {
      mode = 'tablet';
    }

    if (isLandscape) mode = 'landscape' as LayoutMode;

    this.viewportInfo = {
      width,
      height,
      mode,
      isMobile: width < 768,
      isTablet: width >= 480 && width < 1024,
      isDesktop: width >= 1024,
      pixelRatio: window.devicePixelRatio || 1,
    };
  }

  /**
   * Attach event listeners
   */
  private attachEventListeners(): void {
    window.addEventListener('resize', () => this.handleResize());
    window.addEventListener('orientationchange', () => this.handleOrientationChange());

    // Touch events are handled separately
  }

  /**
   * Handle window resize
   */
  private handleResize(): void {
    this.updateViewportInfo();
    this.optimizeLayoutForViewport();
    logger.debug(`[MobileResponsive] Resized to ${this.viewportInfo?.width}x${this.viewportInfo?.height}`);
  }

  /**
   * Handle orientation change
   */
  private handleOrientationChange(): void {
    this.updateViewportInfo();
    this.optimizeLayoutForViewport();
    logger.info(`[MobileResponsive] Orientation changed to ${this.viewportInfo?.mode}`);
  }

  /**
   * Optimize layout for viewport
   */
  private optimizeLayoutForViewport(): void {
    if (!this.viewportInfo) return;

    const { isMobile, isTablet, mode } = this.viewportInfo;

    if (isMobile) {
      // Mobile layout
      this.uiState.toolbarPosition = 'bottom';
      this.uiState.propertyPanelMode = 'bottom-sheet';
      this.uiState.showMinimap = false;
      this.uiState.hiddenElements.add('minimap');
    } else if (isTablet) {
      // Tablet layout
      this.uiState.toolbarPosition = 'top';
      this.uiState.propertyPanelMode = 'slide-over';
      this.uiState.showMinimap = false;
    } else {
      // Desktop layout
      this.uiState.toolbarPosition = 'top';
      this.uiState.propertyPanelMode = 'slide-over';
      this.uiState.showMinimap = true;
      this.uiState.hiddenElements.delete('minimap');
    }
  }

  /**
   * Handle touch event
   */
  handleTouchEvent(event: TouchEvent): GestureEvent | null {
    const gesture = this.gestureRecognizer.recognizeGesture(event);

    if (gesture) {
      this.gestures.push(gesture);
      if (this.gestures.length > this.maxGestureHistorySize) {
        this.gestures.shift();
      }

      logger.debug(`[MobileResponsive] Gesture: ${gesture.type}`);
    }

    return gesture;
  }

  /**
   * Get current viewport info
   */
  getViewportInfo(): ViewportInfo | null {
    this.updateViewportInfo();
    return this.viewportInfo ? { ...this.viewportInfo } : null;
  }

  /**
   * Get UI state
   */
  getUIState(): MobileUIState {
    return JSON.parse(JSON.stringify(this.uiState));
  }

  /**
   * Update UI state
   */
  updateUIState(updates: Partial<MobileUIState>): void {
    this.uiState = { ...this.uiState, ...updates };
    logger.debug('[MobileResponsive] UI state updated');
  }

  /**
   * Toggle fullscreen mode
   */
  toggleCanvasFullscreen(): void {
    this.uiState.canvasFullscreen = !this.uiState.canvasFullscreen;
    logger.info(`[MobileResponsive] Fullscreen: ${this.uiState.canvasFullscreen}`);
  }

  /**
   * Get gesture history
   */
  getGestureHistory(): GestureEvent[] {
    return [...this.gestures];
  }

  /**
   * Clear gesture history
   */
  clearGestureHistory(): void {
    this.gestures = [];
  }

  /**
   * Is mobile device
   */
  isMobile(): boolean {
    return this.viewportInfo?.isMobile ?? false;
  }

  /**
   * Is tablet device
   */
  isTablet(): boolean {
    return this.viewportInfo?.isTablet ?? false;
  }

  /**
   * Get layout mode
   */
  getLayoutMode(): LayoutMode {
    return this.viewportInfo?.mode ?? 'desktop';
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const mobileResponsivity = new MobileResponsivityService();

// Default export
export default mobileResponsivity;
