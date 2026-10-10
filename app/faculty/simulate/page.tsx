'use client';

import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { RotateCcw, Plus, CheckSquare, Square, TrendingUp, TrendingDown, Minus, Zap, BookOpen, Target } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { evaluateFacultyTrack } from '@/lib/evaluator';
import { enhancementsFixture } from '@/lib/fixtures/scenarios';
import { tracksFixture } from '@/lib/fixtures/tracks';
import { AcademicTrack } from '@/types';
import { cn } from '@/lib/utils';
import Button3D from '@/components/ui/button-3d';
import { MockDataBadge } from '@/components/ui/disclaimer-banner';

export default function SimulatePage() {
  const router = useRouter();
  const { faculty, setFacultyTrack, toggleEnhancement, resetFacultyScenario } = useTechGapStore();

  // Filter enhancements relevant to the selected track
  const trackEnhancements = useMemo(() => {
    const trackCodes = {
      BSIT_WEB_DEVELOPMENT: ['ITWB', 'enh-wd'],
      BSIT_NETWORK_TECHNOLOGY: ['ITNT', 'enh-nt'],
      BSCS_INTELLIGENT_SYSTEMS: ['CSIS', 'enh-is'],
      BSCS_GAME_DEVELOPMENT: ['CSGD', 'enh-gd'],
    }[faculty.selectedTrack] || [];
    return enhancementsFixture.filter((e) =>
      trackCodes.some((code) => e.id.includes(code) || e.targetCourseId.includes(code.replace('enh-', '').toUpperCase()))
    );
  }, [faculty.selectedTrack]);

  const result = useMemo(
    () => evaluateFacultyTrack(faculty.selectedTrack, faculty.activeEnhancementIds),
    [faculty.selectedTrack, faculty.activeEnhancementIds]
  );

  const delta = result.projectedAlignment - result.baselineAlignment;
  const gapDelta = result.missingSkillsCount - (result.totalTrackSkills - Math.round((result.projectedAlignment / 100) * result.totalTrackSkills));

  const isToggled = (id: string) => faculty.activeEnhancementIds.includes(id);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-[#0F172A] mb-1">Scenario Simulation Sandbox</h1>
          <p className="text-[#64748B] text-sm">
            Toggle additive curriculum enhancements and observe real-time alignment impacts.
            All proposals are purely additive — no unit reduction or course removal.
          </p>
        </div>
        <MockDataBadge />
      </div>

      {/* Track Switcher */}
      <div className="flex flex-wrap gap-2 mb-6">
        {tracksFixture.map((track) => (
          <button
            key={track.id}
            onClick={() => setFacultyTrack(track.id as AcademicTrack)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm font-semibold border-2 transition-all',
              faculty.selectedTrack === track.id
                ? 'border-[#007041] bg-[#F0FDF4] text-[#007041]'
                : 'border-[#E2E8F0] bg-white text-[#64748B] hover:border-slate-300'
            )}
          >
            {track.shortLabel}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* ── Left: Enhancement Catalog ── */}
        <div>
          <div className="card">
            <div className="px-6 py-4 border-b border-[#E2E8F0] flex items-center justify-between">
              <div>
                <h2 className="font-bold text-[#0F172A]">Additive Enhancement Catalog</h2>
                <p className="text-xs text-[#64748B] mt-0.5">Toggle proposals to see projected impact</p>
              </div>
              <span className="badge-green">{faculty.activeEnhancementIds.length} active</span>
            </div>

            <div className="px-6 py-4 flex flex-col gap-4">
              {/* Additive constraint notice */}
              <div className="bg-[#F0FDF4] border border-[#A7F3D0] rounded-xl p-3 text-xs text-[#007041]">
                <strong>📌 Additive-Only Constraint:</strong> Proposals embed new competencies into existing
                course structures. No existing units, assessments, or courses are removed or replaced.
              </div>

              {trackEnhancements.length === 0 && (
                <div className="text-center text-[#64748B] py-8 text-sm">
                  No enhancements configured for this track yet.
                </div>
              )}

              {trackEnhancements.map((enh) => {
                const active = isToggled(enh.id);
                return (
                  <button
                    key={enh.id}
                    id={`enh-${enh.id}`}
                    onClick={() => toggleEnhancement(enh.id)}
                    className={cn(
                      'text-left w-full p-4 rounded-xl border-2 transition-all duration-200',
                      active
                        ? 'border-[#007041] bg-[#F0FDF4]'
                        : 'border-[#E2E8F0] bg-white hover:border-slate-300'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 shrink-0">
                        {active
                          ? <CheckSquare size={20} className="text-[#007041]" />
                          : <Square size={20} className="text-slate-300" />
                        }
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h3 className="font-bold text-sm text-[#0F172A] leading-tight">{enh.title}</h3>
                          <span className={cn(
                            'text-xs font-bold shrink-0 px-2 py-0.5 rounded',
                            active ? 'bg-[#007041] text-white' : 'bg-slate-100 text-[#64748B]'
                          )}>
                            +{enh.projectedAlignmentGain.toFixed(1)}%
                          </span>
                        </div>

                        <p className="text-xs text-[#64748B] mb-2 font-medium">
                          📎 {enh.targetCourseTitle}
                        </p>

                        {/* Added skills */}
                        <div className="flex flex-wrap gap-1 mb-2">
                          {enh.addedSkills.map((s) => (
                            <span key={s.id} className={cn(
                              'text-xs px-2 py-0.5 rounded-full border font-medium',
                              active ? 'bg-[#007041]/10 text-[#007041] border-[#007041]/30' : 'badge-slate'
                            )}>
                              <Plus size={9} className="inline mr-0.5" />{s.name}
                            </span>
                          ))}
                        </div>

                        <p className="text-xs text-[#64748B] leading-relaxed">{enh.rationale}</p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* ── Right: Impact Comparison ── */}
        <div className="flex flex-col gap-4">
          {/* Side-by-side KPI card */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-bold text-[#0F172A]">Real-Time Impact Comparison</h2>
              <MockDataBadge />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-5">
              {/* Baseline */}
              <div className="bg-slate-50 rounded-xl p-4 text-center border-2 border-[#E2E8F0]">
                <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wide mb-2">Baseline</p>
                <div className="text-4xl font-extrabold text-[#0F172A] mb-1">{result.baselineAlignment}%</div>
                <p className="text-xs text-[#64748B]">Industry Coverage</p>
                <p className="text-xs text-[#64748B] mt-1">{result.missingSkillsCount} gaps</p>
              </div>

              {/* Projected */}
              <div className={cn(
                'rounded-xl p-4 text-center border-2',
                delta > 0 ? 'bg-[#F0FDF4] border-[#007041]' : 'bg-slate-50 border-[#E2E8F0]'
              )}>
                <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wide mb-2">Projected</p>
                <div className={cn(
                  'text-4xl font-extrabold mb-1',
                  delta > 0 ? 'text-[#007041]' : 'text-[#0F172A]'
                )}>
                  {result.projectedAlignment}%
                </div>
                {delta > 0 ? (
                  <div className="flex items-center justify-center gap-1 text-[#007041] font-bold text-sm">
                    <TrendingUp size={15} />
                    +{delta}%
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-1 text-[#64748B] text-sm">
                    <Minus size={14} />
                    No change
                  </div>
                )}
                <p className="text-xs text-[#64748B] mt-1">
                  {Math.round((result.projectedAlignment / 100) * result.totalTrackSkills)} / {result.totalTrackSkills} skills
                </p>
              </div>
            </div>

            {/* Delta progress bar */}
            <div className="mb-4">
              <div className="flex justify-between text-xs text-[#64748B] mb-1">
                <span>Industry Coverage Progress</span>
                <span className="font-semibold">{result.projectedAlignment}%</span>
              </div>
              <div className="h-4 bg-slate-100 rounded-full overflow-hidden border border-slate-200 relative">
                {/* Baseline fill */}
                <div
                  className="h-full rounded-full bg-slate-300 absolute left-0"
                  style={{ width: `${result.baselineAlignment}%` }}
                />
                {/* Projected fill */}
                <div
                  className="h-full rounded-full absolute left-0 transition-all duration-700"
                  style={{
                    width: `${result.projectedAlignment}%`,
                    background: 'linear-gradient(90deg, #007041, #34D399)',
                  }}
                />
              </div>
              <div className="flex items-center gap-3 mt-1.5 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded bg-slate-300" />
                  <span className="text-[#64748B]">Baseline</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded" style={{ background: '#007041' }} />
                  <span className="text-[#64748B]">Projected</span>
                </div>
              </div>
            </div>

            {/* Gap delta */}
            {delta > 0 && (
              <div className="bg-[#F0FDF4] border border-[#A7F3D0] rounded-xl p-3 text-sm">
                <div className="flex items-center gap-2 text-[#007041] font-bold mb-1">
                  <TrendingDown size={16} />
                  Gap Reduction
                </div>
                <p className="text-[#007041] text-xs">
                  Active enhancements address <strong>{faculty.activeEnhancementIds.length} proposal(s)</strong>,
                  projected to close <strong>+{delta}%</strong> of the industry alignment gap.
                </p>
              </div>
            )}

            {/* Active enhancement list */}
            {faculty.activeEnhancementIds.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-bold text-[#64748B] uppercase tracking-wide mb-2">Active Proposals</p>
                <div className="flex flex-col gap-1">
                  {faculty.activeEnhancementIds.map((id) => {
                    const enh = enhancementsFixture.find((e) => e.id === id);
                    if (!enh) return null;
                    return (
                      <div key={id} className="flex items-center gap-2 text-xs">
                        <Zap size={11} className="text-[#007041]" />
                        <span className="text-[#0F172A] font-medium">{enh.title}</span>
                        <span className="text-[#007041] font-bold ml-auto">+{enh.projectedAlignmentGain}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <Button3D
              variant="primary"
              size="md"
              onClick={() => router.push('/faculty/report')}
              className="flex-1"
            >
              <BookOpen size={16} />
              Save to Report
            </Button3D>
            <Button3D
              variant="outline"
              size="md"
              onClick={resetFacultyScenario}
            >
              <RotateCcw size={16} />
              Reset Baseline
            </Button3D>
          </div>
        </div>
      </div>
    </div>
  );
}
