'use client';

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { healthCheck } from '@/lib/api';
import { cn } from '@/lib/utils';

/**
 * Small pill that shows live backend health status in the nav bar.
 * Polls every 30 seconds. Green = all connected, Yellow = degraded, Red = down.
 */
export function SystemStatusPill() {
  const {
    data: health,
    isError,
    isLoading,
  } = useQuery({
    queryKey: queryKeys.health.all,
    queryFn: healthCheck,
    refetchInterval: 30_000,
    retry: 1,
    staleTime: 20_000,
  });

  const allOk =
    health &&
    health.status === 'healthy' &&
    health.database === 'connected' &&
    health.redis === 'connected' &&
    health.minio === 'connected';

  const degraded = health && !allOk;

  let statusColor = 'bg-slate-500'; // loading / unknown
  let label = 'Checking...';
  let pulseClass = '';

  if (isError) {
    statusColor = 'bg-red-500';
    label = 'Offline';
    pulseClass = 'animate-pulse';
  } else if (allOk) {
    statusColor = 'bg-emerald-500';
    label = 'Online';
  } else if (degraded) {
    statusColor = 'bg-yellow-500';
    label = 'Degraded';
    pulseClass = 'animate-pulse';
  }

  return (
    <div
      className="inline-flex items-center gap-1.5 rounded-full border border-slate-600 bg-slate-800 px-2.5 py-1 text-xs"
      role="status"
      aria-label={`System status: ${label}`}
    >
      <span className={cn('h-2 w-2 rounded-full', statusColor, pulseClass)} aria-hidden="true" />
      <span
        className={cn(
          'font-medium',
          isError
            ? 'text-red-300'
            : allOk
              ? 'text-emerald-300'
              : degraded
                ? 'text-yellow-300'
                : 'text-slate-400'
        )}
      >
        {label}
      </span>
    </div>
  );
}
