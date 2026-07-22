/**
 * Domain event infrastructure for event-sourced aggregates.
 *
 * Architecture: Event Sourcing + CQRS (append-only event log, separate read models)
 * Reference:
 *  - Vernon, "Implementing Domain-Driven Design" (2013)
 *  - Fowler, "Event Sourcing" pattern — martinfowler.com/eaaDev/EventSourcing.html
 *  - Chopra & Meindl Ch.17: Information in the supply chain
 */

import { ISOTimestamp, nowUTC } from './types';

export interface DomainEvent {
  readonly eventId: string;
  readonly eventType: string;
  readonly aggregateId: string;
  readonly aggregateType: string;
  readonly occurredAt: ISOTimestamp;
  readonly version: number;
  readonly metadata: EventMetadata;
}

export interface EventMetadata {
  readonly userId?: string;
  readonly correlationId: string;   // trace across services
  readonly causationId?: string;    // event that caused this event
  readonly idempotencyKey?: string; // safe retry support
}

export abstract class BaseDomainEvent implements DomainEvent {
  readonly eventId: string;
  readonly occurredAt: ISOTimestamp;

  constructor(
    readonly eventType: string,
    readonly aggregateId: string,
    readonly aggregateType: string,
    readonly version: number,
    readonly metadata: EventMetadata,
  ) {
    this.eventId = crypto.randomUUID();
    this.occurredAt = nowUTC();
  }
}

// ─── Event Store (in-memory reference implementation) ────────────────────────
export class EventStore {
  private events: DomainEvent[] = [];
  private handlers: Map<string, ((e: DomainEvent) => void)[]> = new Map();

  append(event: DomainEvent): void {
    this.events.push(event);
    const subscribers = this.handlers.get(event.eventType) ?? [];
    for (const handler of subscribers) handler(event);
    const wildcards = this.handlers.get('*') ?? [];
    for (const handler of wildcards) handler(event);
  }

  getByAggregateId(aggregateId: string): DomainEvent[] {
    return this.events.filter(e => e.aggregateId === aggregateId);
  }

  subscribe(eventType: string, handler: (e: DomainEvent) => void): void {
    const existing = this.handlers.get(eventType) ?? [];
    this.handlers.set(eventType, [...existing, handler]);
  }

  getAll(): DomainEvent[] {
    return [...this.events];
  }
}

export const globalEventStore = new EventStore();
