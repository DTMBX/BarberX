'use client';

import { useState, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Input, Badge, Button, EmptyState } from '@/components/ui';

/* ── Types ──────────────────────────────────────────────────── */

export interface ResourceItem {
  id: string;
  type: 'evidence' | 'artifact' | 'issue' | 'timeline_event';
  name: string;
  description?: string;
  status?: string;
  sha256?: string;
  createdAt?: string;
}

interface ResourceLibraryProps {
  /** All resources available for attachment */
  items: ResourceItem[];
  /** Whether data is still loading */
  loading?: boolean;
  /** Called when user selects a resource to attach */
  onAttach: (item: ResourceItem) => void;
  /** Currently attached resource IDs */
  attachedIds?: Set<string>;
  className?: string;
}

const TYPE_LABELS: Record<ResourceItem['type'], string> = {
  evidence: 'Evidence',
  artifact: 'Artifact',
  issue: 'Issue',
  timeline_event: 'Event',
};

const TYPE_FILTERS: ResourceItem['type'][] = ['evidence', 'artifact', 'issue', 'timeline_event'];

/* ── Component ──────────────────────────────────────────────── */

/**
 * Sidebar panel showing filterable case resources that can be attached to chat.
 */
export function ResourceLibrary({
  items,
  loading,
  onAttach,
  attachedIds = new Set(),
  className,
}: ResourceLibraryProps) {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<ResourceItem['type'] | 'all'>('all');

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return items.filter((item) => {
      if (filterType !== 'all' && item.type !== filterType) return false;
      if (
        q &&
        !item.name.toLowerCase().includes(q) &&
        !(item.description ?? '').toLowerCase().includes(q)
      )
        return false;
      return true;
    });
  }, [items, search, filterType]);

  return (
    <div className={cn('flex flex-col h-full bg-slate-800 border-r border-slate-700', className)}>
      {/* Header */}
      <div className="px-3 py-2 border-b border-slate-700">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          Case Resources
        </h3>
        <Input
          label="Search resources"
          hideLabel
          placeholder="Search…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Type filter tabs */}
      <div className="flex gap-1 px-3 py-2 border-b border-slate-700 flex-wrap">
        <FilterChip
          active={filterType === 'all'}
          onClick={() => setFilterType('all')}
          label={`All (${items.length})`}
        />
        {TYPE_FILTERS.map((t) => {
          const count = items.filter((i) => i.type === t).length;
          if (count === 0) return null;
          return (
            <FilterChip
              key={t}
              active={filterType === t}
              onClick={() => setFilterType(t)}
              label={`${TYPE_LABELS[t]} (${count})`}
            />
          );
        })}
      </div>

      {/* Resource list */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-3 space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-14 rounded bg-slate-700 animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-4">
            <EmptyState
              title="No resources"
              description={
                search ? 'No matches for your search.' : 'This case has no resources yet.'
              }
            />
          </div>
        ) : (
          <ul role="list" className="divide-y divide-slate-700/50">
            {filtered.map((item) => {
              const isAttached = attachedIds.has(item.id);
              return (
                <li key={item.id} className="px-3 py-2 hover:bg-slate-700/40 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-200 truncate">{item.name}</p>
                      {item.description && (
                        <p className="text-xs text-slate-400 line-clamp-1">{item.description}</p>
                      )}
                      <div className="flex items-center gap-1.5 mt-1">
                        <Badge variant="info">{TYPE_LABELS[item.type]}</Badge>
                        {item.status && (
                          <Badge variant={item.status === 'verified' ? 'verified' : 'neutral'}>
                            {item.status}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Button
                      variant={isAttached ? 'secondary' : 'ghost'}
                      size="sm"
                      onClick={() => onAttach(item)}
                      aria-label={isAttached ? `Remove ${item.name}` : `Attach ${item.name}`}
                    >
                      {isAttached ? '✓' : '+'}
                    </Button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Footer hint */}
      <div className="px-3 py-2 border-t border-slate-700">
        <p className="text-[11px] text-slate-500">
          Attached resources are sent as context with your next message.
        </p>
      </div>
    </div>
  );
}

/* ── Internal ───────────────────────────────────────────────── */

function FilterChip({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-2 py-0.5 rounded-full text-[11px] font-medium transition-colors',
        active ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
      )}
    >
      {label}
    </button>
  );
}
