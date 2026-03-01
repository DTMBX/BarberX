import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { listIssues, createIssue, type IssueCreate } from '@/lib/api';

/**
 * List issues for a case.
 */
export function useIssues(caseId: string) {
  return useQuery({
    queryKey: queryKeys.issues.list(caseId),
    queryFn: () => listIssues(caseId),
    enabled: !!caseId,
  });
}

/**
 * Create a new issue and invalidate the issues list for that case.
 */
export function useCreateIssue(caseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: IssueCreate) => createIssue(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issues.list(caseId) });
    },
  });
}
