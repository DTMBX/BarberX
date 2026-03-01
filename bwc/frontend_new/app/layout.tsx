import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Evident BWC - Body-Worn Camera Evidence Management',
  description: 'Forensic-grade evidence management platform with tamper-proof chain of custody',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-white min-h-screen">
        <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
          <nav className="max-w-6xl mx-auto flex items-center justify-between">
            <h1 className="text-xl font-bold text-blue-400">Evident BWC</h1>
            <div className="flex gap-6">
              <a href="/" className="hover:text-blue-400 transition-colors">Dashboard</a>
              <a href="/cases" className="hover:text-blue-400 transition-colors">Cases</a>
              <a href="/verify" className="hover:text-blue-400 transition-colors">Verify</a>
            </div>
          </nav>
        </header>
        <main className="max-w-6xl mx-auto px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
