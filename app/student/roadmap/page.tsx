'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  CheckCircle2,
  Lock,
  ChevronRight,
  ExternalLink,
  BookOpen,
  Clock,
  X,
  Zap,
  Target,
  TrendingUp,
  ChevronLeft,
  GraduationCap,
  Star,
} from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { evaluateStudent } from '@/lib/evaluator';
import { Skill, LearningResource } from '@/types';
import { cn } from '@/lib/utils';
import Button3D from '@/components/ui/button-3d';

// ─── Node position pattern for serpentine S-curve ─────────────────────────────
// Pattern cycles: center → right → center → left → center → right ...
const POSITIONS = ['center', 'right', 'center', 'left'] as const;
type Position = (typeof POSITIONS)[number];

const positionClass: Record<Position, string> = {
  center: 'mx-auto',
  right: 'ml-auto mr-8',
  left: 'ml-8 mr-auto',
};

// ─── Provider color map ───────────────────────────────────────────────────────
const providerColor: Record<string, string> = {
  freeCodeCamp: 'bg-amber-50 text-amber-800 border-amber-200',
  'MDN Web Docs': 'bg-sky-50 text-sky-800 border-sky-200',
  Coursera: 'bg-blue-50 text-blue-800 border-blue-200',
  'Official Docs': 'bg-slate-50 text-slate-700 border-slate-200',
  Kaggle: 'bg-cyan-50 text-cyan-800 border-cyan-200',
};

// ─── Skill Inspection Drawer ──────────────────────────────────────────────────
function SkillDrawer({
  skill,
  status,
  upcomingCourseTitle,
  resources,
  onClose,
}: {
  skill: Skill;
  status: 'completed' | 'current' | 'future_gap';
  upcomingCourseTitle?: string;
  resources: LearningResource[];
  onClose: () => void;
}) {
  const statusConfig = {
    completed: { label: 'Competency Acquired', color: 'badge-green', icon: CheckCircle2 },
    current: { label: 'Next Target (Up-Next)', color: 'badge-blue', icon: Target },
    future_gap: { label: 'Gap Identified', color: 'badge-amber', icon: Lock },
  }[status];

  const StatusIcon = statusConfig.icon;

  return (
    <>
      {/* Overlay */}
      <div className="skill-drawer-overlay" onClick={onClose} aria-hidden="true" />

      {/* Drawer */}
      <aside className="skill-drawer" role="complementary" aria-label="Skill details">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b-2 border-[#E2E8F0] px-6 py-4 flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className={cn(statusConfig.color, 'mb-2 inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border')}>
              <StatusIcon size={12} />
              {statusConfig.label}
            </div>
            <h2 className="font-extrabold text-xl text-[#0F172A] leading-tight">{skill.name}</h2>
            <p className="text-xs text-[#64748B] mt-1">{skill.category}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-slate-100 text-[#64748B] hover:text-[#0F172A] transition-colors shrink-0"
            aria-label="Close drawer"
          >
            <X size={20} />
          </button>
        </div>

        <div className="px-6 py-5 flex flex-col gap-5">
          {/* Market Demand */}
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp size={16} className="text-[#007041]" />
              <h3 className="font-bold text-sm text-[#0F172A]">Industry Demand</h3>
              <span className="badge-mock text-xs ml-auto">Illustrative Mock</span>
            </div>
            <div className="flex items-end gap-2 mb-2">
              <span className="text-3xl font-extrabold text-[#007041]">{skill.demandPercentage}%</span>
              <span className="text-[#64748B] text-sm pb-1">of postings</span>
            </div>
            <div className="progress-track mb-2">
              <div className="progress-fill" style={{ width: `${skill.demandPercentage}%` }} />
            </div>
            <p className="text-xs text-[#64748B]">{skill.demandSampleCount}</p>

            {skill.isLowDemand && (
              <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
                <strong>Low-Demand Review Finding:</strong> {skill.lowDemandRationale}
              </div>
            )}
          </div>

          {/* Academic Evidence */}
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <GraduationCap size={16} className="text-[#0284C7]" />
              <h3 className="font-bold text-sm text-[#0F172A]">Academic Evidence</h3>
            </div>
            {status === 'completed' ? (
              <div className="flex items-center gap-2 text-sm text-[#007041] font-semibold">
                <CheckCircle2 size={16} />
                Covered by your completed coursework
              </div>
            ) : upcomingCourseTitle ? (
              <div>
                <div className="badge-blue mb-2">🔒 Logical Coverage</div>
                <p className="text-sm text-[#0F172A] font-medium">Covered in upcoming course:</p>
                <p className="text-sm text-[#0284C7] font-semibold mt-1">{upcomingCourseTitle}</p>
                <p className="text-xs text-[#64748B] mt-2">
                  This skill is addressed in your remaining curriculum — completing this course will
                  provide academic coverage per course learning outcomes.
                </p>
              </div>
            ) : (
              <div>
                <div className="badge-amber mb-2">⚠️ Gap Identified</div>
                <p className="text-sm text-[#64748B]">
                  This competency is not currently addressed in your selected coursework or
                  remaining track curriculum. Self-directed upskilling is recommended.
                </p>
              </div>
            )}
          </div>

          {/* Upskilling Resources */}
          {resources.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <BookOpen size={16} className="text-[#007041]" />
                <h3 className="font-bold text-sm text-[#0F172A]">Curated Learning Resources</h3>
              </div>
              <div className="flex flex-col gap-2">
                {resources.map((r, idx) => (
                  <a
                    key={idx}
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block card p-3 hover:border-[#007041] hover:shadow-sm transition-all group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className={cn(
                            'text-xs font-semibold px-2 py-0.5 rounded border',
                            providerColor[r.provider] || 'bg-slate-50 text-slate-700 border-slate-200'
                          )}>
                            {r.provider}
                          </span>
                          <span className="badge-slate text-xs">{r.type}</span>
                        </div>
                        <p className="text-sm font-semibold text-[#0F172A] group-hover:text-[#007041] transition-colors">
                          {r.title}
                        </p>
                        <div className="flex items-center gap-1.5 mt-1.5 text-xs text-[#64748B]">
                          <Clock size={11} />
                          <span>~{r.estimatedHours} hours</span>
                        </div>
                      </div>
                      <ExternalLink size={14} className="text-[#64748B] group-hover:text-[#007041] shrink-0 mt-1 transition-colors" />
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}

          {resources.length === 0 && (
            <div className="text-center text-[#64748B] py-4 text-sm">
              No specific resources curated yet for this competency.
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

// ─── Milestone Node ────────────────────────────────────────────────────────────
function MilestoneNode({
  skill,
  status,
  index,
  onOpen,
}: {
  skill: Skill;
  status: 'completed' | 'current' | 'future_gap';
  index: number;
  onOpen: () => void;
}) {
  const position = POSITIONS[index % POSITIONS.length];
  const isCompleted = status === 'completed';
  const isCurrent = status === 'current';

  const shortName = skill.name.length > 22 ? skill.name.slice(0, 20) + '…' : skill.name;

  return (
    <div className={cn('flex flex-col items-center w-32 md:w-36', positionClass[position])}>
      <div className="relative">
        {/* Radar pulse for current node */}
        {isCurrent && (
          <>
            <div className="radar-ring absolute -inset-4 opacity-70" style={{ animationDelay: '0s' }} />
            <div className="radar-ring absolute -inset-6 opacity-40" style={{ animationDelay: '0.5s' }} />
          </>
        )}

        {/* Main Node */}
        <button
          onClick={onOpen}
          id={`node-${skill.id}`}
          aria-label={`${skill.name} - ${status}`}
          className={cn(
            'w-20 h-20 md:w-24 md:h-24 rounded-full flex flex-col items-center justify-center gap-1 focus-visible:outline-2 focus-visible:outline-[#007041]',
            isCompleted && 'milestone-node-completed',
            isCurrent && 'milestone-node-current',
            status === 'future_gap' && 'milestone-node-gap'
          )}
        >
          {isCompleted && <CheckCircle2 size={26} />}
          {isCurrent && <Zap size={26} />}
          {status === 'future_gap' && <Lock size={22} />}
          <span className="text-[10px] font-bold text-center leading-tight px-2">
            {isCompleted ? '✓' : `#${index + 1}`}
          </span>
        </button>
      </div>

      {/* Label below node */}
      <p className="mt-2 text-xs font-semibold text-center text-[#0F172A] leading-tight">
        {shortName}
      </p>
      <p className={cn(
        'text-[10px] mt-0.5 font-medium',
        isCompleted ? 'text-[#007041]' : isCurrent ? 'text-[#0284C7]' : 'text-[#64748B]'
      )}>
        {isCompleted ? 'Acquired' : isCurrent ? 'Up Next' : 'Gap'}
      </p>
      <span className="text-[10px] text-[#64748B] mt-0.5">{skill.demandPercentage}% demand</span>
    </div>
  );
}

// ─── Main Roadmap Page ────────────────────────────────────────────────────────
export default function RoadmapPage() {
  const router = useRouter();
  const { student } = useTechGapStore();
  const [activeNode, setActiveNode] = useState<{
    skill: Skill;
    status: 'completed' | 'current' | 'future_gap';
    upcomingCourseTitle?: string;
    resources: LearningResource[];
  } | null>(null);

  const result = useMemo(
    () => evaluateStudent(student.track, student.selectedCourseIds, student.selectedRoleId),
    [student.track, student.selectedCourseIds, student.selectedRoleId]
  );

  if (!result) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <GraduationCap size={48} className="mx-auto mb-4 text-slate-300" />
        <h2 className="font-bold text-xl text-[#0F172A] mb-2">No Career Target Selected</h2>
        <p className="text-[#64748B] mb-6">
          Select a career target and complete your setup to see your roadmap.
        </p>
        <Button3D variant="primary" size="md" onClick={() => router.push('/student/setup')}>
          Go to Setup
        </Button3D>
      </div>
    );
  }

  const completedCount = result.completedSkills.length;
  const gapCount = result.currentGaps.length;
  const futureCount = result.futureCurriculumCoverage.length;

  return (
    <div className="flex w-full min-h-[calc(100vh-105px)]">
      {/* ── Main Stage: S-Curve Path (Expands across available screen width) ── */}
      <div className="flex-1 overflow-y-auto px-6 lg:px-12 py-8 flex flex-col items-center">
        <div className="w-full max-w-2xl mb-6">
          <h1 className="text-2xl font-extrabold text-[#0F172A] mb-1">Your Learning Roadmap</h1>
          <p className="text-[#64748B] text-sm">
            Tap any milestone to inspect skill details and curated learning resources.
          </p>
        </div>

        {/* START Banner */}
        <div className="mx-auto w-fit mb-6">
          <div className="bg-[#007041] text-white rounded-2xl px-8 py-3 text-center shadow-lg"
            style={{ boxShadow: '0 6px 0 #00502E' }}>
            <div className="flex items-center gap-2">
              <Star size={18} className="text-yellow-300" />
              <span className="font-extrabold tracking-widest text-sm">START YOUR JOURNEY</span>
              <Star size={18} className="text-yellow-300" />
            </div>
            <p className="text-[#A7F3D0] text-xs mt-0.5">{result.roleTitle}</p>
          </div>
        </div>

        {/* S-Curve Nodes */}
        <div className="flex flex-col gap-6 w-full max-w-2xl">
          {result.roadmapNodes.map((node, idx) => {
            if (!node.skill) return null;
            return (
              <div key={node.skill.id}>
                {/* Connector dashes */}
                {idx > 0 && (
                  <div className="flex justify-center mb-2 -mt-2">
                    <div className="w-0.5 h-8 border-l-2 border-dashed border-slate-300" />
                  </div>
                )}

                <div className="flex items-center relative">
                  <MilestoneNode
                    skill={node.skill}
                    status={node.status}
                    index={idx}
                    onOpen={() => setActiveNode(node)}
                  />

                  {/* Course overlap tag (right side) */}
                  {node.upcomingCourseTitle && node.status !== 'completed' && (
                    <div className="absolute -right-2 md:right-4 top-1/2 -translate-y-1/2 hidden md:block">
                      <div className="bg-sky-50 border border-sky-200 rounded-lg px-2 py-1 text-xs text-[#0284C7] font-medium max-w-[140px] leading-tight">
                        📚 {node.upcomingCourseTitle.split('·')[0].trim()}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* END Banner */}
          <div className="flex justify-center mt-4">
            <div className="border-2 border-dashed border-slate-300 rounded-2xl px-8 py-3 text-center text-[#64748B]">
              <p className="font-bold text-sm">🏁 Career Ready</p>
              <p className="text-xs">Complete all milestones to achieve full alignment</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Right Sticky Rail: Alignment KPIs (Anchored to right edge, full width on right) ── */}
      <div className="w-80 xl:w-96 shrink-0 border-l-2 border-[#E2E8F0] bg-white sticky top-0 h-[calc(100vh-105px)] overflow-y-auto p-6 flex flex-col gap-5">
        {/* Role title */}
        <div>
          <p className="text-xs text-[#64748B] font-semibold uppercase tracking-wide mb-1">Career Target</p>
          <h2 className="font-extrabold text-[#0F172A] text-base leading-tight">{result.roleTitle}</h2>
          <p className="text-xs text-[#64748B] mt-0.5">{student.yearLevel} · {student.track.replace(/_/g, ' ')}</p>
        </div>

        {/* Big Alignment Score Circle */}
        <div className="flex flex-col items-center">
          <div className="relative w-28 h-28">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#E2E8F0" strokeWidth="10" />
              <circle
                cx="50" cy="50" r="42" fill="none"
                stroke="#007041" strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 42}`}
                strokeDashoffset={`${2 * Math.PI * 42 * (1 - result.overallScore / 100)}`}
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-extrabold text-[#007041]">{result.overallScore}%</span>
              <span className="text-[10px] text-[#64748B] font-medium">alignment</span>
            </div>
          </div>
          <span className="badge-mock text-xs mt-2">Illustrative Mock</span>
        </div>

        {/* KPI breakdown */}
        <div className="card p-4 flex flex-col gap-3">
          <div className="flex justify-between items-center">
            <span className="text-xs text-[#64748B]">✅ Acquired Skills</span>
            <span className="font-extrabold text-[#007041]">{completedCount}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs text-[#64748B]">⚠️ Current Gaps</span>
            <span className="font-extrabold text-[#D97706]">{gapCount}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs text-[#64748B]">📚 Future Coverage</span>
            <span className="font-extrabold text-[#0284C7]">{futureCount}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs text-[#64748B]">Total Required</span>
            <span className="font-extrabold text-[#0F172A]">{result.roadmapNodes.length}</span>
          </div>
        </div>

        {/* Quick links */}
        <div className="flex flex-col gap-2">
          <button
            onClick={() => router.push('/student/careers')}
            className="text-xs text-[#007041] hover:underline font-semibold text-left flex items-center gap-1"
          >
            <ChevronLeft size={13} />
            Change Career Target
          </button>
          <button
            onClick={() => router.push('/student/setup')}
            className="text-xs text-[#007041] hover:underline font-semibold text-left flex items-center gap-1"
          >
            <ChevronLeft size={13} />
            Edit Course Selections
          </button>
        </div>

        {/* Legend */}
        <div className="mt-auto pt-4 border-t border-[#E2E8F0]">
          <p className="text-xs font-bold text-[#64748B] mb-2 uppercase tracking-wide">Legend</p>
          <div className="flex flex-col gap-1.5 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#007041] rounded-full shrink-0" />
              <span className="text-[#64748B]">Competency Acquired</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#0284C7] rounded-full shrink-0" />
              <span className="text-[#64748B]">Up Next (Current)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-slate-200 rounded-full border-2 border-slate-300 shrink-0" />
              <span className="text-[#64748B]">Gap / Locked</span>
            </div>
          </div>
        </div>
      </div>

      {/* Skill Drawer */}
      {activeNode && (
        <SkillDrawer
          skill={activeNode.skill}
          status={activeNode.status}
          upcomingCourseTitle={activeNode.upcomingCourseTitle}
          resources={activeNode.resources}
          onClose={() => setActiveNode(null)}
        />
      )}
    </div>
  );
}
