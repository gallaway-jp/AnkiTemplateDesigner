/**
 * Event Bus - Centralized event-driven architecture
 * Allows decoupled component communication via publish/subscribe pattern
 */

export class EventBus {
  private listeners: Map<string, Function[]> = new Map();

  /**
   * Subscribe to an event
   * @param event Event name
   * @param handler Callback function
   * @returns Unsubscribe function
   */
  on<T>(event: string, handler: (data: T) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.listeners.get(event) || [];
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    };
  }

  /**
   * Emit an event
   * @param event Event name
   * @param data Event data
   */
  emit<T>(event: string, data: T): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for '${event}':`, error);
        }
      });
    }
  }

  /**
   * Remove all listeners for an event
   * @param event Event name
   */
  off(event: string): void {
    this.listeners.delete(event);
  }

  /**
   * Remove all listeners for all events
   */
  clear(): void {
    this.listeners.clear();
  }

  /**
   * Check if event has listeners
   * @param event Event name
   */
  hasListeners(event: string): boolean {
    return this.listeners.has(event) && (this.listeners.get(event)?.length ?? 0) > 0;
  }

  /**
   * Get listener count for an event
   * @param event Event name
   */
  getListenerCount(event: string): number {
    return this.listeners.get(event)?.length ?? 0;
  }
}

// Global instance
export const eventBus = new EventBus();
