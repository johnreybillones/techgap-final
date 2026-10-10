import { AdditiveEnhancement } from '@/types';
import { skillsFixture } from './skills';

// ─── Additive Enhancement Scenarios Fixture ───────────────────────────────────
// Pre-configured additive-only curriculum proposals for the simulation sandbox.
// CONSTRAINT: Purely additive. No reduction, removal, or unit reassignment.
// ─────────────────────────────────────────────────────────────────────────────

const getSkill = (id: string) => {
  const skill = skillsFixture.find((s) => s.id === id);
  if (!skill) throw new Error(`Skill not found: ${id}`);
  return skill;
};

export const enhancementsFixture: AdditiveEnhancement[] = [
  // ── Web Development Track Enhancements ────────────────────────────────────
  {
    id: 'enh-wd-docker-lab',
    title: 'Embed Docker & Containerization into Web Systems Lab',
    targetCourseId: 'ITWB313-LAB',
    targetCourseTitle: 'S-ITWB313LA: Web Systems and Technologies Laboratory',
    addedSkills: [getSkill('skill-docker')],
    rationale:
      'Docker appears in 64% of WD job postings (Q3 2026). Embedding a 3-week hands-on containerization module into the existing lab prevents the need for a new standalone course while directly bridging this top-5 gap.',
    projectedAlignmentGain: 8.0,
  },
  {
    id: 'enh-wd-nextjs',
    title: 'Introduce Next.js & Server Components to Advanced Web Dev',
    targetCourseId: 'ITWB312-LEC',
    targetCourseTitle: 'S-ITWB312: Advanced Web Development (Lecture)',
    addedSkills: [getSkill('skill-nextjs'), getSkill('skill-typescript')],
    rationale:
      'Next.js (61%) and TypeScript (78%) are consistently required by employers for mid-level WD roles. A 4-week module on the App Router and type safety directly extends the existing React curriculum without replacing any units.',
    projectedAlignmentGain: 12.0,
  },
  {
    id: 'enh-wd-unit-testing',
    title: 'Add Unit Testing Module to Full Stack Lab',
    targetCourseId: 'ITWB411-LAB',
    targetCourseTitle: 'S-ITWB411LA: Full Stack Web Application Development Laboratory',
    addedSkills: [getSkill('skill-unit-testing')],
    rationale:
      'Professional QA/testing literacy (58% demand) is underrepresented in the current lab structure. Adding Jest/Vitest exercises into existing assessments costs zero new credit hours.',
    projectedAlignmentGain: 5.5,
  },

  // ── Network Technology Track Enhancements ─────────────────────────────────
  {
    id: 'enh-nt-devops-ci',
    title: 'Integrate CI/CD Pipeline Labs into DevOps Course',
    targetCourseId: 'ITNT412-LAB',
    targetCourseTitle: 'S-ITNT412LA: DevOps and Network Automation Laboratory',
    addedSkills: [getSkill('skill-devops-ci'), getSkill('skill-scripting-python')],
    rationale:
      'DevOps (72%) and Python automation (67%) are both in the top demand gap for NT graduates. Extending the existing lab with GitHub Actions and Ansible playbooks maps directly to the course\'s stated automation outcomes.',
    projectedAlignmentGain: 10.0,
  },
  {
    id: 'enh-nt-cloud-practical',
    title: 'Add AWS Practitioner Track to Cloud Infra Lab',
    targetCourseId: 'ITNT411-LAB',
    targetCourseTitle: 'S-ITNT411LA: Cloud Infrastructure and Virtualization Laboratory',
    addedSkills: [getSkill('skill-cloud-infra')],
    rationale:
      'Cloud infrastructure skills (78% demand) are already partially addressed conceptually; practical AWS sandbox labs in the existing course significantly elevate employability without adding credit hours.',
    projectedAlignmentGain: 7.0,
  },

  // ── Intelligent Systems Track Enhancements ────────────────────────────────
  {
    id: 'enh-is-mlops',
    title: 'Add MLOps Deployment Track to AI Deployment Course',
    targetCourseId: 'CSIS412',
    targetCourseTitle: 'S-CSIS412: MLOps and AI System Deployment',
    addedSkills: [getSkill('skill-ml-ops'), getSkill('skill-cloud-ml')],
    rationale:
      'MLOps (68%) and cloud ML platforms (59%) are critical for IS graduates seeking production ML roles. Expanding the existing deployment course with Dockerized model serving and SageMaker labs directly addresses these gaps.',
    projectedAlignmentGain: 11.0,
  },
  {
    id: 'enh-is-sql-analytics',
    title: 'Embed SQL Analytics Module into Data Science Course',
    targetCourseId: 'CSIS-DATA',
    targetCourseTitle: 'S-CSIS214: Data Science and Analytics',
    addedSkills: [getSkill('skill-sql-analytics')],
    rationale:
      'SQL for analytics (73% demand) is a foundational skill for data roles that complements the existing pandas/Python curriculum. A dedicated 2-week SQL window functions module closes this gap efficiently.',
    projectedAlignmentGain: 6.5,
  },

  // ── Game Development Track Enhancements ───────────────────────────────────
  {
    id: 'enh-gd-unreal',
    title: 'Introduce Unreal Engine Module to Advanced Game Programming',
    targetCourseId: 'CSGD411-LEC',
    targetCourseTitle: 'S-CSGD411: Advanced Game Programming (Lecture)',
    addedSkills: [getSkill('skill-unreal')],
    rationale:
      'Unreal Engine (54% demand) is increasingly required for AAA studio internships. A 4-week Unreal Blueprint module within the existing advanced course expands graduate portfolio options without replacing the Unity curriculum.',
    projectedAlignmentGain: 8.0,
  },
  {
    id: 'enh-gd-multiplayer',
    title: 'Add Multiplayer Networking Module to Game Dev 2 Lab',
    targetCourseId: 'CSGD312-LAB',
    targetCourseTitle: 'S-CSGD312LA: Game Design and Development 2 Laboratory',
    addedSkills: [getSkill('skill-multiplayer-net')],
    rationale:
      'Multiplayer networking (49% demand) is a sought-after specialization for indie and mobile studios. Embedding Photon SDK basics into the existing lab extends student projects with real networked gameplay.',
    projectedAlignmentGain: 6.0,
  },
];
