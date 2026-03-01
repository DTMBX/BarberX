import { describe, it, expect } from 'vitest';
import { queryKeys } from '@/lib/queryKeys';

describe('queryKeys factory', () => {
  it('returns a stable health key', () => {
    expect(queryKeys.health.all).toEqual(['health']);
  });

  it('returns projects list key', () => {
    expect(queryKeys.projects.all).toEqual(['projects']);
    expect(queryKeys.projects.list()).toEqual(['projects', 'list']);
  });

  it('returns projects detail key with id', () => {
    expect(queryKeys.projects.detail('proj-123')).toEqual(['projects', 'detail', 'proj-123']);
  });

  it('returns cases list key with optional projectId', () => {
    expect(queryKeys.cases.all).toEqual(['cases']);
    expect(queryKeys.cases.list()).toEqual(['cases', 'list', { projectId: undefined }]);
    expect(queryKeys.cases.list('proj-1')).toEqual(['cases', 'list', { projectId: 'proj-1' }]);
  });

  it('returns evidence list key scoped to case', () => {
    expect(queryKeys.evidence.list('case-456')).toEqual(['evidence', 'list', 'case-456']);
  });

  it('returns timeline list key scoped to case', () => {
    expect(queryKeys.timeline.list('case-789')).toEqual(['timeline', 'list', 'case-789']);
  });

  it('returns issues list key scoped to case', () => {
    expect(queryKeys.issues.list('case-abc')).toEqual(['issues', 'list', 'case-abc']);
  });

  it('returns jobs list key scoped to case', () => {
    expect(queryKeys.jobs.list('case-def')).toEqual(['jobs', 'list', 'case-def']);
  });

  it('returns legal search key with query and jurisdiction', () => {
    expect(queryKeys.legal.search('test query', 'NJ')).toEqual([
      'legal',
      'search',
      { query: 'test query', jurisdiction: 'NJ' },
    ]);
  });

  it('returns legal search key without jurisdiction', () => {
    expect(queryKeys.legal.search('test query')).toEqual([
      'legal',
      'search',
      { query: 'test query', jurisdiction: undefined },
    ]);
  });

  it('all keys start with entity name', () => {
    const entities = Object.keys(queryKeys);
    for (const entity of entities) {
      const group = (queryKeys as any)[entity];
      expect(group.all[0]).toBe(entity);
    }
  });
});
