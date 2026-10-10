'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import { TrendingUp, AlertTriangle, ChevronRight, BarChart2, Target, BookOpen, Zap } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { evaluateFacultyTrack } from '@/lib/evaluator';
import { tracksFixture } from '@/lib/fixtures/tracks';
import { AcademicTrack } from '@/types';
import { cn } from '@/lib/utils';
import { MockDataBadge } from '@/components/ui/disclaimer-banner';

export default function FacultyDashboardPage() {
  const { faculty, setFacultyTrack } = useTechGapStore();

  const result = useMemo(
    () => evaluateFacultyTrack(faculty.selectedTrack, faculty.activeEnhancementIds),
    [faculty.selectedTrack, faculty.activeEnhancementIds]
  );

  const currentTrackMeta = tracksFixture.find((t) => t.id === faculty.selectedTrack);

  const alignmentColor =
    result.baselineAlignment >= 75
      ? 'text-[#007041]'
      : result.baselineAlignment >= 55
        ? 'text-[#0284C7]'
        : 'text-[#D97706]';

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Page Title */}
      <div className="flex items-start justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-[#0F172A] mb-1">Track Curriculum Overview</h1>
          <p className="text-[#64748B] text-sm">
            Baseline alignment metrics computed from curriculum-to-industry competency mapping.
          </p>
        </div>
        <MockDataBadge />
      </div>

      {/* Track Switcher */}
      <div className="flex flex-wrap gap-2 mb-8">
        {tracksFixture.map((track) => (
          <button
            key={track.id}
            id={`track-${track.id}`}
            onClick={() => setFacultyTrack(track.id as AcademicTrack)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm font-semibold border-2 transition-all',
              faculty.selectedTrack === track.id
                ? 'border-[#007041] bg-[#F0FDF4] text-[#007041]'
                : 'border-[#E2E8F0] bg-white text-[#64748B] hover:border-slate-300 hover:bg-slate-50'
            )}
          >
            {track.shortLabel}
          </button>
        ))}
      </div>

      {/* KPI Banner */}
      <div className="grid md:grid-cols-4 gap-4 mb-8">
        {/* Alignment Score */}
        <div className="card p-5 col-span-1">
          <div className="flex items-center gap-2 mb-2">
            <BarChart2 size={16} className="text-[#007041]" />
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wide">Baseline Alignment</span>
          </div>
          <div className={cn('text-4xl font-extrabold mb-1', alignmentColor)}>
            {result.baselineAlignment}%
          </div>
          <div className="progress-track mb-2">
            <div className="progress-fill" style={{ width: `${result.baselineAlignment}%` }} />
          </div>
          <p className="text-xs text-[#64748B]">Industry competency coverage</p>
        </div>

        {/* Covered */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Target size={16} className="text-[#007041]" />
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wide">Covered Skills</span>
          </div>
          <div className="text-4xl font-extrabold text-[#007041] mb-1">{result.coveredSkillsCount}</div>
          <p className="text-xs text-[#64748B]">of {result.totalTrackSkills} required</p>
        </div>

        {/* Gaps */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} className="text-[#D97706]" />
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wide">Identified Gaps</span>
          </div>
          <div className="text-4xl font-extrabold text-[#D97706] mb-1">{result.missingSkillsCount}</div>
          <p className="text-xs text-[#64748B]">competencies not covered</p>
        </div>

        {/* Snapshot */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <BookOpen size={16} className="text-[#0284C7]" />
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wide">Evidence Source</span>
          </div>
          <div className="text-sm font-bold text-[#0F172A] mb-1">Q3 2026 Snapshot</div>
          <p className="text-xs text-[#64748B]">N=182 illustrative job postings</p>
          <div className="mt-2 badge-mock">Controlled Sample</div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Gap Priority Table */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="px-6 py-4 border-b border-[#E2E8F0] flex items-center justify-between">
              <div>
                <h2 className="font-bold text-[#0F172A]">Industry Gap Priority Table</h2>
                <p className="text-xs text-[#64748B] mt-0.5">Competencies ranked by market demand — missing from current track curriculum</p>
              </div>
              <Link
                href="/faculty/simulate"
                className="btn-3d-blue btn-sm text-sm flex items-center gap-1.5"
              >
                <Zap size={14} />
                Simulate
              </Link>
            </div>

            {result.gapPriorities.length === 0 ? (
              <div className="px-6 py-12 text-center text-[#64748B]">
                <Target size={40} className="mx-auto mb-3 opacity-30" />
                <p className="font-medium">No gaps identified — full alignment achieved!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[#E2E8F0] bg-slate-50">
                      <th className="px-4 py-3 text-left text-xs font-bold text-[#64748B] uppercase tracking-wide">#</th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-[#64748B] uppercase tracking-wide">Competency</th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-[#64748B] uppercase tracking-wide">Category</th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-[#64748B] uppercase tracking-wide">Demand</th>
                      <th className="px-4 py-3 text-left text-xs font-bold text-[#64748B] uppercase tracking-wide">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.gapPriorities.map((gap) => (
                      <tr key={gap.skill?.id} className="border-b border-[#E2E8F0] hover:bg-slate-50 transition-colors">
                        <td className="px-4 py-3">
                          <span className={cn(
                            'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                            gap.priorityRank === 1 ? 'bg-red-100 text-red-700' :
                            gap.priorityRank === 2 ? 'bg-amber-100 text-amber-700' :
                            'bg-slate-100 text-slate-500'
                          )}>
                            {gap.priorityRank}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <p className="font-semibold text-sm text-[#0F172A]">{gap.skill?.name}</p>
                          <p className="text-xs text-[#64748B]">{gap.skill?.demandSampleCount}</p>
                        </td>
                        <td className="px-4 py-3">
                          <span className="badge-slate text-xs">{gap.skill?.category}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-16 progress-track">
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${gap.demandPercentage}%`,
                                  background: gap.demandPercentage >= 75 ? '#DC2626' : gap.demandPercentage >= 60 ? '#D97706' : '#0284C7',
                                }}
                              />
                            </div>
                            <span className="text-sm font-bold text-[#0F172A]">{gap.demandPercentage}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {gap.recommendedEnhancementId ? (
                            <Link
                              href="/faculty/simulate"
                              className="text-xs text-[#007041] font-semibold hover:underline flex items-center gap-1"
                            >
                              Simulate <ChevronRight size={12} />
                            </Link>
                          ) : (
                            <span className="text-xs text-[#64748B]">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Low-Demand Review */}
        <div className="lg:col-span-1">
          <div className="card h-fit">
            <div className="px-6 py-4 border-b border-[#E2E8F0]">
              <h2 className="font-bold text-[#0F172A]">Low-Demand Review</h2>
              <p className="text-xs text-[#64748B] mt-0.5">Topics warranting curriculum review</p>
            </div>

            {result.lowDemandFindings.length === 0 ? (
              <div className="px-6 py-8 text-center text-[#64748B] text-sm">
                No low-demand findings for this track.
              </div>
            ) : (
              <div className="px-6 py-4 flex flex-col gap-4">
                {/* Non-obsolete disclaimer */}
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800">
                  <strong>⚠️ Review Finding Only:</strong> Not designated as obsolete or recommended
                  for unilateral removal. Curriculum decisions require faculty committee review.
                </div>

                {result.lowDemandFindings.map((finding) => (
                  <div key={finding.skill.id} className="card p-4">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <p className="font-semibold text-sm text-[#0F172A]">{finding.skill.name}</p>
                      <span className="badge-amber shrink-0">{finding.skill.demandPercentage}%</span>
                    </div>
                    <p className="text-xs text-[#64748B] mb-2">{finding.associatedCourseTitle}</p>
                    <p className="text-xs text-amber-800 leading-relaxed">{finding.reviewNote}</p>
                    <div className="mt-2">
                      <TrendingUp size={11} className="inline text-slate-400 mr-1" />
                      <span className="text-xs text-slate-400">{finding.skill.demandSampleCount}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
