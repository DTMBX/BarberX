import type { Metadata } from 'next';
import Link from 'next/link';
import { Providers } from './providers';
import { SystemStatusPill } from '@/components/system-status-pill';
import { NavLinks } from '@/components/nav-links';
import './globals.css';

export const metadata: Metadata = {
  title: 'Evident BWC - Body-Worn Camera Evidence Management',
  description: 'Forensic-grade evidence management platform with tamper-proof chain of custody',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-white min-h-screen">
        <Providers>
          <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
            <nav
              className="max-w-7xl mx-auto flex items-center justify-between"
              aria-label="Main navigation"
            >
              <div className="flex items-center gap-4">
                <Link href="/" className="text-xl font-bold text-blue-400">
                  Evident BWC
                </Link>
                <SystemStatusPill />
              </div>
              <NavLinks />
            </nav>
          </header>
          <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
