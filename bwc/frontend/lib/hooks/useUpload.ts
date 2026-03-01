'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { UploadManager, type UploadFile, type UploadEvent } from '@/lib/uploadManager';
import { useToast } from '@/components/ui';

/**
 * React hook wrapping the UploadManager.
 *
 * Provides reactive state + auto-invalidates React Query caches on completion.
 */
export function useUpload(caseId: string) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const managerRef = useRef<UploadManager | null>(null);
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  // Create/replace manager when caseId changes
  useEffect(() => {
    const manager = new UploadManager(caseId);
    managerRef.current = manager;

    const unsub = manager.subscribe((event: UploadEvent) => {
      setFiles(manager.getFiles());

      if (event.type === 'done') {
        const f = event.file;
        if (f.status === 'verified') {
          addToast('success', `${f.file.name} uploaded and verified`);
        } else if (f.status === 'failed') {
          addToast('error', `${f.file.name}: ${f.error || 'Upload failed'}`);
        }
      }

      if (event.type === 'allDone') {
        // Invalidate evidence + artifacts + timeline + jobs caches
        queryClient.invalidateQueries({ queryKey: queryKeys.evidence.list(caseId) });
        queryClient.invalidateQueries({ queryKey: queryKeys.artifacts.list(caseId) });
        queryClient.invalidateQueries({ queryKey: queryKeys.timeline.list(caseId) });
        queryClient.invalidateQueries({ queryKey: queryKeys.jobs.list(caseId) });
      }
    });

    return () => {
      unsub();
    };
  }, [caseId, queryClient, addToast]);

  const addFiles = useCallback((fileList: FileList | File[]) => {
    managerRef.current?.addFiles(fileList);
  }, []);

  const clearDone = useCallback(() => {
    managerRef.current?.clearDone();
    setFiles(managerRef.current?.getFiles() ?? []);
  }, []);

  const isUploading = files.some((f) => !['verified', 'failed'].includes(f.status));

  return {
    files,
    addFiles,
    clearDone,
    isUploading,
    completedCount: files.filter((f) => f.status === 'verified').length,
    totalCount: files.length,
  };
}
