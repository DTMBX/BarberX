import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

/* ── Badge ──────────────────────────────────────────────────── */

const variantClasses = {
  verified: 'bg-emerald-900/30 text-emerald-400 border-emerald-600/30',
  pending: 'bg-yellow-900/30 text-yellow-400 border-yellow-600/30',
  tampered: 'bg-red-900/30 text-red-400 border-red-600/30',
  error: 'bg-red-900/30 text-red-400 border-red-600/30',
  success: 'bg-emerald-900/30 text-emerald-400 border-emerald-600/30',
  warning: 'bg-yellow-900/30 text-yellow-400 border-yellow-600/30',
  info: 'bg-blue-900/30 text-blue-400 border-blue-600/30',
  neutral: 'bg-slate-700 text-slate-300 border-slate-600',
} as const;

export type BadgeVariant = keyof typeof variantClasses;

export interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

export function Badge({ variant = 'neutral', children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
