import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { listEvidence } from '@/lib/api';

/**
 * List evidence for a case.
 * Refetches when the case ID changes.
 */
export function useEvidence(caseId: string) {
  return useQuery({
    queryKey: queryKeys.evidence.list(caseId),
    queryFn: () => listEvidence(caseId),
    enabled: !!caseId,
  });
}
