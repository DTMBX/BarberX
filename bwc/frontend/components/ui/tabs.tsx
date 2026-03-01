'use client';

import { cn } from '@/lib/utils';

export interface Tab {
  id: string;
  label: string;
  count?: number;
  icon?: React.ReactNode;
}

export interface TabsProps {
  tabs: Tab[];
  /** Active tab id (alias: activeTab) */
  value?: string;
  activeTab?: string;
  /** Tab-change handler (alias: onTabChange) */
  onChange?: (id: string) => void;
  onTabChange?: (id: string) => void;
  /** Optional prefix for data-testid on each tab, e.g. "case-detail-tab" → data-testid="case-detail-tab-evidence" */
  testIdPrefix?: string;
  className?: string;
}

export function Tabs({
  tabs,
  value,
  activeTab,
  onChange,
  onTabChange,
  testIdPrefix,
  className,
}: TabsProps) {
  const current = value ?? activeTab ?? tabs[0]?.id ?? '';
  const handleChange = onChange ?? onTabChange ?? (() => {});

  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className={cn('flex border-b border-slate-700 overflow-x-auto', className)}
      onKeyDown={(e) => {
        const idx = tabs.findIndex((t) => t.id === current);
        let next = idx;
        if (e.key === 'ArrowRight') next = (idx + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') next = (idx - 1 + tabs.length) % tabs.length;
        else return;
        e.preventDefault();
        handleChange(tabs[next].id);
        // Focus the next tab button
        const tabEl = (e.currentTarget as HTMLElement).querySelector(
          `[data-tab-id="${tabs[next].id}"]`
        ) as HTMLElement;
        tabEl?.focus();
      }}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          data-tab-id={tab.id}
          data-testid={testIdPrefix ? `${testIdPrefix}-${tab.id}` : undefined}
          aria-selected={current === tab.id}
          aria-controls={`tabpanel-${tab.id}`}
          tabIndex={current === tab.id ? 0 : -1}
          onClick={() => handleChange(tab.id)}
          className={cn(
            'flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
            '-mb-px', // overlap the container border
            current === tab.id
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-600'
          )}
        >
          {tab.icon && (
            <span className="shrink-0" aria-hidden="true">
              {tab.icon}
            </span>
          )}
          {tab.label}
          {tab.count !== undefined && (
            <span
              className={cn(
                'ml-1 rounded-full px-1.5 py-0.5 text-[10px] leading-none font-medium',
                current === tab.id ? 'bg-blue-900/50 text-blue-300' : 'bg-slate-700 text-slate-400'
              )}
            >
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}

export function TabPanel({
  id,
  active,
  activeTab,
  children,
  className,
}: {
  id: string;
  /** Direct boolean (alias: activeTab === id) */
  active?: boolean;
  activeTab?: string;
  children: React.ReactNode;
  className?: string;
}) {
  const isActive = active ?? (activeTab != null ? activeTab === id : false);
  if (!isActive) return null;
  return (
    <div
      role="tabpanel"
      id={`tabpanel-${id}`}
      aria-labelledby={id}
      className={cn('pt-4', className)}
    >
      {children}
    </div>
  );
}
