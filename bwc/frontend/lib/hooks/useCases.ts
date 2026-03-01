import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { listCases, createCase, getCase } from '@/lib/api';

/**
 * List cases, optionally filtered by project.
 */
export function useCases(projectId?: string) {
  return useQuery({
    queryKey: queryKeys.cases.list(projectId),
    queryFn: () => listCases(projectId),
  });
}

/**
 * Fetch a single case by ID.
 */
export function useCase(id: string) {
  return useQuery({
    queryKey: queryKeys.cases.detail(id),
    queryFn: () => getCase(id),
    enabled: !!id,
  });
}

/**
 * Create a new case and invalidate cases list.
 */
export function useCreateCase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { title: string; created_by: string; project_id?: string }) =>
      createCase(data.title, data.created_by, data.project_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cases.all });
    },
  });
}
