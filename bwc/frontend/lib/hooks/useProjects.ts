import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { healthCheck, listProjects, createProject, getProject } from '@/lib/api';

/**
 * Fetch system health status.
 * Polls every 30 seconds when the window is focused.
 */
export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health.all,
    queryFn: healthCheck,
    refetchInterval: 30_000,
    retry: 1,
  });
}

/**
 * List all projects.
 */
export function useProjects() {
  return useQuery({
    queryKey: queryKeys.projects.list(),
    queryFn: listProjects,
  });
}

/**
 * Fetch a single project by ID.
 */
export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => getProject(id),
    enabled: !!id,
  });
}

/**
 * Create a new project and invalidate the list cache.
 */
export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; created_by: string; description?: string }) =>
      createProject(data.name, data.created_by, data.description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
    },
  });
}
