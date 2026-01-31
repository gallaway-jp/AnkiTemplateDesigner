/**
 * Type definitions for application events
 * Used with EventBus for component communication
 */

import { Template } from '@/types';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface CraftComponent {
  id: string;
  type: string;
  props: Record<string, any>;
}

export interface TemplateEvent {
  id: string;
  timestamp: number;
  type: 'created' | 'updated' | 'deleted' | 'saved' | 'loaded';
}

/**
 * Application event types
 * Use these string literals as keys in eventBus.on/emit
 */
export interface AppEvents {
  'template:loaded': { template: Template; source: string };
  'template:updated': { template: Template; changes: Partial<Template> };
  'template:saved': { template: Template; timestamp: number };
  'template:deleted': { id: string; timestamp: number };
  'template:duplicated': { sourceId: string; newId: string };
  'component:selected': { id: string; type: string; path: string[] };
  'component:deselected': { id: string };
  'component:updated': { component: CraftComponent; path: string[] };
  'component:added': { component: CraftComponent; parentId: string };
  'component:removed': { id: string; parentId: string };
  'component:moved': { id: string; fromPath: string[]; toPath: string[] };
  'error:occurred': { error: Error; context: string; recoverable: boolean };
  'error:recovered': { errorId: string; context: string };
  'notification:show': Notification;
  'notification:dismiss': { id: string };
  'editor:focus': { componentId: string };
  'editor:blur': { componentId: string };
  'preview:refreshed': { templateId: string; timestamp: number };
  'validation:triggered': { templateId: string; errors: string[] };
  'export:started': { templateId: string; format: string };
  'export:completed': { templateId: string; data: any };
  'export:failed': { templateId: string; error: Error };
  'history:changed': { canUndo: boolean; canRedo: boolean };
  'settings:changed': { key: string; value: any };
  'connection:changed': { status: 'connected' | 'disconnected' };
}

/**
 * Type-safe event emitter
 * Use with EventBus for better type checking
 */
export class TypedEventBus {
  constructor(private bus: any) {}

  on<K extends keyof AppEvents>(
    event: K,
    handler: (data: AppEvents[K]) => void
  ): () => void {
    return this.bus.on(event, handler);
  }

  emit<K extends keyof AppEvents>(event: K, data: AppEvents[K]): void {
    this.bus.emit(event, data);
  }

  off(event: keyof AppEvents): void {
    this.bus.off(event);
  }
}
