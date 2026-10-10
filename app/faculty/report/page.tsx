'use client';

import { useMemo } from 'react';
import { Printer, AlertTriangle, BookOpen, GraduationCap, BarChart2 } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { evaluateFacultyTrack } from '@/lib/evaluator';
import { enhancementsFixture } from '@/lib/fixtures/scenarios';
import { tracksFixture } from '@/lib/fixtures/tracks';
import Button3D from '@/components/ui/button-3d';

export default function ReportPage() {
  const { faculty } = useTechGapStore();

  const result = useMemo(
    () => evaluateFacultyTrack(faculty.selectedTrack, faculty.activeEnhancementIds),
    [faculty.selectedTrack, faculty.activeEnhancementIds]
  );

  const activeEnhancements = enhancementsFixture.filter((e) =>
    faculty.activeEnhancementIds.includes(e.id)
  );

  const trackMeta = tracksFixture.find((t) => t.id === faculty.selectedTrack);
  const hasScenario = activeEnhancements.length > 0;

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Print Action Bar - hidden in print */}
      <div className="flex items-center justify-between mb-6 no-print">
        <div>
          <h1 className="text-2xl font-extrabold text-[#0F172A] mb-1">Consolidated Academic Review Report</h1>
          <p className="text-[#64748B] text-sm">
            Native browser print — formatted for A4/Letter institutional documentation.
          </p>
        </div>
        <Button3D
          variant="primary"
          size="md"
          onClick={() => window.print()}
          className="flex items-center gap-2"
        >
          <Printer size={18} />
          Print / Save to PDF
        </Button3D>
      </div>

      {/* ── PRINTABLE REPORT DOCUMENT ── */}
      <div className="bg-white border-2 border-[#E2E8F0] rounded-2xl overflow-hidden print-card">
        {/* Letterhead */}
        <div className="bg-[#007041] text-white px-8 py-6">
          <div className="flex items-start justify-between gap-6">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <GraduationCap size={26} className="text-white" />
                </div>
                <div>
                  <p className="font-extrabold text-lg leading-tight">De La Salle University – Dasmariñas</p>
                  <p className="text-white/80 text-sm">College of Science and Computer Studies</p>
                </div>
              </div>
              <h1 className="text-2xl font-extrabold leading-tight">TechGap: Curriculum Alignment Review</h1>
              <p className="text-white/80 text-sm mt-1">Academic Year 2025–2026 | Curriculum Gap Analysis</p>
            </div>
            <div className="text-right text-xs text-white/80 shrink-0">
              <p>Dataset: Q3 2026 Snapshot (N=182)</p>
              <p className="mt-1 font-bold text-white">Curriculum Review</p>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-amber-50 border-b border-amber-200 px-8 py-3 flex items-center gap-2 text-xs text-amber-800">
          <AlertTriangle size={13} className="shrink-0" />
          <span>
            <strong>Important:</strong> This report is generated from an illustrative prototype using curated mock data.
            Figures are for academic discussion purposes only and do not represent formally validated research outcomes.
            All alignment scores reference a controlled Q3 2026 job posting sample (N=182).
          </span>
        </div>

        <div className="px-8 py-6 flex flex-col gap-8">
          {/* Section 1: Executive Summary */}
          <section>
            <h2 className="text-lg font-extrabold text-[#0F172A] mb-3 flex items-center gap-2 border-b-2 border-[#E2E8F0] pb-2">
              <BarChart2 size={18} className="text-[#007041]" />
              1. Executive Summary
            </h2>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div className="print-card bg-[#F0FDF4] border border-[#A7F3D0] rounded-xl p-4 text-center">
                <div className="text-3xl font-extrabold text-[#007041] mb-1">{result.baselineAlignment}%</div>
                <div className="text-xs text-[#64748B]">Baseline Alignment</div>
              </div>
              <div className="print-card bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                <div className="text-3xl font-extrabold text-[#D97706] mb-1">{result.missingSkillsCount}</div>
                <div className="text-xs text-[#64748B]">Identified Gaps</div>
              </div>
              <div className="print-card bg-sky-50 border border-sky-200 rounded-xl p-4 text-center">
                <div className="text-3xl font-extrabold text-[#0284C7] mb-1">{result.totalTrackSkills}</div>
                <div className="text-xs text-[#64748B]">Total Industry Skills</div>
              </div>
            </div>
            <p className="text-sm text-[#64748B] leading-relaxed">
              The <strong>{trackMeta?.label || faculty.selectedTrack}</strong> curriculum was evaluated
              against {result.totalTrackSkills} industry-required competencies derived from {result.totalTrackSkills > 0 ? 'a controlled Q3 2026 sample of 182 illustrative job postings' : 'industry benchmarks'}.
              The baseline alignment score of <strong>{result.baselineAlignment}%</strong> ({result.coveredSkillsCount} of {result.totalTrackSkills} competencies)
              indicates that {result.missingSkillsCount} prioritized competencies are not yet formally addressed
              in the current curriculum structure.
            </p>
          </section>

          {/* Section 2: Gap Priorities */}
          <section className="page-break">
            <h2 className="text-lg font-extrabold text-[#0F172A] mb-3 flex items-center gap-2 border-b-2 border-[#E2E8F0] pb-2">
              <AlertTriangle size={18} className="text-[#D97706]" />
              2. Prioritized Industry Gaps & Demand Evidence
            </h2>
            {result.gapPriorities.length > 0 ? (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border border-[#E2E8F0]">
                    <th className="px-3 py-2 text-left font-bold text-[#64748B] text-xs">Priority</th>
                    <th className="px-3 py-2 text-left font-bold text-[#64748B] text-xs">Competency</th>
                    <th className="px-3 py-2 text-left font-bold text-[#64748B] text-xs">Category</th>
                    <th className="px-3 py-2 text-right font-bold text-[#64748B] text-xs">Demand %</th>
                    <th className="px-3 py-2 text-left font-bold text-[#64748B] text-xs">Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {result.gapPriorities.map((gap) => (
                    <tr key={gap.skill?.id} className="border-b border-[#E2E8F0]">
                      <td className="px-3 py-2 font-bold text-center">{gap.priorityRank}</td>
                      <td className="px-3 py-2 font-semibold">{gap.skill?.name}</td>
                      <td className="px-3 py-2 text-[#64748B] text-xs">{gap.skill?.category}</td>
                      <td className="px-3 py-2 text-right font-bold text-[#007041]">{gap.demandPercentage}%</td>
                      <td className="px-3 py-2 text-xs text-[#64748B]">{gap.skill?.demandSampleCount}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-sm text-[#64748B]">No gaps identified for this track.</p>
            )}
          </section>

          {/* Section 3: Low-Demand Review */}
          <section>
            <h2 className="text-lg font-extrabold text-[#0F172A] mb-3 flex items-center gap-2 border-b-2 border-[#E2E8F0] pb-2">
              <BookOpen size={18} className="text-[#64748B]" />
              3. Low-Demand Academic Review Findings
            </h2>
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-3 text-xs text-amber-800">
              <strong>Disclaimer:</strong> The following findings are review observations only. They do not constitute
              recommendations for unilateral removal. Any curriculum modification must undergo formal faculty committee review
              per institutional academic governance procedures.
            </div>
            {result.lowDemandFindings.length > 0 ? (
              <div className="flex flex-col gap-3">
                {result.lowDemandFindings.map((f) => (
                  <div key={f.skill.id} className="print-card border border-[#E2E8F0] rounded-xl p-4">
                    <div className="flex items-start justify-between gap-4 mb-1">
                      <p className="font-semibold text-sm text-[#0F172A]">{f.skill.name}</p>
                      <span className="text-sm font-bold text-[#D97706] shrink-0">{f.skill.demandPercentage}% demand</span>
                    </div>
                    <p className="text-xs text-[#64748B] mb-1">{f.associatedCourseTitle}</p>
                    <p className="text-xs text-amber-800 leading-relaxed">{f.reviewNote}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[#64748B]">No low-demand findings for this track.</p>
            )}
          </section>

          {/* Section 4: Scenario (conditional) */}
          {hasScenario && (
            <section className="page-break">
              <h2 className="text-lg font-extrabold text-[#0F172A] mb-1 flex items-center gap-2 border-b-2 border-[#E2E8F0] pb-2">
                <AlertTriangle size={18} className="text-[#D97706]" />
                4. Hypothetical Revision Scenario
              </h2>
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4 text-xs text-amber-800 font-bold">
                ⚠️ HYPOTHETICAL REVISION SCENARIO — NON-OFFICIAL.
                The following additive proposals are illustrative only and have NOT been formally approved or implemented.
              </div>
              <div className="grid md:grid-cols-2 gap-3 mb-4">
                <div className="print-card bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
                  <p className="text-xs text-[#64748B] mb-1">Baseline Alignment</p>
                  <p className="text-2xl font-extrabold text-[#0F172A]">{result.baselineAlignment}%</p>
                </div>
                <div className="print-card bg-[#F0FDF4] border border-[#A7F3D0] rounded-xl p-4 text-center">
                  <p className="text-xs text-[#64748B] mb-1">Projected Alignment</p>
                  <p className="text-2xl font-extrabold text-[#007041]">{result.projectedAlignment}%</p>
                  <p className="text-xs text-[#007041] font-semibold">+{result.projectedAlignment - result.baselineAlignment}%</p>
                </div>
              </div>
              {activeEnhancements.map((enh) => (
                <div key={enh.id} className="print-card border border-[#E2E8F0] rounded-xl p-4 mb-3">
                  <p className="font-bold text-sm text-[#0F172A] mb-1">{enh.title}</p>
                  <p className="text-xs text-[#64748B] mb-1">Target: {enh.targetCourseTitle}</p>
                  <p className="text-xs text-[#007041] font-semibold mb-2">Added Skills: {enh.addedSkills.map(s => s.name).join(', ')}</p>
                  <p className="text-xs text-[#64748B] leading-relaxed">{enh.rationale}</p>
                </div>
              ))}
            </section>
          )}

        </div>
      </div>
    </div>
  );
}
