import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  cqrsHandler,
  CommandBus,
  QueryBus,
  BaseCommand,
  BaseQuery,
  CQRSHandler,
} from '../services/cqrs';
import {
  InMemoryEventStore,
  EventProjector,
  EventSourcedRepository,
  AggregateRoot,
  EventReplayService,
  SnapshotRepository,
  DomainEvent,
} from '../services/eventSourcing';

// ==================== CQRS Tests ====================

describe('CQRS Pattern', () => {
  describe('CommandBus', () => {
    let commandBus: CommandBus;

    beforeEach(() => {
      commandBus = new CommandBus();
    });

    it('should register and execute command', async () => {
      class TestCommand extends BaseCommand {
        constructor(public value: string) {
          super();
        }

        async execute(): Promise<any> {
          return `executed: ${this.value}`;
        }
      }

      commandBus.registerCommand('test', TestCommand);
      const result = await commandBus.execute('test', { value: 'hello' });

      expect(result).toBe('executed: hello');
    });

    it('should throw on unregistered command', async () => {
      await expect(commandBus.execute('unknown', {})).rejects.toThrow();
    });

    it('should support command interception', async () => {
      const interceptor = vi.fn(async (name: string, params: any) => {
        params.intercepted = true;
        return params;
      });

      class TestCommand extends BaseCommand {
        async execute(params: any): Promise<any> {
          return params;
        }
      }

      commandBus.addInterceptor(interceptor);
      commandBus.registerCommand('test', TestCommand);

      const result = await commandBus.execute('test', { value: 'hello' });
      expect(interceptor).toHaveBeenCalled();
    });

    it('should track command history', async () => {
      class TestCommand extends BaseCommand {
        async execute(): Promise<any> {
          return 'done';
        }

        async undo(): Promise<void> {
          // undo implementation
        }
      }

      commandBus.registerCommand('test', TestCommand);
      await commandBus.execute('test', {});

      const history = commandBus.getHistory();
      expect(history.length).toBe(1);
    });

    it('should support undo operation', async () => {
      const undoFn = vi.fn();

      class TestCommand extends BaseCommand {
        async execute(): Promise<any> {
          return 'done';
        }

        async undo(): Promise<void> {
          undoFn();
        }
      }

      commandBus.registerCommand('test', TestCommand);
      const commandId = await commandBus.execute('test', {});
      await commandBus.undo(commandId);

      expect(undoFn).toHaveBeenCalled();
    });

    it('should clear history', () => {
      class TestCommand extends BaseCommand {
        async execute(): Promise<any> {
          return 'done';
        }
      }

      commandBus.registerCommand('test', TestCommand);
      commandBus.clearHistory();

      expect(commandBus.getHistory().length).toBe(0);
    });
  });

  describe('QueryBus', () => {
    let queryBus: QueryBus;

    beforeEach(() => {
      queryBus = new QueryBus();
    });

    it('should register and execute query', async () => {
      class TestQuery extends BaseQuery {
        constructor(public id: string) {
          super();
        }

        async execute(): Promise<any> {
          return { id: this.id, name: 'test' };
        }
      }

      queryBus.registerQuery('test', TestQuery);
      const result = await queryBus.execute('test', { id: '123' });

      expect(result.id).toBe('123');
      expect(result.name).toBe('test');
    });

    it('should cache query results', async () => {
      const executeFn = vi.fn(async () => ({ cached: true }));

      class TestQuery extends BaseQuery {
        async execute(): Promise<any> {
          return executeFn();
        }
      }

      queryBus.registerQuery('test', TestQuery);

      const result1 = await queryBus.execute('test', { id: '123' });
      const result2 = await queryBus.execute('test', { id: '123' });

      expect(result1).toEqual(result2);
      expect(executeFn).toHaveBeenCalledOnce();
    });

    it('should invalidate cache', async () => {
      const executeFn = vi.fn(async () => ({ value: Math.random() }));

      class TestQuery extends BaseQuery {
        async execute(): Promise<any> {
          return executeFn();
        }
      }

      queryBus.registerQuery('test', TestQuery);

      const result1 = await queryBus.execute('test', { id: '123' });
      queryBus.invalidateCache('test');
      const result2 = await queryBus.execute('test', { id: '123' });

      expect(result1).not.toEqual(result2);
      expect(executeFn).toHaveBeenCalledTimes(2);
    });

    it('should throw on unregistered query', async () => {
      await expect(queryBus.execute('unknown', {})).rejects.toThrow();
    });

    it('should clear all caches', async () => {
      const executeFn = vi.fn(async () => ({ value: Math.random() }));

      class TestQuery extends BaseQuery {
        async execute(): Promise<any> {
          return executeFn();
        }
      }

      queryBus.registerQuery('test1', TestQuery);
      queryBus.registerQuery('test2', TestQuery);

      await queryBus.execute('test1', { id: '1' });
      await queryBus.execute('test2', { id: '2' });

      queryBus.clearAllCaches();

      await queryBus.execute('test1', { id: '1' });
      await queryBus.execute('test2', { id: '2' });

      expect(executeFn).toHaveBeenCalledTimes(4);
    });

    it('should support custom cache TTL', async () => {
      vi.useFakeTimers();
      const executeFn = vi.fn(async () => ({ value: Math.random() }));

      class TestQuery extends BaseQuery {
        async execute(): Promise<any> {
          return executeFn();
        }
      }

      queryBus.registerQuery('test', TestQuery);

      const result1 = await queryBus.execute('test', { id: '123' }, 1000);
      vi.advanceTimersByTime(500);
      const result2 = await queryBus.execute('test', { id: '123' });

      expect(result1).toEqual(result2);

      vi.advanceTimersByTime(600);
      const result3 = await queryBus.execute('test', { id: '123' });

      expect(result1).not.toEqual(result3);
      expect(executeFn).toHaveBeenCalledTimes(2);

      vi.useRealTimers();
    });
  });

  describe('CQRSHandler', () => {
    let handler: CQRSHandler;

    beforeEach(() => {
      handler = new CQRSHandler();
    });

    it('should provide access to command bus', () => {
      const commandBus = handler.getCommandBus();
      expect(commandBus).toBeDefined();
      expect(commandBus).toBeInstanceOf(CommandBus);
    });

    it('should provide access to query bus', () => {
      const queryBus = handler.getQueryBus();
      expect(queryBus).toBeDefined();
      expect(queryBus).toBeInstanceOf(QueryBus);
    });

    it('should execute commands through handler', async () => {
      class TestCommand extends BaseCommand {
        async execute(params: any): Promise<any> {
          return `cmd: ${params.msg}`;
        }
      }

      handler.registerCommand('test', TestCommand);
      const result = await handler.command('test', { msg: 'hello' });

      expect(result).toBe('cmd: hello');
    });

    it('should execute queries through handler', async () => {
      class TestQuery extends BaseQuery {
        async execute(params: any): Promise<any> {
          return `query: ${params.msg}`;
        }
      }

      handler.registerQuery('test', TestQuery);
      const result = await handler.query('test', { msg: 'hello' });

      expect(result).toBe('query: hello');
    });

    it('should handle concurrent commands', async () => {
      class SlowCommand extends BaseCommand {
        async execute(params: any): Promise<any> {
          return new Promise((resolve) =>
            setTimeout(() => resolve(`cmd: ${params.id}`), 100)
          );
        }
      }

      handler.registerCommand('slow', SlowCommand);

      const promises = Array.from({ length: 5 }, (_, i) =>
        handler.command('slow', { id: i })
      );

      const results = await Promise.all(promises);
      expect(results).toHaveLength(5);
    });

    it('should handle concurrent queries with caching', async () => {
      const executeFn = vi.fn(async () => ({ data: 'cached' }));

      class TestQuery extends BaseQuery {
        async execute(): Promise<any> {
          return executeFn();
        }
      }

      handler.registerQuery('test', TestQuery);

      const promises = Array.from({ length: 5 }, () =>
        handler.query('test', {})
      );

      const results = await Promise.all(promises);
      expect(results).toHaveLength(5);
      expect(executeFn).toHaveBeenCalledOnce();
    });
  });

  describe('Global cqrsHandler instance', () => {
    it('should be available for direct use', async () => {
      class TestCommand extends BaseCommand {
        async execute(): Promise<any> {
          return 'global';
        }
      }

      cqrsHandler.registerCommand('global-test', TestCommand);
      const result = await cqrsHandler.command('global-test', {});

      expect(result).toBe('global');
    });
  });
});

// ==================== Event Sourcing Tests ====================

describe('Event Sourcing Pattern', () => {
  describe('InMemoryEventStore', () => {
    let store: InMemoryEventStore;

    beforeEach(() => {
      store = new InMemoryEventStore();
    });

    it('should append events', async () => {
      const event: DomainEvent = {
        id: '1',
        type: 'TestEvent',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 1,
        data: { value: 'test' },
      };

      await store.append(event);
      const events = await store.getEvents('agg-1');

      expect(events).toHaveLength(1);
      expect(events[0].type).toBe('TestEvent');
    });

    it('should retrieve events by aggregate ID', async () => {
      const event1: DomainEvent = {
        id: '1',
        type: 'Event1',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'Event2',
        timestamp: Date.now(),
        aggregateId: 'agg-2',
        version: 1,
        data: {},
      };

      await store.append(event1);
      await store.append(event2);

      const events1 = await store.getEvents('agg-1');
      const events2 = await store.getEvents('agg-2');

      expect(events1).toHaveLength(1);
      expect(events2).toHaveLength(1);
    });

    it('should retrieve all events', async () => {
      const event1: DomainEvent = {
        id: '1',
        type: 'Event1',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'Event2',
        timestamp: Date.now(),
        aggregateId: 'agg-2',
        version: 1,
        data: {},
      };

      await store.append(event1);
      await store.append(event2);

      const allEvents = await store.getAllEvents();
      expect(allEvents).toHaveLength(2);
    });

    it('should filter events by type', async () => {
      const event1: DomainEvent = {
        id: '1',
        type: 'Created',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'Updated',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 2,
        data: {},
      };

      await store.append(event1);
      await store.append(event2);

      const createdEvents = await store.getEventsByType('Created');
      expect(createdEvents).toHaveLength(1);
      expect(createdEvents[0].type).toBe('Created');
    });

    it('should filter events by timestamp range', async () => {
      const now = Date.now();

      const event1: DomainEvent = {
        id: '1',
        type: 'Event1',
        timestamp: now - 1000,
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'Event2',
        timestamp: now,
        aggregateId: 'agg-1',
        version: 2,
        data: {},
      };

      await store.append(event1);
      await store.append(event2);

      const rangeEvents = await store.getEventsByDateRange(now - 500, now + 500);
      expect(rangeEvents).toHaveLength(1);
      expect(rangeEvents[0].id).toBe('2');
    });

    it('should get events since timestamp', async () => {
      const now = Date.now();

      const event1: DomainEvent = {
        id: '1',
        type: 'Event1',
        timestamp: now - 1000,
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'Event2',
        timestamp: now,
        aggregateId: 'agg-1',
        version: 2,
        data: {},
      };

      await store.append(event1);
      await store.append(event2);

      const events = await store.getEventsSince(now - 500);
      expect(events).toHaveLength(1);
      expect(events[0].id).toBe('2');
    });

    it('should clear all events', async () => {
      const event: DomainEvent = {
        id: '1',
        type: 'Event',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      await store.append(event);
      store.clear();

      const events = await store.getAllEvents();
      expect(events).toHaveLength(0);
    });

    it('should track event count', async () => {
      expect(store.getEventCount()).toBe(0);

      const event: DomainEvent = {
        id: '1',
        type: 'Event',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 1,
        data: {},
      };

      await store.append(event);
      expect(store.getEventCount()).toBe(1);
    });
  });

  describe('AggregateRoot', () => {
    class TestAggregate extends AggregateRoot {
      private state: any = {};

      setState(data: any): void {
        this.raiseEvent('StateChanged', data);
      }

      getState(): any {
        return this.state;
      }

      protected applyEvent(event: DomainEvent): void {
        super.applyEvent(event);
        if (event.type === 'StateChanged') {
          this.state = event.data;
        }
      }
    }

    it('should create aggregate with ID', () => {
      const aggregate = new TestAggregate('test-1');
      expect(aggregate.getId()).toBe('test-1');
      expect(aggregate.getVersion()).toBe(0);
    });

    it('should raise and track events', () => {
      const aggregate = new TestAggregate('test-1');
      aggregate.setState({ value: 'test' });

      const events = aggregate.getUncommittedEvents();
      expect(events).toHaveLength(1);
      expect(events[0].type).toBe('StateChanged');
    });

    it('should mark events as committed', () => {
      const aggregate = new TestAggregate('test-1');
      aggregate.setState({ value: 'test' });

      aggregate.markEventsAsCommitted();
      const events = aggregate.getUncommittedEvents();

      expect(events).toHaveLength(0);
    });

    it('should rebuild state from history', () => {
      const events: DomainEvent[] = [
        {
          id: '1',
          type: 'StateChanged',
          timestamp: Date.now(),
          aggregateId: 'test-1',
          version: 1,
          data: { value: 'first' },
        },
        {
          id: '2',
          type: 'StateChanged',
          timestamp: Date.now(),
          aggregateId: 'test-1',
          version: 2,
          data: { value: 'second' },
        },
      ];

      const aggregate = new TestAggregate('test-1');
      aggregate.loadFromHistory(events);

      expect(aggregate.getVersion()).toBe(2);
      expect(aggregate.getState().value).toBe('second');
    });
  });

  describe('EventProjector', () => {
    it('should project events to read models', () => {
      const projector = new EventProjector();

      projector.registerProjector('UserCreated', (event, projection) => {
        return { ...projection, name: event.data.name };
      });

      const event: DomainEvent = {
        id: '1',
        type: 'UserCreated',
        timestamp: Date.now(),
        aggregateId: 'user-1',
        version: 1,
        data: { name: 'John' },
      };

      const projection = projector.project('user-1', event, {});
      expect(projection.name).toBe('John');
    });

    it('should update projections incrementally', () => {
      const projector = new EventProjector();

      projector.registerProjector('PropertyChanged', (event, projection) => {
        return { ...projection, ...event.data };
      });

      const event1: DomainEvent = {
        id: '1',
        type: 'PropertyChanged',
        timestamp: Date.now(),
        aggregateId: 'obj-1',
        version: 1,
        data: { a: 1 },
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'PropertyChanged',
        timestamp: Date.now(),
        aggregateId: 'obj-1',
        version: 2,
        data: { b: 2 },
      };

      projector.project('obj-1', event1, {});
      projector.project('obj-1', event2);

      const projection = projector.getProjection('obj-1');
      expect(projection).toEqual({ a: 1, b: 2 });
    });

    it('should handle missing projectors', () => {
      const projector = new EventProjector();

      const event: DomainEvent = {
        id: '1',
        type: 'UnregisteredEvent',
        timestamp: Date.now(),
        aggregateId: 'obj-1',
        version: 1,
        data: {},
      };

      const result = projector.project('obj-1', event, { initial: true });
      expect(result).toEqual({ initial: true });
    });

    it('should clear projections', () => {
      const projector = new EventProjector();

      projector.registerProjector('Event', (event, projection) => event.data);

      const event: DomainEvent = {
        id: '1',
        type: 'Event',
        timestamp: Date.now(),
        aggregateId: 'obj-1',
        version: 1,
        data: { value: 'test' },
      };

      projector.project('obj-1', event);
      expect(projector.getProjection('obj-1')).toBeDefined();

      projector.clear();
      expect(projector.getProjection('obj-1')).toBeUndefined();
    });
  });

  describe('EventSourcedRepository', () => {
    class TestAggregate extends AggregateRoot {
      private value: string = '';

      getValue(): string {
        return this.value;
      }

      setValue(val: string): void {
        this.raiseEvent('ValueSet', { value: val });
      }

      protected applyEvent(event: DomainEvent): void {
        super.applyEvent(event);
        if (event.type === 'ValueSet') {
          this.value = event.data.value;
        }
      }
    }

    let repo: EventSourcedRepository<TestAggregate>;
    let store: InMemoryEventStore;

    beforeEach(() => {
      store = new InMemoryEventStore();
      repo = new EventSourcedRepository(store, TestAggregate);
    });

    it('should save aggregate', async () => {
      const agg = new TestAggregate('test-1');
      agg.setValue('test-value');

      await repo.save(agg);

      const events = await store.getEvents('test-1');
      expect(events).toHaveLength(1);
    });

    it('should retrieve aggregate by ID', async () => {
      const agg = new TestAggregate('test-1');
      agg.setValue('test-value');

      await repo.save(agg);

      const retrieved = await repo.getById('test-1');
      expect(retrieved).not.toBeNull();
      expect(retrieved?.getValue()).toBe('test-value');
    });

    it('should return null for non-existent aggregate', async () => {
      const retrieved = await repo.getById('non-existent');
      expect(retrieved).toBeNull();
    });

    it('should get all aggregates', async () => {
      const agg1 = new TestAggregate('test-1');
      agg1.setValue('value1');

      const agg2 = new TestAggregate('test-2');
      agg2.setValue('value2');

      await repo.save(agg1);
      await repo.save(agg2);

      const all = await repo.getAll();
      expect(all).toHaveLength(2);
    });

    it('should delete aggregate', async () => {
      const agg = new TestAggregate('test-1');
      agg.setValue('test-value');

      await repo.save(agg);
      await repo.delete('test-1');

      const events = await store.getEvents('test-1');
      const hasDeleteEvent = events.some((e) => e.type === 'AggregateDeleted');
      expect(hasDeleteEvent).toBe(true);
    });
  });

  describe('EventReplayService', () => {
    let service: EventReplayService;
    let store: InMemoryEventStore;

    beforeEach(async () => {
      store = new InMemoryEventStore();
      service = new EventReplayService(store);

      const event1: DomainEvent = {
        id: '1',
        type: 'Event1',
        timestamp: Date.now() - 1000,
        aggregateId: 'agg-1',
        version: 1,
        data: { msg: 'first' },
      };

      const event2: DomainEvent = {
        id: '2',
        type: 'Event2',
        timestamp: Date.now(),
        aggregateId: 'agg-1',
        version: 2,
        data: { msg: 'second' },
      };

      await store.append(event1);
      await store.append(event2);
    });

    it('should get history', async () => {
      const history = await service.getHistory('agg-1');
      expect(history).toHaveLength(2);
    });

    it('should get history in range', async () => {
      const now = Date.now();
      const history = await service.getHistoryInRange('agg-1', now - 500, now);

      expect(history).toHaveLength(1);
      expect(history[0].type).toBe('Event2');
    });

    it('should get snapshot at version', async () => {
      class TestAggregate extends AggregateRoot {
        protected applyEvent(): void {
          super.applyEvent(...arguments);
        }
      }

      const snapshot = await service.getSnapshotAtVersion<TestAggregate>(
        'agg-1',
        1,
        TestAggregate
      );

      expect(snapshot).not.toBeNull();
      expect(snapshot?.getVersion()).toBe(1);
    });

    it('should generate audit trail', async () => {
      const trail = await service.getAuditTrail('agg-1');

      expect(trail).toContain('Event1');
      expect(trail).toContain('Event2');
      expect(trail).toContain('first');
      expect(trail).toContain('second');
    });

    it('should search events by predicate', async () => {
      const results = await service.searchEvents(
        (e) => e.data.msg === 'first'
      );

      expect(results).toHaveLength(1);
      expect(results[0].type).toBe('Event1');
    });
  });

  describe('SnapshotRepository', () => {
    let repo: SnapshotRepository<any>;

    beforeEach(() => {
      repo = new SnapshotRepository();
    });

    it('should save and retrieve snapshot', () => {
      const snapshot = {
        aggregateId: 'agg-1',
        version: 5,
        state: { value: 'test' },
        timestamp: Date.now(),
      };

      repo.saveSnapshot(snapshot);
      const retrieved = repo.getLatestSnapshot('agg-1');

      expect(retrieved).toEqual(snapshot);
    });

    it('should delete snapshot', () => {
      const snapshot = {
        aggregateId: 'agg-1',
        version: 5,
        state: { value: 'test' },
        timestamp: Date.now(),
      };

      repo.saveSnapshot(snapshot);
      repo.deleteSnapshot('agg-1');

      const retrieved = repo.getLatestSnapshot('agg-1');
      expect(retrieved).toBeNull();
    });

    it('should clear all snapshots', () => {
      repo.saveSnapshot({
        aggregateId: 'agg-1',
        version: 1,
        state: {},
        timestamp: Date.now(),
      });

      repo.saveSnapshot({
        aggregateId: 'agg-2',
        version: 1,
        state: {},
        timestamp: Date.now(),
      });

      repo.clear();
      expect(repo.getSnapshotCount()).toBe(0);
    });

    it('should track snapshot count', () => {
      expect(repo.getSnapshotCount()).toBe(0);

      repo.saveSnapshot({
        aggregateId: 'agg-1',
        version: 1,
        state: {},
        timestamp: Date.now(),
      });

      expect(repo.getSnapshotCount()).toBe(1);
    });

    it('should return null for non-existent snapshot', () => {
      const snapshot = repo.getLatestSnapshot('non-existent');
      expect(snapshot).toBeNull();
    });
  });
});

// ==================== Integration Tests ====================

describe('CQRS + Event Sourcing Integration', () => {
  class User extends AggregateRoot {
    private email: string = '';
    private isActive: boolean = false;

    getEmail(): string {
      return this.email;
    }

    isActiveUser(): boolean {
      return this.isActive;
    }

    createUser(email: string): void {
      this.raiseEvent('UserCreated', { email });
    }

    activateUser(): void {
      this.raiseEvent('UserActivated', { activatedAt: Date.now() });
    }

    deactivateUser(): void {
      this.raiseEvent('UserDeactivated', { deactivatedAt: Date.now() });
    }

    protected applyEvent(event: DomainEvent): void {
      super.applyEvent(event);

      switch (event.type) {
        case 'UserCreated':
          this.email = event.data.email;
          break;
        case 'UserActivated':
          this.isActive = true;
          break;
        case 'UserDeactivated':
          this.isActive = false;
          break;
      }
    }
  }

  class CreateUserCommand extends BaseCommand {
    constructor(
      private repo: EventSourcedRepository<User>,
      public email: string
    ) {
      super();
    }

    async execute(): Promise<string> {
      const userId = `user-${Date.now()}`;
      const user = new User(userId);
      user.createUser(this.email);

      await this.repo.save(user);

      return userId;
    }
  }

  class GetUserQuery extends BaseQuery {
    constructor(
      private repo: EventSourcedRepository<User>,
      public userId: string
    ) {
      super();
    }

    async execute(): Promise<any> {
      const user = await this.repo.getById(this.userId);

      if (!user) {
        return null;
      }

      return {
        id: user.getId(),
        email: user.getEmail(),
        isActive: user.isActiveUser(),
      };
    }
  }

  it('should create user via command and query via query', async () => {
    const store = new InMemoryEventStore();
    const repo = new EventSourcedRepository(store, User);
    const handler = new CQRSHandler();

    handler.registerCommand('createUser', CreateUserCommand);
    handler.registerQuery('getUser', GetUserQuery);

    const userId = await handler.command('createUser', {
      repo,
      email: 'test@example.com',
    });

    const user = await handler.query('getUser', { repo, userId });

    expect(user).not.toBeNull();
    expect(user.email).toBe('test@example.com');
    expect(user.isActive).toBe(false);
  });

  it('should track event history through CQRS operations', async () => {
    const store = new InMemoryEventStore();
    const repo = new EventSourcedRepository(store, User);
    const handler = new CQRSHandler();

    handler.registerCommand('createUser', CreateUserCommand);

    const userId = await handler.command('createUser', {
      repo,
      email: 'test@example.com',
    });

    // Manually update user
    const user = await repo.getById(userId);
    user?.activateUser();
    await repo.save(user!);

    // Check event history
    const events = await store.getEvents(userId);
    expect(events).toHaveLength(2);
    expect(events[0].type).toBe('UserCreated');
    expect(events[1].type).toBe('UserActivated');
  });

  it('should replay events to recreate state', async () => {
    const store = new InMemoryEventStore();
    const repo = new EventSourcedRepository(store, User);

    // Create and modify user
    const user1 = new User('user-1');
    user1.createUser('test@example.com');
    user1.activateUser();

    await repo.save(user1);

    // Retrieve and verify
    const user2 = await repo.getById('user-1');

    expect(user2?.getEmail()).toBe('test@example.com');
    expect(user2?.isActiveUser()).toBe(true);
    expect(user2?.getVersion()).toBe(2);
  });
});
