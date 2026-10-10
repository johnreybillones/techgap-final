'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { ArrowLeft, GraduationCap, RotateCcw, FlaskConical, AlertTriangle } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { cn } from '@/lib/utils';

const steps = [
  { label: 'Setup', href: '/student/setup', num: 1 },
  { label: 'Careers', href: '/student/careers', num: 2 },
  { label: 'Roadmap', href: '/student/roadmap', num: 3 },
];

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { student, resetAll, setActiveRole } = useTechGapStore();

  const trackLabel = student.track
    .replace('BSIT_', 'BSIT ')
    .replace('BSCS_', 'BSCS ')
    .replace(/_/g, ' ');

  return (
    <div className="min-h-screen bg-surface-bg flex flex-col">
      {/* Disclaimer */}
      <div className="w-full bg-amber-50 border-b border-amber-200 px-4 py-1.5 no-print">
        <div className="max-w-6xl mx-auto flex items-center gap-2 text-amber-800 text-xs font-medium">
          <FlaskConical size={12} />
          <span><strong>Illustrative Prototype</strong> — Mock data only. No live backend.</span>
          <AlertTriangle size={12} className="ml-auto" />
        </div>
      </div>

      {/* Header */}
      <header className="bg-white border-b-2 border-[#E2E8F0] px-6 py-3 no-print">
        <div className="max-w-6xl mx-auto flex items-center gap-4">
          {/* Back to home */}
          <Link
            href="/"
            onClick={() => setActiveRole(null)}
            className="flex items-center gap-1.5 text-[#64748B] hover:text-[#0F172A] transition-colors text-sm font-medium"
          >
            <ArrowLeft size={16} />
            Home
          </Link>

          <div className="h-6 w-px bg-[#E2E8F0]" />

          {/* Brand */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#007041] rounded-lg flex items-center justify-center">
              <GraduationCap size={18} className="text-white" />
            </div>
            <div>
              <span className="font-extrabold text-[#0F172A] text-sm">TechGap</span>
              <span className="text-[#64748B] text-xs ml-2">Student Journey</span>
            </div>
          </div>

          {/* Track indicator */}
          {student.selectedCourseIds.length > 0 && (
            <>
              <div className="h-6 w-px bg-[#E2E8F0] ml-auto" />
              <div className="text-right hidden md:block">
                <p className="text-xs font-semibold text-[#0F172A]">{student.yearLevel} · {trackLabel}</p>
                <p className="text-xs text-[#64748B]">{student.selectedCourseIds.length} courses selected</p>
              </div>
            </>
          )}

          {/* Reset */}
          <button
            onClick={() => {
              if (confirm('Reset student selections?')) {
                resetAll();
                router.push('/student/setup');
              }
            }}
            className="flex items-center gap-1 text-xs text-[#64748B] hover:text-red-600 transition-colors ml-4"
            title="Reset student data"
          >
            <RotateCcw size={13} />
            <span className="hidden md:inline">Reset</span>
          </button>
        </div>

        {/* Step progress bar */}
        <div className="max-w-6xl mx-auto mt-3 flex items-center gap-2">
          {steps.map((step, idx) => {
            const isActive = pathname === step.href;
            const isPast = steps.findIndex(s => s.href === pathname) > idx;
            return (
              <div key={step.href} className="flex items-center gap-2 flex-1">
                <div className={cn(
                  'flex items-center gap-1.5 text-xs font-semibold flex-1',
                  isActive ? 'text-[#007041]' : isPast ? 'text-[#007041]' : 'text-[#64748B]'
                )}>
                  <span className={cn(
                    'w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold',
                    isActive
                      ? 'bg-[#007041] text-white'
                      : isPast
                        ? 'bg-[#F0FDF4] text-[#007041] border-2 border-[#007041]'
                        : 'bg-slate-100 text-slate-400'
                  )}>
                    {isPast ? '✓' : step.num}
                  </span>
                  <span className="hidden sm:inline">{step.label}</span>
                </div>
                {idx < steps.length - 1 && (
                  <div className={cn(
                    'flex-1 h-0.5 rounded-full mx-1',
                    isPast ? 'bg-[#007041]' : 'bg-slate-200'
                  )} />
                )}
              </div>
            );
          })}
        </div>
      </header>

      <main className="flex-1">{children}</main>
    </div>
  );
}
