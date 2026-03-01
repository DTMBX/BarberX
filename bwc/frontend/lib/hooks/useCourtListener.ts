import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { legalSearch, type LegalOpinion } from '@/lib/api';

/**
 * Search CourtListener opinions.
 * Only fires when query is non-empty (manual trigger).
 */
export function useCourtListener(query: string, jurisdiction?: string, enabled = false) {
  return useQuery({
    queryKey: queryKeys.legal.search(query, jurisdiction),
    queryFn: () => legalSearch(query, { jurisdiction }),
    enabled: enabled && !!query.trim(),
    staleTime: 5 * 60_000, // 5 min — legal search results don't change rapidly
  });
}
