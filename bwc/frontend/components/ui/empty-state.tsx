import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn('flex flex-col items-center justify-center py-12 px-6 text-center', className)}
    >
      {icon && <div className="text-slate-500 mb-4 text-4xl">{icon}</div>}
      <h3 className="text-sm font-semibold text-slate-300 mb-1">{title}</h3>
      {description && <p className="text-xs text-slate-500 max-w-sm mb-4">{description}</p>}
      {action}
    </div>
  );
}
