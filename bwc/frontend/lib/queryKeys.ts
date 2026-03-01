/**
 * Centralized React Query cache key factory.
 * Convention: every key is a tuple — first element is the entity name,
 * subsequent elements narrow the scope.
 *
 * Usage in hooks:
 *   useQuery({ queryKey: queryKeys.evidence.list(caseId), ... })
 *
 * Invalidation:
 *   queryClient.invalidateQueries({ queryKey: queryKeys.evidence.all })
 */
export const queryKeys = {
  // ── Health ──────────────────────────────────────────────
  health: {
    all: ['health'] as const,
  },

  // ── Projects ───────────────────────────────────────────
  projects: {
    all: ['projects'] as const,
    list: () => ['projects', 'list'] as const,
    detail: (id: string) => ['projects', 'detail', id] as const,
  },

  // ── Cases ──────────────────────────────────────────────
  cases: {
    all: ['cases'] as const,
    list: (projectId?: string) => ['cases', 'list', { projectId }] as const,
    detail: (id: string) => ['cases', 'detail', id] as const,
  },

  // ── Evidence ───────────────────────────────────────────
  evidence: {
    all: ['evidence'] as const,
    list: (caseId: string) => ['evidence', 'list', caseId] as const,
  },

  // ── Artifacts ──────────────────────────────────────────
  artifacts: {
    all: ['artifacts'] as const,
    list: (caseId: string) => ['artifacts', 'list', caseId] as const,
  },

  // ── Timeline ──────────────────────────────────────────
  timeline: {
    all: ['timeline'] as const,
    list: (caseId: string) => ['timeline', 'list', caseId] as const,
  },

  // ── Issues ─────────────────────────────────────────────
  issues: {
    all: ['issues'] as const,
    list: (caseId: string) => ['issues', 'list', caseId] as const,
  },

  // ── Jobs ───────────────────────────────────────────────
  jobs: {
    all: ['jobs'] as const,
    list: (caseId: string) => ['jobs', 'list', caseId] as const,
  },

  // ── Chat ───────────────────────────────────────────────
  chat: {
    all: ['chat'] as const,
    history: (scope: string, caseId?: string, projectId?: string) =>
      ['chat', 'history', { scope, caseId, projectId }] as const,
  },

  // ── Legal / CourtListener ─────────────────────────────
  legal: {
    all: ['legal'] as const,
    search: (query: string, jurisdiction?: string) =>
      ['legal', 'search', { query, jurisdiction }] as const,
  },
} as const;
