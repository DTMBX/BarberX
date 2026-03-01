import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { getTimeline } from '@/lib/api';

/**
 * List timeline events for a case.
 */
export function useTimeline(caseId: string) {
  return useQuery({
    queryKey: queryKeys.timeline.list(caseId),
    queryFn: () => getTimeline(caseId),
    enabled: !!caseId,
  });
}
