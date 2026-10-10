'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, FlaskConical, FileText, Upload, ArrowLeft, AlertTriangle, Database } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/faculty', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { href: '/faculty/simulate', label: 'Simulate', icon: FlaskConical, exact: false },
  { href: '/faculty/report', label: 'Report', icon: FileText, exact: false },
  { href: '/faculty/upload-preview', label: 'Upload Preview', icon: Upload, exact: false },
];

export default function FacultyLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { faculty, setActiveRole, setDatasetSnapshot } = useTechGapStore();

  return (
    <div className="min-h-screen bg-surface-bg flex flex-col">

      {/* Top Navigation */}
      <header className="bg-white border-b-2 border-[#E2E8F0] px-6 py-0 no-print">
        <div className="max-w-7xl mx-auto flex items-center gap-0">
          {/* Brand */}
          <div className="flex items-center gap-3 py-3 mr-6">
            <Link
              href="/"
              onClick={() => setActiveRole(null)}
              className="flex items-center gap-1.5 text-[#64748B] hover:text-[#0F172A] text-sm"
            >
              <ArrowLeft size={14} />
            </Link>
            <div className="w-8 h-8 bg-[#0284C7] rounded-lg flex items-center justify-center">
              <LayoutDashboard size={16} className="text-white" />
            </div>
            <div>
              <span className="font-extrabold text-[#0F172A] text-sm">TechGap</span>
              <span className="text-[#64748B] text-xs ml-2">Faculty Dashboard</span>
            </div>
          </div>

          {/* Nav tabs */}
          <nav className="flex items-center flex-1" aria-label="Faculty navigation">
            {navItems.map(({ href, label, icon: Icon, exact }) => {
              const isActive = exact ? pathname === href : pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    'flex items-center gap-1.5 px-4 py-4 text-sm font-semibold border-b-2 transition-all',
                    isActive
                      ? 'border-[#007041] text-[#007041]'
                      : 'border-transparent text-[#64748B] hover:text-[#0F172A] hover:border-slate-200'
                  )}
                >
                  <Icon size={15} />
                  {label}
                </Link>
              );
            })}
          </nav>

          {/* Dataset Snapshot Toggle (required by spec) */}
          <div className="flex items-center gap-2 ml-auto py-3">
            <Database size={13} className="text-[#64748B]" />
            <div className="flex rounded-lg border-2 border-[#E2E8F0] overflow-hidden text-xs font-semibold">
              {(['Q3 2026', 'Q4 2026'] as const).map((snap) => (
                <button
                  key={snap}
                  onClick={() => setDatasetSnapshot(snap)}
                  className={cn(
                    'px-3 py-1.5 transition-colors',
                    faculty.datasetSnapshot === snap
                      ? 'bg-[#007041] text-white'
                      : 'bg-white text-[#64748B] hover:bg-slate-50'
                  )}
                >
                  {snap === 'Q3 2026' ? 'Controlled Q3 2026 Snapshot' : 'Updated Q4 Snapshot'}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1">{children}</main>
    </div>
  );
}
