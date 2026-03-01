'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard' },
  { href: '/projects', label: 'Projects' },
  { href: '/cases', label: 'Cases' },
  { href: '/verify', label: 'Verify' },
  { href: '/chat', label: 'Chat' },
  { href: '/settings', label: 'Settings' },
] as const;

export function NavLinks() {
  const pathname = usePathname();

  return (
    <div className="flex gap-1">
      {NAV_ITEMS.map(({ href, label }) => {
        const isActive = href === '/' ? pathname === '/' : pathname.startsWith(href);

        return (
          <Link
            key={href}
            href={href}
            data-testid={`nav-link-${label.toLowerCase()}`}
            className={cn(
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              isActive
                ? 'bg-slate-700 text-blue-400'
                : 'text-slate-300 hover:text-blue-400 hover:bg-slate-700/50'
            )}
            aria-current={isActive ? 'page' : undefined}
          >
            {label}
          </Link>
        );
      })}
    </div>
  );
}
