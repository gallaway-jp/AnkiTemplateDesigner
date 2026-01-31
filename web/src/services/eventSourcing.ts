/**
 * Event Sourcing Pattern - Complete audit trail and replay capabilities
 * Stores changes as a sequence of immutable events
 */

/**
 * Domain event interface
 * Represents something that happened in the system
 */
export interface DomainEvent {
  id: string;
  type: string;
  timestamp: number;
  aggregateId: string;
  version: number;
  data: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * Event store interface
 * Responsible for storing and retrieving events
 */
export interface IEventStore {
  append(event: DomainEvent): Promise<void>;
  getEvents(aggregateId: string): Promise<DomainEvent[]>;
  getAllEvents(): Promise<DomainEvent[]>;
  getEventsByType(type: string): Promise<DomainEvent[]>;
  getEventsSince(timestamp: number): Promise<DomainEvent[]>;
}

/**
 * In-memory event store implementation
 */
export class InMemoryEventStore implements IEventStore {
  private events: DomainEvent[] = [];

  async append(event: DomainEvent): Promise<void> {
    this.events.push(event);
  }

  async getEvents(aggregateId: string): Promise<DomainEvent[]> {
    return this.events.filter((e) => e.aggregateId === aggregateId);
  }

  async getAllEvents(): Promise<DomainEvent[]> {
    return [...this.events];
  }

  async getEventsByType(type: string): Promise<DomainEvent[]> {
    return this.events.filter((e) => e.type === type);
  }

  async getEventsSince(timestamp: number): Promise<DomainEvent[]> {
    return this.events.filter((e) => e.timestamp >= timestamp);
  }

  /**
   * Get events in a time range
   */
  async getEventsByDateRange(
    from: number,
    to: number
  ): Promise<DomainEvent[]> {
    return this.events.filter((e) => e.timestamp >= from && e.timestamp <= to);
  }

  /**
   * Clear all events (for testing)
   */
  clear(): void {
    this.events = [];
  }

  /**
   * Get event count
   */
  getEventCount(): number {
    return this.events.length;
  }
}

/**
 * Aggregate root base class
 * Encapsulates domain logic and event sourcing
 */
export abstract class AggregateRoot {
  protected id: string;
  protected version: number = 0;
  protected uncommittedEvents: DomainEvent[] = [];

  constructor(id: string) {
    this.id = id;
  }

  /**
   * Get aggregate ID
   */
  getId(): string {
    return this.id;
  }

  /**
   * Get current version
   */
  getVersion(): number {
    return this.version;
  }

  /**
   * Apply event and update state
   */
  protected applyEvent(event: DomainEvent): void {
    this.version++;
  }

  /**
   * Raise a domain event
   */
  protected raiseEvent(
    type: string,
    data: Record<string, any>,
    metadata?: Record<string, any>
  ): void {
    const event: DomainEvent = {
      id: `event-${Date.now()}-${Math.random()}`,
      type,
      timestamp: Date.now(),
      aggregateId: this.id,
      version: this.version + 1,
      data,
      metadata,
    };

    this.applyEvent(event);
    this.uncommittedEvents.push(event);
  }

  /**
   * Get uncommitted events
   */
  getUncommittedEvents(): DomainEvent[] {
    return this.uncommittedEvents;
  }

  /**
   * Mark events as committed
   */
  markEventsAsCommitted(): void {
    this.uncommittedEvents = [];
  }

  /**
   * Replay events to rebuild state
   */
  loadFromHistory(events: DomainEvent[]): void {
    events.forEach((event) => {
      this.applyEvent(event);
    });
  }
}

/**
 * Event projector
 * Creates read models from events
 */
export class EventProjector {
  private projections: Map<string, any> = new Map();
  private projectors: Map<
    string,
    (event: DomainEvent, projection: any) => any
  > = new Map();

  /**
   * Register a projector for an event type
   */
  registerProjector(
    eventType: string,
    projector: (event: DomainEvent, projection: any) => any
  ): void {
    this.projectors.set(eventType, projector);
  }

  /**
   * Project an event
   */
  project(
    key: string,
    event: DomainEvent,
    initialValue: any = {}
  ): any {
    const currentProjection = this.projections.get(key) || initialValue;
    const projector = this.projectors.get(event.type);

    if (!projector) {
      return currentProjection;
    }

    const newProjection = projector(event, currentProjection);
    this.projections.set(key, newProjection);

    return newProjection;
  }

  /**
   * Get projection
   */
  getProjection(key: string): any {
    return this.projections.get(key);
  }

  /**
   * Clear all projections
   */
  clear(): void {
    this.projections.clear();
  }
}

/**
 * Event sourced repository
 * Manages aggregates with event sourcing
 */
export class EventSourcedRepository<T extends AggregateRoot> {
  constructor(
    private eventStore: IEventStore,
    private AggregateClass: new (id: string) => T
  ) {}

  /**
   * Save aggregate
   */
  async save(aggregate: T): Promise<void> {
    const events = aggregate.getUncommittedEvents();

    for (const event of events) {
      await this.eventStore.append(event);
    }

    aggregate.markEventsAsCommitted();
  }

  /**
   * Get aggregate by ID
   */
  async getById(id: string): Promise<T | null> {
    const events = await this.eventStore.getEvents(id);

    if (events.length === 0) {
      return null;
    }

    const aggregate = new this.AggregateClass(id);
    aggregate.loadFromHistory(events);

    return aggregate;
  }

  /**
   * Get all aggregates
   */
  async getAll(): Promise<T[]> {
    const allEvents = await this.eventStore.getAllEvents();
    const aggregates = new Map<string, T>();

    for (const event of allEvents) {
      const id = event.aggregateId;
      if (!aggregates.has(id)) {
        aggregates.set(id, new this.AggregateClass(id));
      }
      aggregates.get(id)!.loadFromHistory([event]);
    }

    return Array.from(aggregates.values());
  }

  /**
   * Delete aggregate (records deletion event)
   */
  async delete(id: string): Promise<void> {
    const aggregate = await this.getById(id);
    if (aggregate) {
      // Create deletion event
      const deletionEvent: DomainEvent = {
        id: `event-${Date.now()}-${Math.random()}`,
        type: 'AggregateDeleted',
        timestamp: Date.now(),
        aggregateId: id,
        version: aggregate.getVersion() + 1,
        data: { deletedAt: Date.now() },
      };

      await this.eventStore.append(deletionEvent);
    }
  }
}

/**
 * Event replay service
 * Replays events for auditing and debugging
 */
export class EventReplayService {
  constructor(private eventStore: IEventStore) {}

  /**
   * Get full history for aggregate
   */
  async getHistory(aggregateId: string): Promise<DomainEvent[]> {
    return this.eventStore.getEvents(aggregateId);
  }

  /**
   * Get history between timestamps
   */
  async getHistoryInRange(
    aggregateId: string,
    from: number,
    to: number
  ): Promise<DomainEvent[]> {
    const allEvents = await this.eventStore.getEvents(aggregateId);
    return allEvents.filter((e) => e.timestamp >= from && e.timestamp <= to);
  }

  /**
   * Get snapshot at specific version
   */
  async getSnapshotAtVersion<T extends AggregateRoot>(
    aggregateId: string,
    version: number,
    AggregateClass: new (id: string) => T
  ): Promise<T | null> {
    const allEvents = await this.eventStore.getEvents(aggregateId);
    const eventsUpToVersion = allEvents.filter((e) => e.version <= version);

    if (eventsUpToVersion.length === 0) {
      return null;
    }

    const aggregate = new AggregateClass(aggregateId);
    aggregate.loadFromHistory(eventsUpToVersion);

    return aggregate;
  }

  /**
   * Audit trail
   */
  async getAuditTrail(aggregateId: string): Promise<string> {
    const events = await this.getHistory(aggregateId);
    const lines = events.map(
      (e) =>
        `[${new Date(e.timestamp).toISOString()}] ${e.type}: ${JSON.stringify(e.data)}`
    );

    return lines.join('\n');
  }

  /**
   * Find events by criteria
   */
  async searchEvents(
    predicate: (event: DomainEvent) => boolean
  ): Promise<DomainEvent[]> {
    const allEvents = await this.eventStore.getAllEvents();
    return allEvents.filter(predicate);
  }
}

/**
 * Snapshot store for performance optimization
 */
export interface Snapshot<T> {
  aggregateId: string;
  version: number;
  state: T;
  timestamp: number;
}

/**
 * Snapshot repository
 */
export class SnapshotRepository<T> {
  private snapshots: Map<string, Snapshot<T>> = new Map();

  /**
   * Save snapshot
   */
  saveSnapshot(snapshot: Snapshot<T>): void {
    this.snapshots.set(snapshot.aggregateId, snapshot);
  }

  /**
   * Get latest snapshot
   */
  getLatestSnapshot(aggregateId: string): Snapshot<T> | null {
    return this.snapshots.get(aggregateId) || null;
  }

  /**
   * Delete snapshot
   */
  deleteSnapshot(aggregateId: string): void {
    this.snapshots.delete(aggregateId);
  }

  /**
   * Clear all snapshots
   */
  clear(): void {
    this.snapshots.clear();
  }

  /**
   * Get snapshot count
   */
  getSnapshotCount(): number {
    return this.snapshots.size;
  }
}
