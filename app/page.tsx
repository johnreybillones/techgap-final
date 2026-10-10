'use client';

import { useRouter } from 'next/navigation';
import { GraduationCap, LayoutDashboard, RotateCcw, BookOpen, ChevronRight, FlaskConical, AlertTriangle } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import Button3D from '@/components/ui/button-3d';
import { coursesFixture } from '@/lib/fixtures/courses';

export default function HomePage() {
  const router = useRouter();
  const { activeRole, student, setActiveRole, resetAll } = useTechGapStore();

  const hasStudentContext = student.selectedCourseIds.length > 0;
  const trackLabel = student.track.replace(/_/g, ' ');
  const selectedCourseCount = student.selectedCourseIds.filter(id =>
    coursesFixture.some(c => c.id === id && c.track === student.track)
  ).length;

  const handleStudentEntry = () => {
    setActiveRole('student');
    if (hasStudentContext) {
      router.push('/student/roadmap');
    } else {
      router.push('/student/setup');
    }
  };

  const handleFacultyEntry = () => {
    setActiveRole('faculty');
    router.push('/faculty');
  };

  const handleReset = () => {
    if (confirm('Reset all saved data? This will clear course selections and faculty scenarios.')) {
      resetAll();
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-surface-bg flex flex-col">

      {/* Header */}
      <header className="bg-white border-b-2 border-[#E2E8F0] px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#007041] rounded-xl flex items-center justify-center shadow-md">
              <span className="text-white font-extrabold text-base tracking-tight">TG</span>
            </div>
            <div>
              <h1 className="font-extrabold text-xl text-[#0F172A] leading-tight">TechGap</h1>
              <p className="text-xs text-[#64748B] font-medium">DLSU-D Curriculum Alignment Tool</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge-mock text-xs">
              <FlaskConical size={11} />
              Prototype v1.0
            </span>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16">
        <div className="max-w-5xl w-full">
          {/* Title Section */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#F0FDF4] border border-[#A7F3D0] text-[#007041] text-sm font-semibold mb-6">
              <BookOpen size={15} />
              De La Salle University – Dasmariñas
            </div>
            <h2 className="text-4xl md:text-5xl font-extrabold text-[#0F172A] leading-tight mb-4">
              Bridge the gap between{' '}
              <span className="text-[#007041]">curriculum</span> and{' '}
              <span className="text-[#0284C7]">industry</span>.
            </h2>
            <p className="text-lg text-[#64748B] max-w-2xl mx-auto leading-relaxed">
              TechGap maps your academic coursework to real industry competency demands,
              helping students visualize career readiness and helping faculty identify
              curriculum gaps with evidence-backed priorities.
            </p>
          </div>

          {/* Role Selection Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Student Card */}
            <div className="card p-8 flex flex-col gap-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#F0FDF4] rounded-bl-full opacity-60" />
              <div className="relative">
                <div className="w-14 h-14 bg-[#007041] rounded-2xl flex items-center justify-center mb-4 shadow-md"
                  style={{ boxShadow: '0 4px 0 #00502E' }}>
                  <GraduationCap size={28} className="text-white" />
                </div>
                <h3 className="text-xl font-bold text-[#0F172A] mb-2">Student Experience</h3>
                <p className="text-[#64748B] text-sm leading-relaxed mb-4">
                  Explore your career alignment, map your completed courses, and unlock
                  a personalized upskilling roadmap with real learning resources.
                </p>

                {/* Resume context */}
                {hasStudentContext && (
                  <div className="bg-[#F0FDF4] border border-[#A7F3D0] rounded-xl p-3 mb-4 text-sm">
                    <p className="text-[#007041] font-semibold text-xs mb-1">📌 Resume Previous Session</p>
                    <p className="text-[#0F172A] font-medium">{student.yearLevel} · {trackLabel}</p>
                    <p className="text-[#64748B] text-xs mt-0.5">{selectedCourseCount} courses selected</p>
                  </div>
                )}

                <div className="flex flex-col gap-2">
                  <Button3D variant="primary" size="md" onClick={handleStudentEntry} className="w-full">
                    {hasStudentContext ? (
                      <>Continue Journey <ChevronRight size={18} /></>
                    ) : (
                      <>Start Student Journey <ChevronRight size={18} /></>
                    )}
                  </Button3D>
                  {hasStudentContext && (
                    <button
                      onClick={() => { setActiveRole('student'); router.push('/student/setup'); }}
                      className="text-sm text-[#64748B] hover:text-[#007041] underline underline-offset-2 transition-colors"
                    >
                      Start Fresh Instead
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Faculty Card */}
            <div className="card p-8 flex flex-col gap-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-sky-50 rounded-bl-full opacity-60" />
              <div className="relative">
                <div className="w-14 h-14 bg-[#0284C7] rounded-2xl flex items-center justify-center mb-4 shadow-md"
                  style={{ boxShadow: '0 4px 0 #075985' }}>
                  <LayoutDashboard size={28} className="text-white" />
                </div>
                <h3 className="text-xl font-bold text-[#0F172A] mb-2">Faculty / Academic Dashboard</h3>
                <p className="text-[#64748B] text-sm leading-relaxed mb-4">
                  Review curriculum alignment across all four tracks, prioritize industry gaps,
                  simulate additive revisions, and generate consolidated academic review reports.
                </p>

                <div className="bg-sky-50 border border-sky-200 rounded-xl p-3 mb-4 text-sm">
                  <p className="text-[#0284C7] font-semibold text-xs mb-1">🗂 Available Tools</p>
                  <div className="grid grid-cols-2 gap-1 text-xs text-slate-600">
                    <span>• Track Dashboard</span>
                    <span>• Scenario Sandbox</span>
                    <span>• Printable Report</span>
                    <span>• Upload Preview</span>
                  </div>
                </div>

                <Button3D variant="outline" size="md" onClick={handleFacultyEntry} className="w-full">
                  Enter Academic Dashboard <ChevronRight size={18} />
                </Button3D>
              </div>
            </div>
          </div>

          {/* What is TechGap */}
          <div className="card p-6 mb-6 bg-white">
            <div className="grid md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-2xl font-extrabold text-[#007041] mb-1">4 Tracks</div>
                <p className="text-xs text-[#64748B]">BSCS IS, BSCS GD, BSIT NT, BSIT WD</p>
              </div>
              <div>
                <div className="text-2xl font-extrabold text-[#0284C7] mb-1">182 Postings</div>
                <p className="text-xs text-[#64748B]">Q3 2026 illustrative job snapshot</p>
              </div>
              <div>
                <div className="text-2xl font-extrabold text-[#D97706] mb-1">11 Roles</div>
                <p className="text-xs text-[#64748B]">Industry career targets across all tracks</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#E2E8F0] bg-white px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between text-xs text-[#64748B]">
          <span>TechGap Mock UI · DLSU-D Research Prototype · 2026</span>
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 hover:text-red-600 transition-colors"
          >
            <RotateCcw size={12} />
            Reset All Data
          </button>
        </div>
      </footer>
    </div>
  );
}
