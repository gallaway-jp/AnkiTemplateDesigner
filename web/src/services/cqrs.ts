/**
 * CQRS Pattern - Command Query Responsibility Segregation
 * Separates read and write operations for improved scalability and performance
 */

/**
 * Command interface
 * Represents a write operation that changes state
 */
export interface Command<TInput, TOutput> {
  execute(data: TInput): Promise<TOutput>;
  undo?(): Promise<void>;
  canExecute?(data: TInput): boolean;
}

/**
 * Query interface
 * Represents a read operation that retrieves state
 */
export interface Query<TInput, TOutput> {
  execute(criteria: TInput): Promise<TOutput>;
}

/**
 * Base command class with common functionality
 */
export abstract class BaseCommand<TInput, TOutput>
  implements Command<TInput, TOutput>
{
  protected lastInput?: TInput;
  protected lastOutput?: TOutput;

  abstract execute(data: TInput): Promise<TOutput>;

  canExecute(data: TInput): boolean {
    return true;
  }

  undo(): Promise<void> {
    throw new Error('Undo not implemented');
  }

  getLastInput(): TInput | undefined {
    return this.lastInput;
  }

  getLastOutput(): TOutput | undefined {
    return this.lastOutput;
  }
}

/**
 * Base query class with common functionality
 */
export abstract class BaseQuery<TInput, TOutput>
  implements Query<TInput, TOutput>
{
  abstract execute(criteria: TInput): Promise<TOutput>;
}

/**
 * Command bus for routing and executing commands
 */
export class CommandBus {
  private commands: Map<string, Command<any, any>> = new Map();
  private interceptors: Array<(name: string, input: any) => Promise<void>> =
    [];

  /**
   * Register a command
   */
  register<TInput, TOutput>(
    name: string,
    command: Command<TInput, TOutput>
  ): void {
    this.commands.set(name, command);
  }

  /**
   * Execute a command
   */
  async execute<TOutput = any>(name: string, data?: any): Promise<TOutput> {
    const command = this.commands.get(name);
    if (!command) {
      throw new Error(`Command '${name}' not registered`);
    }

    // Run interceptors
    for (const interceptor of this.interceptors) {
      await interceptor(name, data);
    }

    if (command.canExecute && !command.canExecute(data)) {
      throw new Error(`Command '${name}' cannot execute with given data`);
    }

    return command.execute(data);
  }

  /**
   * Undo last command
   */
  async undo(name: string): Promise<void> {
    const command = this.commands.get(name);
    if (!command || !command.undo) {
      throw new Error(`Cannot undo command '${name}'`);
    }

    await command.undo();
  }

  /**
   * Add command interceptor
   */
  addInterceptor(
    interceptor: (name: string, input: any) => Promise<void>
  ): void {
    this.interceptors.push(interceptor);
  }

  /**
   * Check if command exists
   */
  has(name: string): boolean {
    return this.commands.has(name);
  }

  /**
   * Get registered command names
   */
  getCommandNames(): string[] {
    return Array.from(this.commands.keys());
  }
}

/**
 * Query bus for routing and executing queries
 */
export class QueryBus {
  private queries: Map<string, Query<any, any>> = new Map();
  private cache: Map<string, { result: any; timestamp: number }> = new Map();
  private cacheExpiry = 5000; // 5 seconds

  /**
   * Register a query
   */
  register<TInput, TOutput>(
    name: string,
    query: Query<TInput, TOutput>
  ): void {
    this.queries.set(name, query);
  }

  /**
   * Execute a query
   */
  async execute<TOutput = any>(
    name: string,
    criteria?: any,
    useCache: boolean = true
  ): Promise<TOutput> {
    const cacheKey = `${name}:${JSON.stringify(criteria || {})}`;

    // Check cache
    if (useCache) {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
        return cached.result;
      }
    }

    const query = this.queries.get(name);
    if (!query) {
      throw new Error(`Query '${name}' not registered`);
    }

    const result = await query.execute(criteria);

    // Cache result
    this.cache.set(cacheKey, { result, timestamp: Date.now() });

    return result;
  }

  /**
   * Check if query exists
   */
  has(name: string): boolean {
    return this.queries.has(name);
  }

  /**
   * Get registered query names
   */
  getQueryNames(): string[] {
    return Array.from(this.queries.keys());
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Set cache expiry time
   */
  setCacheExpiry(ms: number): void {
    this.cacheExpiry = ms;
  }
}

/**
 * CQRS Handler - Combines command and query buses
 */
export class CQRSHandler {
  private commandBus: CommandBus;
  private queryBus: QueryBus;

  constructor() {
    this.commandBus = new CommandBus();
    this.queryBus = new QueryBus();
  }

  /**
   * Register command
   */
  registerCommand<TInput, TOutput>(
    name: string,
    command: Command<TInput, TOutput>
  ): void {
    this.commandBus.register(name, command);
  }

  /**
   * Register query
   */
  registerQuery<TInput, TOutput>(
    name: string,
    query: Query<TInput, TOutput>
  ): void {
    this.queryBus.register(name, query);
  }

  /**
   * Execute command
   */
  async command<TOutput = any>(name: string, data?: any): Promise<TOutput> {
    const result = await this.commandBus.execute<TOutput>(name, data);
    // Invalidate queries after command execution
    this.queryBus.clearCache();
    return result;
  }

  /**
   * Execute query
   */
  async query<TOutput = any>(
    name: string,
    criteria?: any,
    useCache?: boolean
  ): Promise<TOutput> {
    return this.queryBus.execute<TOutput>(name, criteria, useCache);
  }

  /**
   * Get command bus
   */
  getCommandBus(): CommandBus {
    return this.commandBus;
  }

  /**
   * Get query bus
   */
  getQueryBus(): QueryBus {
    return this.queryBus;
  }

  /**
   * Get all registered handlers
   */
  getRegistered(): {
    commands: string[];
    queries: string[];
  } {
    return {
      commands: this.commandBus.getCommandNames(),
      queries: this.queryBus.getQueryNames(),
    };
  }
}

/**
 * Global CQRS handler instance
 */
export const cqrsHandler = new CQRSHandler();
