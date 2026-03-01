'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { listCases, type Case } from '@/lib/api';
import { Button, Badge, PageHeader, DataTable, EmptyState, type Column } from '@/components/ui';

const columns: Column<Case>[] = [
  {
    id: 'title',
    header: 'Title',
    cell: (c) => (
      <Link href={`/cases/${c.id}`} className="font-medium text-blue-400 hover:text-blue-300">
        {c.title}
      </Link>
    ),
    sortValue: (c) => c.title,
  },
  {
    id: 'status',
    header: 'Status',
    cell: (c) => <Badge variant={c.status === 'open' ? 'success' : 'neutral'}>{c.status}</Badge>,
    sortValue: (c) => c.status,
  },
  {
    id: 'created_by',
    header: 'Created By',
    cell: (c) => <span className="text-slate-300">{c.created_by}</span>,
    sortValue: (c) => c.created_by,
  },
  {
    id: 'created_at',
    header: 'Created',
    cell: (c) => (
      <span className="text-slate-400 text-xs">{new Date(c.created_at).toLocaleDateString()}</span>
    ),
    sortValue: (c) => c.created_at,
  },
  {
    id: 'actions',
    header: '',
    cell: (c) => (
      <Link href={`/cases/${c.id}`} className="text-blue-400 hover:text-blue-300 text-sm">
        View &rarr;
      </Link>
    ),
    className: 'text-right',
  },
];

export default function CasesPage() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project_id') || undefined;
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCases(projectId)
      .then(setCases)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [projectId]);

  return (
    <div>
      <PageHeader
        title="Cases"
        actions={
          <Link href="/cases/new">
            <Button data-testid="cases-new-btn">New Case</Button>
          </Link>
        }
      />

      <div className="mt-6" data-testid="cases-table">
        <DataTable
          columns={columns}
          data={cases}
          loading={loading}
          error={error ?? undefined}
          rowKey={(c) => c.id}
          emptyTitle="No cases yet"
          emptyDescription="Create your first case to get started"
          emptyAction={
            <Link href="/cases/new">
              <Button size="sm" data-testid="cases-empty-create-btn">
                Create your first case
              </Button>
            </Link>
          }
        />
      </div>
    </div>
  );
}
