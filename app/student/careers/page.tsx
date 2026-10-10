'use client';

import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronRight, ArrowLeft, TrendingUp, Lock, CheckCircle2 } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { rolesFixture } from '@/lib/fixtures/roles';
import { evaluateStudent } from '@/lib/evaluator';
import Button3D from '@/components/ui/button-3d';
import { cn } from '@/lib/utils';

export default function StudentCareersPage() {
  const router = useRouter();
  const { student, setStudentRole } = useTechGapStore();

  const trackRoles = rolesFixture.filter((r) => r.applicableTrack === student.track);

  // Compute live alignment preview for each role
  const roleEvals = useMemo(() => {
    return trackRoles.map((role) => {
      const result = evaluateStudent(student.track, student.selectedCourseIds, role.id);
      return { role, score: result?.overallScore ?? 0 };
    }).sort((a, b) => b.score - a.score);
  }, [student.track, student.selectedCourseIds]);

  const handleSelect = (roleId: string) => {
    setStudentRole(roleId);
    router.push('/student/roadmap');
  };

  const demandLabel = (score: number) => {
    if (score >= 75) return { label: 'High Demand', color: 'badge-green' };
    if (score >= 55) return { label: 'Moderate Demand', color: 'badge-blue' };
    return { label: 'Growing Niche', color: 'badge-amber' };
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-extrabold text-[#0F172A] mb-1">Career Target Selection</h1>
        <p className="text-[#64748B]">
          Roles are ranked by your live alignment score based on courses selected.
          Select one to lock your career target and view your personalized roadmap.
        </p>
      </div>

      {student.selectedCourseIds.length === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 text-sm text-amber-800">
          ⚠️ No courses selected yet. <button onClick={() => router.push('/student/setup')} className="font-semibold underline">Go back to setup</button> to select your completed courses.
        </div>
      )}

      <div className="flex flex-col gap-4 mb-8">
        {roleEvals.map(({ role, score }, idx) => {
          const isSelected = student.selectedRoleId === role.id;
          const demand = demandLabel(score);
          const topSkills = role.requiredSkillIds.slice(0, 4);

          return (
            <button
              key={role.id}
              id={`career-${role.id}`}
              onClick={() => handleSelect(role.id)}
              className={cn(
                'text-left p-5 rounded-2xl border-2 transition-all duration-200 relative overflow-hidden group',
                isSelected
                  ? 'border-[#007041] bg-[#F0FDF4] shadow-md'
                  : 'border-[#E2E8F0] bg-white hover:border-[#007041]/40 hover:shadow-sm'
              )}
            >
              {/* Rank badge */}
              <div className="absolute top-4 right-4">
                {isSelected && (
                  <CheckCircle2 size={22} className="text-[#007041]" />
                )}
              </div>

              <div className="flex items-start gap-4">
                {/* Rank number */}
                <div className={cn(
                  'w-9 h-9 rounded-xl flex items-center justify-center text-sm font-extrabold shrink-0',
                  idx === 0 ? 'bg-[#007041] text-white' : 'bg-slate-100 text-slate-500'
                )}>
                  #{idx + 1}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className="font-bold text-[#0F172A] text-base">{role.title}</h3>
                    <span className={demand.color}>{demand.label}</span>
                  </div>
                  <p className="text-[#64748B] text-sm leading-relaxed mb-3">{role.description}</p>

                  {/* Key skills */}
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {topSkills.map((sId) => (
                      <span key={sId} className="badge-slate text-xs">{sId.replace('skill-', '').replace(/-/g, ' ')}</span>
                    ))}
                    {role.requiredSkillIds.length > 4 && (
                      <span className="badge-slate text-xs">+{role.requiredSkillIds.length - 4} more</span>
                    )}
                  </div>

                  {/* Live alignment bar */}
                  <div className="flex items-center gap-3">
                    <div className="flex-1 progress-track">
                      <div className="progress-fill" style={{ width: `${score}%` }} />
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <TrendingUp size={14} className="text-[#007041]" />
                      <span className="font-extrabold text-[#007041] text-sm">{score}%</span>
                      <span className="text-[#64748B] text-xs">alignment</span>
                    </div>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <Button3D variant="ghost" size="md" onClick={() => router.push('/student/setup')}>
          <ArrowLeft size={18} />
          Back to Setup
        </Button3D>

        <Button3D
          variant="primary"
          size="lg"
          onClick={() => {
            if (!student.selectedRoleId && roleEvals.length > 0) {
              setStudentRole(roleEvals[0].role.id);
            }
            router.push('/student/roadmap');
          }}
          disabled={student.selectedCourseIds.length === 0}
        >
          {student.selectedRoleId ? 'Lock Target & View Roadmap' : 'Use Top Match & View Roadmap'}
          <ChevronRight size={20} />
        </Button3D>
      </div>

      {roleEvals.length === 0 && (
        <div className="text-center text-[#64748B] py-12">
          <Lock size={40} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No roles available for this track.</p>
          <button onClick={() => router.push('/student/setup')} className="text-[#007041] text-sm underline mt-1">
            Change your track
          </button>
        </div>
      )}
    </div>
  );
}
