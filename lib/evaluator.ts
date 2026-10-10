import { AcademicTrack, StudentAlignmentResult, TrackEvaluationResult } from '@/types';
import { coursesFixture } from './fixtures/courses';
import { rolesFixture } from './fixtures/roles';
import { skillsFixture } from './fixtures/skills';
import { resourcesFixture } from './fixtures/resources';
import { enhancementsFixture } from './fixtures/scenarios';

// ─── Deterministic Rule Evaluator ─────────────────────────────────────────────
// Pure TypeScript — no backend, no ML inference.
// All scores are computed from fixture data at runtime.
// Results tagged: "Illustrative Prototype / Mock Data" in UI.
// ─────────────────────────────────────────────────────────────────────────────

export function evaluateStudent(
  track: AcademicTrack,
  selectedCourseIds: string[],
  roleId: string | null
): StudentAlignmentResult | null {
  const role =
    rolesFixture.find((r) => r.id === roleId) ||
    rolesFixture.find((r) => r.applicableTrack === track);
  if (!role) return null;

  // 1. Gather all skills covered by the student's selected courses
  const studentCourses = coursesFixture.filter((c) => selectedCourseIds.includes(c.id));
  const coveredSkillIdSet = new Set<string>();
  studentCourses.forEach((c) => c.coveredSkillIds.forEach((sId) => coveredSkillIdSet.add(sId)));

  // 2. Identify remaining courses in the student's track (not yet selected)
  const remainingTrackCourses = coursesFixture.filter(
    (c) => c.track === track && !selectedCourseIds.includes(c.id)
  );

  // 3. Map required skills against student coverage
  const completedSkills = role.requiredSkillIds
    .filter((sId) => coveredSkillIdSet.has(sId))
    .map((sId) => skillsFixture.find((s) => s.id === sId)!)
    .filter(Boolean);

  const currentGapSkillIds = role.requiredSkillIds.filter((sId) => !coveredSkillIdSet.has(sId));

  const currentGaps = currentGapSkillIds
    .map((sId) => skillsFixture.find((s) => s.id === sId)!)
    .filter(Boolean);

  // 4. Check if uncompleted curriculum courses cover any current gaps
  const futureCurriculumCoverage: StudentAlignmentResult['futureCurriculumCoverage'] = [];
  currentGapSkillIds.forEach((sId) => {
    const upcomingCourse = remainingTrackCourses.find((c) => c.coveredSkillIds.includes(sId));
    if (upcomingCourse) {
      const skill = skillsFixture.find((s) => s.id === sId);
      if (skill) {
        futureCurriculumCoverage.push({ skill, upcomingCourse });
      }
    }
  });

  // 5. Calculate alignment percentage
  const totalRequired = role.requiredSkillIds.length;
  const overallScore =
    totalRequired > 0 ? Math.round((completedSkills.length / totalRequired) * 100) : 0;

  // 6. Build ordered S-curve roadmap nodes
  const roadmapNodes = role.recommendedOrder.map((sId, index) => {
    const skill = skillsFixture.find((s) => s.id === sId)!;
    const isCompleted = coveredSkillIdSet.has(sId);
    const futureMatch = futureCurriculumCoverage.find((f) => f.skill.id === sId);
    const resources = resourcesFixture.filter((r) => r.skillId === sId);

    // The "current" node is the first uncompleted skill
    const completedCount = role.recommendedOrder
      .slice(0, index)
      .filter((id) => coveredSkillIdSet.has(id)).length;
    const isCurrent = !isCompleted && completedCount === index;

    return {
      skill,
      status: isCompleted
        ? ('completed' as const)
        : isCurrent
          ? ('current' as const)
          : ('future_gap' as const),
      upcomingCourseTitle: futureMatch
        ? `${futureMatch.upcomingCourse.code} · ${futureMatch.upcomingCourse.title}`
        : undefined,
      resources,
    };
  });

  return {
    roleId: role.id,
    roleTitle: role.title,
    overallScore,
    completedSkills,
    currentGaps,
    futureCurriculumCoverage,
    roadmapNodes,
  };
}

export function evaluateFacultyTrack(
  track: AcademicTrack,
  activeEnhancementIds: string[]
): TrackEvaluationResult & { projectedAlignment: number } {
  const trackCourses = coursesFixture.filter((c) => c.track === track);
  const trackCoveredSkillIds = new Set<string>();
  trackCourses.forEach((c) => c.coveredSkillIds.forEach((sId) => trackCoveredSkillIds.add(sId)));

  // All relevant skills expected by industry roles for this track
  const relevantRoles = rolesFixture.filter((r) => r.applicableTrack === track);
  const allIndustrySkillIds = Array.from(
    new Set(relevantRoles.flatMap((r) => r.requiredSkillIds))
  );

  const coveredSkills = allIndustrySkillIds.filter((sId) => trackCoveredSkillIds.has(sId));
  const missingSkillIds = allIndustrySkillIds.filter((sId) => !trackCoveredSkillIds.has(sId));

  const baselineAlignment =
    allIndustrySkillIds.length > 0
      ? Math.round((coveredSkills.length / allIndustrySkillIds.length) * 100)
      : 0;

  // Prioritize gaps by industry demand
  const gapPriorities = missingSkillIds
    .map((sId) => {
      const skill = skillsFixture.find((s) => s.id === sId)!;
      const rec = enhancementsFixture.find(
        (e) => e.addedSkills.some((s) => s.id === sId)
      );
      return {
        skill,
        priorityRank: 0,
        demandPercentage: skill?.demandPercentage || 50,
        recommendedEnhancementId: rec?.id,
      };
    })
    .filter((g) => g.skill) // guard against undefined
    .sort((a, b) => b.demandPercentage - a.demandPercentage)
    .map((item, idx) => ({ ...item, priorityRank: idx + 1 }));

  // Low-demand review findings (track-scoped)
  const lowDemandSkills = skillsFixture.filter((s) => s.isLowDemand);
  const lowDemandFindings = lowDemandSkills
    .map((skill) => {
      const course = trackCourses.find((c) => c.coveredSkillIds.includes(skill.id));
      if (!course) return null;
      return {
        skill,
        associatedCourseTitle: `${course.code}: ${course.title}`,
        reviewNote:
          skill.lowDemandRationale || 'Observed low market requirement across recent job postings.',
      };
    })
    .filter(Boolean) as TrackEvaluationResult['lowDemandFindings'];

  // Calculate projected gain from active additive enhancements
  const activeEnhancements = enhancementsFixture.filter((e) =>
    activeEnhancementIds.includes(e.id)
  );
  const additionalSkillIds = new Set(
    activeEnhancements.flatMap((e) => e.addedSkills.map((s) => s.id))
  );
  // Only count skills that are actually missing (not already covered)
  const newlyAddedCount = Array.from(additionalSkillIds).filter(
    (sId) => !trackCoveredSkillIds.has(sId) && allIndustrySkillIds.includes(sId)
  ).length;

  const projectedCoveredCount = Math.min(
    allIndustrySkillIds.length,
    coveredSkills.length + newlyAddedCount
  );
  const projectedAlignment =
    allIndustrySkillIds.length > 0
      ? Math.round((projectedCoveredCount / allIndustrySkillIds.length) * 100)
      : 0;

  return {
    track,
    trackTitle: track.replace(/_/g, ' '),
    baselineAlignment,
    projectedAlignment,
    totalTrackSkills: allIndustrySkillIds.length,
    coveredSkillsCount: coveredSkills.length,
    missingSkillsCount: missingSkillIds.length,
    gapPriorities,
    lowDemandFindings,
  };
}
