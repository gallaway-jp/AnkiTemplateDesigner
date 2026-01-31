/**
 * Dependency Injection Service for PythonBridge
 * Enables testing with mock implementations and configuration flexibility
 */

import { PythonBridge } from './pythonBridge';

export interface PythonBridgeFactory {
  create(): PythonBridge;
}

export interface IPythonBridge {
  initialize(): Promise<void>;
  sendRequest(request: any): Promise<any>;
  disconnect(): void;
  isConnected(): boolean;
  health(): Promise<any>;
  requestQueue(): any;
  requestMetrics(): any;
}

/**
 * Dependency injection container for PythonBridge
 * Allows swapping implementations for testing
 */
export class PythonBridgeProvider {
  private static instance: PythonBridge | null = null;
  private static factory: PythonBridgeFactory | null = null;

  /**
   * Set a custom factory for creating PythonBridge instances
   * Useful for testing with mocks
   */
  static setFactory(factory: PythonBridgeFactory): void {
    PythonBridgeProvider.factory = factory;
    PythonBridgeProvider.instance = null; // Reset instance when factory changes
  }

  /**
   * Get the current PythonBridge instance
   */
  static getInstance(): PythonBridge {
    if (!PythonBridgeProvider.instance) {
      if (PythonBridgeProvider.factory) {
        PythonBridgeProvider.instance = PythonBridgeProvider.factory.create();
      } else {
        PythonBridgeProvider.instance = new PythonBridge();
      }
    }
    return PythonBridgeProvider.instance;
  }

  /**
   * Reset to default factory
   */
  static reset(): void {
    PythonBridgeProvider.factory = null;
    PythonBridgeProvider.instance = null;
  }
}

/**
 * Mock factory for testing
 */
export class MockPythonBridgeFactory implements PythonBridgeFactory {
  private mockBridge: any;

  constructor(mockBridge: any) {
    this.mockBridge = mockBridge;
  }

  create(): PythonBridge {
    return this.mockBridge;
  }
}
