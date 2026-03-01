'use client';

import { useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { EmptyState } from './empty-state';
import { SkeletonTable } from './loading';

/* ── Types ──────────────────────────────────────────────────── */

export interface Column<T> {
  id: string;
  header: string;
  /** Render the cell content for a given row */
  cell: (row: T) => ReactNode;
  /** Enable sorting for this column — return the sortable value */
  sortValue?: (row: T) => string | number | Date | null;
  /** Column width class, e.g. 'w-48' */
  className?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  error?: string;
  emptyIcon?: ReactNode;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: ReactNode;
  /** Unique key for each row */
  rowKey: (row: T) => string;
  /** Click handler for row */
  onRowClick?: (row: T) => void;
  /** data-testid prefix for rows: renders data-testid="{rowTestId}" on each <tr> */
  rowTestId?: string;
  className?: string;
}

/* ── Component ──────────────────────────────────────────────── */

export function DataTable<T>({
  columns,
  data,
  loading,
  error,
  emptyIcon,
  emptyTitle = 'No data',
  emptyDescription,
  emptyAction,
  rowKey,
  onRowClick,
  rowTestId,
  className,
}: DataTableProps<T>) {
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  if (loading) return <SkeletonTable rows={5} />;

  if (error) {
    return (
      <div className="rounded-lg border border-red-600/30 bg-red-900/20 p-4">
        <p className="text-sm text-red-300">{error}</p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-800">
        <EmptyState
          icon={emptyIcon}
          title={emptyTitle}
          description={emptyDescription}
          action={emptyAction}
        />
      </div>
    );
  }

  // Sort
  const sortColumn = columns.find((c) => c.id === sortCol);
  const sorted = sortColumn?.sortValue
    ? [...data].sort((a, b) => {
        const aVal = sortColumn.sortValue!(a);
        const bVal = sortColumn.sortValue!(b);
        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return 1;
        if (bVal == null) return -1;
        const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        return sortDir === 'asc' ? cmp : -cmp;
      })
    : data;

  function handleSort(colId: string) {
    if (sortCol === colId) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortCol(colId);
      setSortDir('asc');
    }
  }

  return (
    <div
      className={cn('rounded-lg border border-slate-700 bg-slate-800 overflow-x-auto', className)}
    >
      <table className="w-full text-sm">
        <thead className="bg-slate-700/50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.id}
                scope="col"
                className={cn(
                  'px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-300',
                  col.sortValue && 'cursor-pointer select-none hover:text-white',
                  col.className
                )}
                onClick={col.sortValue ? () => handleSort(col.id) : undefined}
                aria-sort={
                  sortCol === col.id ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined
                }
              >
                <span className="inline-flex items-center gap-1">
                  {col.header}
                  {col.sortValue && sortCol === col.id && (
                    <span aria-hidden="true" className="text-blue-400">
                      {sortDir === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {sorted.map((row) => (
            <tr
              key={rowKey(row)}
              data-testid={rowTestId || undefined}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              className={cn(
                'transition-colors',
                onRowClick && 'cursor-pointer hover:bg-slate-700/50',
                !onRowClick && 'hover:bg-slate-750'
              )}
            >
              {columns.map((col) => (
                <td key={col.id} className={cn('px-4 py-3', col.className)}>
                  {col.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
