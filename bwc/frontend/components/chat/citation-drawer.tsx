'use client';

import { useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui';

/* ── Types ──────────────────────────────────────────────────── */

export interface CitationItem {
  id: string;
  sourceType: 'courtlistener' | 'evidence_artifact' | 'evidence' | 'external';
  title: string;
  subtitle?: string;
  url?: string;
  verificationStatus: string;
  snippet?: string;
}

interface CitationDrawerProps {
  open: boolean;
  onClose: () => void;
  citation: CitationItem | null;
}

/* ── Component ──────────────────────────────────────────────── */

/**
 * Slide-over drawer that shows citation details.
 * Opens from the right side when a user clicks a citation badge.
 */
export function CitationDrawer({ open, onClose, citation }: CitationDrawerProps) {
  if (!citation) return null;

  const statusColor: Record<string, string> = {
    verified: 'text-emerald-400',
    unverified: 'text-yellow-400',
    failed: 'text-red-400',
  };

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div className="fixed inset-0 z-40 bg-black/50" onClick={onClose} aria-hidden="true" />
      )}

      {/* Drawer */}
      <aside
        className={cn(
          'fixed top-0 right-0 z-50 h-full w-full max-w-md bg-slate-800 border-l border-slate-700 shadow-xl',
          'transition-transform duration-200 ease-out',
          open ? 'translate-x-0' : 'translate-x-full'
        )}
        role="dialog"
        aria-modal="true"
        aria-label="Citation details"
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-700 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-200">Citation Details</h2>
            <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close">
              ✕
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Source</span>
              <p className="text-sm font-medium text-slate-200 mt-1">
                {citation.sourceType === 'courtlistener'
                  ? '⚖️ CourtListener'
                  : citation.sourceType === 'evidence_artifact'
                    ? '📎 Evidence Artifact'
                    : citation.sourceType === 'evidence'
                      ? '🔒 Evidence'
                      : '🔗 External'}
              </p>
            </div>

            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Title</span>
              <p className="text-sm font-medium text-white mt-1">{citation.title}</p>
              {citation.subtitle && (
                <p className="text-xs text-slate-400 mt-0.5">{citation.subtitle}</p>
              )}
            </div>

            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Verification</span>
              <p
                className={cn(
                  'text-sm font-medium mt-1',
                  statusColor[citation.verificationStatus] ?? 'text-slate-300'
                )}
              >
                {citation.verificationStatus}
              </p>
            </div>

            {citation.snippet && (
              <div>
                <span className="text-xs text-slate-400 uppercase tracking-wider">Excerpt</span>
                <blockquote className="mt-1 border-l-2 border-slate-600 pl-3 text-sm text-slate-300 italic">
                  {citation.snippet}
                </blockquote>
              </div>
            )}

            {citation.url && (
              <div>
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300"
                >
                  Open source →
                </a>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-slate-700 px-4 py-3">
            <p className="text-xs text-slate-500">
              All citations are grounded in case data or verified legal sources. Never rely on
              AI-only output without checking the source.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
