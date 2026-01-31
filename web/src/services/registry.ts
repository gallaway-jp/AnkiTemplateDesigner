/**
 * Service Registry - Centralized service management and lifecycle
 * Manages service initialization, access, and cleanup
 */

export interface ServiceConfig {
  onInit?: () => Promise<void>;
  onDestroy?: () => Promise<void>;
  singleton?: boolean;
}

export class ServiceRegistry {
  private services: Map<string, any> = new Map();
  private initializers: Map<string, () => Promise<void>> = new Map();
  private destroyers: Map<string, () => Promise<void>> = new Map();
  private initialized: Set<string> = new Set();

  /**
   * Register a service
   * @param name Service name
   * @param factory Factory function to create service
   * @param config Service configuration
   */
  register<T>(name: string, factory: () => T, config?: ServiceConfig): void {
    if (this.services.has(name)) {
      console.warn(`Service ${name} is already registered, replacing it`);
    }

    const instance = factory();
    this.services.set(name, instance);

    if (config?.onInit) {
      this.initializers.set(name, config.onInit);
    }

    if (config?.onDestroy) {
      this.destroyers.set(name, config.onDestroy);
    }
  }

  /**
   * Initialize a specific service
   * @param name Service name
   */
  async initialize(name: string): Promise<void> {
    if (this.initialized.has(name)) {
      return;
    }

    const initializer = this.initializers.get(name);
    if (initializer) {
      try {
        await initializer();
        this.initialized.add(name);
      } catch (error) {
        console.error(`Failed to initialize service ${name}:`, error);
        throw new Error(`Failed to initialize service ${name}: ${error}`);
      }
    } else {
      this.initialized.add(name);
    }
  }

  /**
   * Initialize all registered services
   */
  async initializeAll(): Promise<void> {
    const promises = Array.from(this.initializers.keys())
      .filter((name) => !this.initialized.has(name))
      .map((name) =>
        this.initialize(name).catch((e) => {
          console.error(`Failed to initialize ${name}:`, e);
        })
      );

    await Promise.all(promises);
  }

  /**
   * Get a service instance
   * @param name Service name
   * @returns Service instance
   */
  get<T>(name: string): T {
    const service = this.services.get(name);
    if (!service) {
      throw new Error(`Service ${name} not registered`);
    }
    return service as T;
  }

  /**
   * Check if a service is registered
   * @param name Service name
   */
  has(name: string): boolean {
    return this.services.has(name);
  }

  /**
   * Destroy a specific service
   * @param name Service name
   */
  async destroy(name: string): Promise<void> {
    const destroyer = this.destroyers.get(name);
    if (destroyer) {
      try {
        await destroyer();
      } catch (error) {
        console.error(`Failed to destroy service ${name}:`, error);
      }
    }
    this.services.delete(name);
    this.initialized.delete(name);
  }

  /**
   * Destroy all services
   */
  async destroyAll(): Promise<void> {
    const names = Array.from(this.destroyers.keys());
    const promises = names.map((name) => this.destroy(name));
    await Promise.all(promises);
  }

  /**
   * Get list of registered service names
   */
  getServiceNames(): string[] {
    return Array.from(this.services.keys());
  }

  /**
   * Get initialization status
   */
  getInitializationStatus(): Record<string, boolean> {
    const status: Record<string, boolean> = {};
    this.services.forEach((_, name) => {
      status[name] = this.initialized.has(name);
    });
    return status;
  }
}

// Global instance
export const registry = new ServiceRegistry();
