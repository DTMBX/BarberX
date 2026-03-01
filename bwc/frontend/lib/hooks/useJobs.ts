import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { listJobs } from '@/lib/api';

/**
 * List jobs for a case.
 * Jobs update frequently, so we use a shorter stale time.
 */
export function useJobs(caseId: string) {
  return useQuery({
    queryKey: queryKeys.jobs.list(caseId),
    queryFn: () => listJobs(caseId),
    enabled: !!caseId,
    staleTime: 10_000, // 10s — jobs change often
    refetchInterval: 15_000, // auto-poll every 15s
  });
}
