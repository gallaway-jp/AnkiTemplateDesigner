/**
 * Service Exports
 * Central location for all service imports
 */

export { PythonBridge, BridgeError, bridge } from './pythonBridge';
export type { } from './pythonBridge';

export {
  convertGrapeJSToXraftJS,
  craftDataToHtml,
  flattenCraftComponents,
  getCraftComponent,
  updateCraftComponent,
  validateCraftData,
} from './craftjsAdapter';

// Phase 1 Architecture Enhancements
export { ServiceRegistry, registry } from './registry';
export type { ServiceConfig } from './registry';

// Phase 2 Architecture Enhancements
export {
  CacheManager,
  LRUCacheStrategy,
  TTLCacheStrategy,
  HybridCacheStrategy,
  SimpleMemoryCacheStrategy,
  cacheManager,
} from './cacheManager';
export type { CacheStrategy } from './cacheManager';

export {
  ApiClient,
  HttpTransport,
  WebSocketTransport,
  ApiError,
} from './apiClient';
export type { ApiRequest, ApiResponse, ApiTransport } from './apiClient';

// Phase 3 Architecture Enhancements
export {
  CommandBus,
  QueryBus,
  CQRSHandler,
  BaseCommand,
  BaseQuery,
  cqrsHandler,
} from './cqrs';

export {
  InMemoryEventStore,
  EventProjector,
  EventSourcedRepository,
  AggregateRoot,
  EventReplayService,
  SnapshotRepository,
} from './eventSourcing';
export type {
  DomainEvent,
  IEventStore,
  Snapshot,
} from './eventSourcing';
