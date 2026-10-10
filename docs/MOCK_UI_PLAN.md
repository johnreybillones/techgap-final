# TechGap Mock UI Implementation Plan

**Status:** Approved for execution  
**Date:** 2026-10-10  
**Authority:** Derived from [MOCK_UI_HANDOFF.md](file:///c:/Users/Alfierey/Downloads/JR/Programming/VSCode/techgap-final/techgap-final/docs/handoff/MOCK_UI_HANDOFF.md) and design alignment decisions.  
**Guiding Principles:** `/ponytail` (simplest working implementation, native stdlib/CSS first, zero fluff), `/frontend-design` & `/impeccable` (high aesthetic polish, tactile feedback, anti-AI slop), and `/ui-ux-pro-max` (EdTech UX best practices).

---

## 1. Executive Summary & Design System

### 1.1 Aesthetic & Inspo Direction
* **Style:** **Duolingo-inspired Hybrid EdTech**.
  * **Student Journey:** Playful, gamified UI featuring an interactive **S-Curve winding milestone path** (`START`, completed checkmark, current in-progress pulse/glow, and locked/gap nodes), chunky 3D push-buttons, and slide-out skill inspection sheets with real curated learning links.
  * **Faculty / Administrator Journey:** Clean, polished, data-dense modern dashboard sharing the same tactile button tokens, institutional typography, and crisp borders.
* **Color Palette (DLSU-D Anchored):**
  * `primary-green`: `#007041` (DLSU-D Lasallian Forest Green)
  * `primary-green-shadow`: `#00502E` (3D bottom border on push-buttons)
  * `primary-green-tint`: `#F0FDF4` (Light emerald background tint)
  * `accent-blue`: `#0284C7` (Sky / Royal Blue for tech tags & curriculum outcomes)
  * `accent-amber`: `#D97706` / `#F59E0B` (Amber / Gold for gaps, low-demand warnings, and notifications)
  * `surface-bg`: `#F8FAFC` (Slate 50 off-white canvas)
  * `card-bg`: `#FFFFFF` with `border: 2px solid #E2E8F0`
  * `text-main`: `#0F172A` (Slate 900)
  * `text-muted`: `#64748B` (Slate 500)
* **Typography:** **Plus Jakarta Sans** (via `next/font/google`), balancing rounded, friendly headings with crisp tabular metrics.
* **Tactile 3D Button Utility (CSS / Tailwind):**
  * Base: `rounded-xl font-bold transition-all duration-150`
  * Default state: `bg-[#007041] text-white border-b-4 border-[#00502E]`
  * Pressed state: `active:translate-y-1 active:border-b-0`
  * Hover state: `hover:brightness-105`
* **Anti-AI Slop Rules:**
  * ❌ No generic dark-mode purple/indigo-to-cyan neon gradients.
  * ❌ No blurry, low-contrast glassmorphic panels or illegible floating cards.
  * ❌ No boilerplate lorem ipsum or uncalibrated stock numbers.
  * ❌ No fake AI chatbot widgets or hallucinated model outputs.
  * ✅ Explicit "Illustrative Mock Data / Educational Demo" badges on all metrics.
  * ✅ High contrast, accessible WCAG AA color pairings, and visible focus rings.

---

## 2. Technical Stack & Dependencies

```json
{
  "name": "techgap-mock-ui",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "clsx": "^2.1.1",
    "lucide-react": "^0.475.0",
    "next": "^14.2.23",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "tailwind-merge": "^2.6.0",
    "zustand": "^4.5.5"
  },
  "devDependencies": {
    "@types/node": "^20.17.19",
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.5.2",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.7.3"
  }
}
```

> **Ponytail Architecture Note:**
> * Zero heavy animation libraries (CSS keyframes & native Tailwind transitions only).
> * Zero external PDF generation libraries (native browser `@media print` + `window.print()` only).
> * Zero external database or backend calls (in-memory fixtures + Zustand `persist` with `localStorage` fallback).

---

## 3. Directory & File Structure

```text
mock-ui/
├── app/
│   ├── layout.tsx                     # Root layout with Plus Jakarta Sans & Navbar
│   ├── globals.css                    # Tailwind directives, 3D button classes, print styles
│   ├── page.tsx                       # Shared Entry & Role Restoration screen
│   ├── student/
│   │   ├── layout.tsx                 # Student header with back-navigation & reset controls
│   │   ├── setup/page.tsx             # S1: Academic Context & Completed Courses Wizard
│   │   ├── careers/page.tsx           # S2: Career Role Ranking & Comparison
│   │   └── roadmap/page.tsx           # S3-S5: Duolingo S-Curve Winding Roadmap & Inspection Sheet
│   └── faculty/
│       ├── layout.tsx                 # Faculty navigation shell (Dashboard, Simulate, Report, Upload)
│       ├── page.tsx                   # A1-A4: Track Overview, Coverage Evidence, Gap Priorities
│       ├── simulate/page.tsx          # A5: Interactive Additive Scenario Sandbox (Split-view)
│       ├── report/page.tsx            # A6: Consolidated Academic Review Report (@media print)
│       └── upload-preview/page.tsx    # Section 6: Planned Syllabus Upload Extension Preview
├── components/
│   ├── ui/
│   │   ├── button-3d.tsx              # Chunky tactile 3D push-button component
│   │   ├── badge.tsx                  # Status pill (Completed, Gap, Future, Low-Demand)
│   │   ├── card.tsx                   # 2px bordered card with clean header/body
│   │   ├── modal.tsx                  # Accessible overlay dialog
│   │   └── disclaimer-banner.tsx      # Illustrative data & non-production disclaimer
│   ├── student/
│   │   ├── winding-path.tsx           # S-curve SVG/flex serpentine milestone layout
│   │   ├── milestone-node.tsx         # Circular 3D push-node with icons & status badges
│   │   ├── skill-drawer.tsx           # Slide-out sheet with skill details & curated URLs
│   │   └── alignment-card.tsx         # Sticky alignment score & gap counter card
│   └── faculty/
│       ├── track-selector.tsx         # Dropdown/pill selector across all 4 tracks
│       ├── gap-priority-table.tsx     # Demand-ordered competency gaps table
│       ├── low-demand-list.tsx        # Low-demand review findings cards
│       ├── scenario-sandbox.tsx       # Additive enhancement toggle list + delta preview
│       └── syllabus-dropzone.tsx      # Mock file drag-and-drop parse preview
├── lib/
│   ├── store.ts                       # Zustand store with `persist` middleware (techgap_mock_v1)
│   ├── evaluator.ts                   # Pure deterministic rule evaluator for scores & gaps
│   ├── utils.ts                       # `cn()` helper (clsx + tailwind-merge)
│   └── fixtures/
│       ├── tracks.ts                  # All 4 tracks from CSVs (BSCS IS/GD, BSIT NT/WD)
│       ├── courses.ts                 # Full course catalog with lecture/lab separation
│       ├── roles.ts                   # Sample industry roles with required competencies
│       ├── skills.ts                  # Competencies, demand metrics & rationales
│       ├── resources.ts               # Verified upskilling resource links (Coursera, FCC, MDN)
│       └── scenarios.ts               # Pre-configured additive curriculum enhancement options
└── types/
    └── index.ts                       # Complete TypeScript contracts & fixture schemas
```

---

## 4. Concrete Data Contracts (`types/index.ts`)

```typescript
export type AcademicProgram = 'BSCS' | 'BSIT';

export type AcademicTrack = 
  | 'BSCS_INTELLIGENT_SYSTEMS'
  | 'BSCS_GAME_DEVELOPMENT'
  | 'BSIT_NETWORK_TECHNOLOGY'
  | 'BSIT_WEB_DEVELOPMENT';

export type YearLevel = '1st Year' | '2nd Year' | '3rd Year' | '4th Year';

export type CourseComponent = 'LEC' | 'LAB' | 'COMBINED';

export interface Course {
  id: string; // Distinct key, e.g. "ITWB311-LAB" to prevent CSV code collisions
  code: string;
  title: string;
  component: CourseComponent;
  track: AcademicTrack;
  yearLevel: YearLevel;
  semester: '1st Sem' | '2nd Sem';
  units: number;
  isCore: boolean; // true if common/core computing course
  coveredSkillIds: string[];
}

export interface Skill {
  id: string;
  name: string;
  category: 'Core Computing' | 'Specialization' | 'Tool/Framework' | 'Professional';
  demandPercentage: number; // e.g., 78 (%)
  demandSampleCount: string; // e.g., "142 / 182 postings (Q3 2026 snapshot)"
  isLowDemand?: boolean;
  lowDemandRationale?: string;
}

export interface LearningResource {
  skillId: string;
  title: string;
  provider: 'freeCodeCamp' | 'MDN Web Docs' | 'Coursera' | 'Official Docs' | 'Kaggle';
  url: string;
  estimatedHours: number;
  type: 'Interactive' | 'Documentation' | 'Video Course';
}

export interface CareerRole {
  id: string;
  title: string;
  applicableTrack: AcademicTrack;
  description: string;
  requiredSkillIds: string[];
  recommendedOrder: string[]; // Ordered skill IDs for the S-curve roadmap
}

export interface StudentAlignmentResult {
  roleId: string;
  roleTitle: string;
  overallScore: number; // 0 to 100%
  completedSkills: Skill[];
  currentGaps: Skill[];
  futureCurriculumCoverage: {
    skill: Skill;
    upcomingCourse: Course;
  }[];
  roadmapNodes: {
    skill: Skill;
    status: 'completed' | 'current' | 'future_gap';
    upcomingCourseTitle?: string;
    resources: LearningResource[];
  }[];
}

export interface AdditiveEnhancement {
  id: string;
  title: string;
  targetCourseId: string;
  targetCourseTitle: string;
  addedSkills: Skill[];
  rationale: string;
  projectedAlignmentGain: number; // e.g., +8.5%
}

export interface TrackEvaluationResult {
  track: AcademicTrack;
  trackTitle: string;
  baselineAlignment: number; // e.g., 68.2%
  totalTrackSkills: number;
  coveredSkillsCount: number;
  missingSkillsCount: number;
  gapPriorities: {
    skill: Skill;
    priorityRank: number;
    demandPercentage: number;
    recommendedEnhancementId?: string;
  }[];
  lowDemandFindings: {
    skill: Skill;
    associatedCourseTitle: string;
    reviewNote: string;
  }[];
}
```

---

## 5. Mock State Store (`lib/store.ts`)

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AcademicProgram, AcademicTrack, YearLevel } from '@/types';

interface StudentState {
  program: AcademicProgram;
  track: AcademicTrack;
  yearLevel: YearLevel;
  selectedCourseIds: string[];
  selectedRoleId: string | null;
}

interface FacultyState {
  selectedTrack: AcademicTrack;
  activeEnhancementIds: string[]; // IDs of toggled additive scenarios
}

interface TechGapStore {
  activeRole: 'student' | 'faculty' | null;
  student: StudentState;
  faculty: FacultyState;
  
  // Actions
  setActiveRole: (role: 'student' | 'faculty' | null) => void;
  setStudentAcademicContext: (program: AcademicProgram, track: AcademicTrack, year: YearLevel) => void;
  toggleStudentCourse: (courseId: string) => void;
  selectAllEligibleCourses: (courseIds: string[]) => void;
  clearStudentCourses: () => void;
  setStudentRole: (roleId: string) => void;
  
  setFacultyTrack: (track: AcademicTrack) => void;
  toggleEnhancement: (enhancementId: string) => void;
  resetFacultyScenario: () => void;
  
  resetAll: () => void;
}

export const useTechGapStore = create<TechGapStore>()(
  persist(
    (set) => ({
      activeRole: null,
      student: {
        program: 'BSIT',
        track: 'BSIT_WEB_DEVELOPMENT',
        yearLevel: '3rd Year',
        selectedCourseIds: [
          'ITWB311-LEC',
          'ITWB311-LAB',
          'ITCC101',
          'ITCC102',
          'ITCC103'
        ],
        selectedRoleId: 'role-fullstack-dev',
      },
      faculty: {
        selectedTrack: 'BSIT_WEB_DEVELOPMENT',
        activeEnhancementIds: [],
      },

      setActiveRole: (role) => set({ activeRole: role }),
      setStudentAcademicContext: (program, track, yearLevel) =>
        set((state) => ({
          student: {
            ...state.student,
            program,
            track,
            yearLevel,
            // Clear courses if switching to an incompatible track
            selectedCourseIds: state.student.track === track ? state.student.selectedCourseIds : [],
            selectedRoleId: null,
          },
        })),
      toggleStudentCourse: (courseId) =>
        set((state) => ({
          student: {
            ...state.student,
            selectedCourseIds: state.student.selectedCourseIds.includes(courseId)
              ? state.student.selectedCourseIds.filter((id) => id !== courseId)
              : [...state.student.selectedCourseIds, courseId],
          },
        })),
      selectAllEligibleCourses: (courseIds) =>
        set((state) => ({
          student: { ...state.student, selectedCourseIds: courseIds },
        })),
      clearStudentCourses: () =>
        set((state) => ({
          student: { ...state.student, selectedCourseIds: [] },
        })),
      setStudentRole: (roleId) =>
        set((state) => ({
          student: { ...state.student, selectedRoleId: roleId },
        })),

      setFacultyTrack: (track) =>
        set((state) => ({
          faculty: {
            selectedTrack: track,
            activeEnhancementIds: [], // Reset scenario when switching tracks
          },
        })),
      toggleEnhancement: (enhancementId) =>
        set((state) => ({
          faculty: {
            ...state.faculty,
            activeEnhancementIds: state.faculty.activeEnhancementIds.includes(enhancementId)
              ? state.faculty.activeEnhancementIds.filter((id) => id !== enhancementId)
              : [...state.faculty.activeEnhancementIds, enhancementId],
          },
        })),
      resetFacultyScenario: () =>
        set((state) => ({
          faculty: { ...state.faculty, activeEnhancementIds: [] },
        })),

      resetAll: () =>
        set({
          activeRole: null,
          student: {
            program: 'BSIT',
            track: 'BSIT_WEB_DEVELOPMENT',
            yearLevel: '3rd Year',
            selectedCourseIds: [],
            selectedRoleId: null,
          },
          faculty: {
            selectedTrack: 'BSIT_WEB_DEVELOPMENT',
            activeEnhancementIds: [],
          },
        }),
    }),
    {
      name: 'techgap_mock_v1',
    }
  )
);
```

---

## 6. Deterministic Rule Evaluator (`lib/evaluator.ts`)

This pure TypeScript utility provides real-time, non-contradictory results without requiring any real backend or ML pipeline:

```typescript
import { 
  AcademicTrack, 
  StudentAlignmentResult, 
  TrackEvaluationResult 
} from '@/types';
import { coursesFixture } from './fixtures/courses';
import { rolesFixture } from './fixtures/roles';
import { skillsFixture } from './fixtures/skills';
import { resourcesFixture } from './fixtures/resources';
import { enhancementsFixture } from './fixtures/scenarios';

export function evaluateStudent(
  track: AcademicTrack,
  selectedCourseIds: string[],
  roleId: string | null
): StudentAlignmentResult | null {
  const role = rolesFixture.find((r) => r.id === roleId) || rolesFixture.find((r) => r.applicableTrack === track);
  if (!role) return null;

  // 1. Gather all skills covered by the student's selected courses
  const studentCourses = coursesFixture.filter((c) => selectedCourseIds.includes(c.id));
  const coveredSkillIdSet = new Set<string>();
  studentCourses.forEach((c) => c.coveredSkillIds.forEach((sId) => coveredSkillIdSet.add(sId)));

  // 2. Identify remaining courses in the student's track that are not yet selected
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

  // 4. Check if uncompleted curriculum courses cover any of the current gaps
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
  const overallScore = totalRequired > 0 
    ? Math.round((completedSkills.length / totalRequired) * 100) 
    : 0;

  // 6. Build the ordered S-curve roadmap nodes
  const roadmapNodes = role.recommendedOrder.map((sId, index) => {
    const skill = skillsFixture.find((s) => s.id === sId)!;
    const isCompleted = coveredSkillIdSet.has(sId);
    const futureMatch = futureCurriculumCoverage.find((f) => f.skill.id === sId);
    const resources = resourcesFixture.filter((r) => r.skillId === sId);

    return {
      skill,
      status: isCompleted 
        ? ('completed' as const) 
        : index === completedSkills.length 
          ? ('current' as const) 
          : ('future_gap' as const),
      upcomingCourseTitle: futureMatch ? `${futureMatch.upcomingCourse.code} (${futureMatch.upcomingCourse.title})` : undefined,
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

  const baselineAlignment = Math.round((coveredSkills.length / allIndustrySkillIds.length) * 100);

  // Prioritize gaps based on industry demand
  const gapPriorities = missingSkillIds
    .map((sId) => {
      const skill = skillsFixture.find((s) => s.id === sId)!;
      const rec = enhancementsFixture.find(
        (e) => e.targetCourseId && e.addedSkills.some((s) => s.id === sId)
      );
      return {
        skill,
        priorityRank: 0,
        demandPercentage: skill?.demandPercentage || 50,
        recommendedEnhancementId: rec?.id,
      };
    })
    .sort((a, b) => b.demandPercentage - a.demandPercentage)
    .map((item, idx) => ({ ...item, priorityRank: idx + 1 }));

  // Low demand review findings
  const lowDemandSkills = skillsFixture.filter((s) => s.isLowDemand);
  const lowDemandFindings = lowDemandSkills.map((skill) => {
    const course = trackCourses.find((c) => c.coveredSkillIds.includes(skill.id));
    return {
      skill,
      associatedCourseTitle: course ? `${course.code}: ${course.title}` : 'Curriculum Elective',
      reviewNote: skill.lowDemandRationale || 'Observed low market requirement across recent job postings.',
    };
  });

  // Calculate projected gain from active additive enhancements
  const activeEnhancements = enhancementsFixture.filter((e) =>
    activeEnhancementIds.includes(e.id)
  );
  const additionalSkillCount = new Set(
    activeEnhancements.flatMap((e) => e.addedSkills.map((s) => s.id))
  ).size;

  const projectedCoveredCount = Math.min(
    allIndustrySkillIds.length,
    coveredSkills.length + additionalSkillCount
  );
  const projectedAlignment = Math.round(
    (projectedCoveredCount / allIndustrySkillIds.length) * 100
  );

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
```

---

## 7. Screen-by-Screen Implementation Specifications

### Screen 1: Shared Entry & Role Restoration (`/`)
* **URL:** `/`
* **Components:**
  * Header with DLSU-D TechGap logo (`#007041` primary brand badge)
  * Prominent **Illustrative Prototype Disclaimer** (amber callout: sample data only, no live DB/scraping).
  * **Role Selection Cards (Duolingo 3D style):**
    * **Student Experience Card:** "Explore career alignment, map your completed courses, and unlock your upskilling journey."
      * If prior student state exists: Displays "Resume [Year Level] [Track] ($\rightarrow$ `X` courses selected)" + "Start Fresh" link.
      * Action: Chunky 3D Green Button (`Start Student Journey` / `Continue`).
    * **Faculty / Admin Experience Card:** "Review curriculum alignment, prioritize industry gaps, simulate additive revisions, and generate official reports."
      * Action: Chunky 3D Outline Button (`Enter Academic Dashboard`).
  * **Global Reset Action:** Inconspicuous link at the footer to flush `localStorage` (`techgap_mock_v1`).

---

### Screen 2: Student Setup Wizard (`/student/setup`)
* **URL:** `/student/setup`
* **Workflow:**
  1. **Academic Context Selectors:** Program (`BSCS` | `BSIT`), Specialization Track (all 4 tracks), Year Level (`1st Year` to `4th Year`).
  2. **Course Selection Grid:**
     * Filterable by tabs: `All Eligible`, `Core Computing`, `Track Specialization`.
     * Distinguishes Lecture vs. Lab components (`ITWB311-LEC` vs. `ITWB311-LAB`) to prevent CSV code collisions.
     * Clickable card tokens with checkbox states (`border-2 border-[#007041] bg-[#F0FDF4]` when active).
  3. **Batch Actions:** "Select All Completed", "Clear Selection".
  4. **Validation Guardrail:** Empty course selection displays an instructional notice ("Select at least one completed course to compute your evidence path") and disables the proceed button.
  5. **Next Step:** 3D Button `Proceed to Career Selection` $\rightarrow$ routes to `/student/careers`.

---

### Screen 3: Student Career Target Selection (`/student/careers`)
* **URL:** `/student/careers`
* **Workflow:**
  1. Displays ranked demo career roles matching the selected track (e.g. *Full Stack Developer*, *Frontend Engineer*, *Cloud Systems Specialist*).
  2. Each card shows:
     * Role Title & Job Market Demand Badge.
     * Real-time match preview based on selected courses (e.g., `65% Alignment`).
     * Primary required competencies pills.
  3. Radio-button style selection with a prominent 3D Button: `Lock Career Target & View Roadmap` $\rightarrow$ routes to `/student/roadmap`.

---

### Screen 4: Student Duolingo S-Curve Winding Roadmap (`/student/roadmap`)
* **URL:** `/student/roadmap`
* **Visual Presentation:**
  * **Split Layout:**
    * **Left/Center (Main Stage):** Serpentine S-Curve milestone path (`winding-path.tsx`).
      * Circular 3D push-nodes (`size-16` to `size-20`) staggered left, center, right in a winding wave connected by dashed vertical SVG pathways.
      * **Node 0 (Start Banner):** `START YOUR JOURNEY`.
      * **Completed Nodes:** Green with white checkmark badge (`bg-[#007041] border-b-4 border-[#00502E]`).
      * **Current Up-Next Node:** Vibrant Sky Blue with glowing radar pulse ring (`bg-[#0284C7] ring-4 ring-sky-300 animate-pulse`).
      * **Locked / Future Gap Nodes:** Slate gray / Amber lock icon (`bg-slate-200 border-b-4 border-slate-300 text-slate-500`).
      * **Course Overlap Tag:** If a future gap has an uncompleted curriculum course that covers it, shows a neat pill: *"Covered in 4th Year: ITWB412"*.
    * **Right Sticky Rail (Summary Widget):**
      * Overall Role Alignment Score Circle (e.g., `72%`).
      * Current Completed Competencies count.
      * Unaddressed Gap count.
      * "Change Target Career" & "Edit Course Selections" quick links.
  * **Interaction:** Clicking any milestone node slides open the **Skill Inspection Drawer** (`skill-drawer.tsx`):
    * Skill title, description, and market demand rate.
    * Academic Evidence: "Covered by: ITWB311 Web Development" OR "Identified Gap (Not yet completed)".
    * Curated External Upskilling Resources: Direct links to freeCodeCamp, MDN, Coursera, or documentation with estimated completion hours.

---

### Screen 5: Faculty Track Dashboard (`/faculty`)
* **URL:** `/faculty`
* **Components:**
  1. **Track Switcher Bar:** Pills to toggle between all 4 tracks (`BSCS IS`, `BSCS GD`, `BSIT NT`, `BSIT WD`).
  2. **High-Level Alignment Banner:**
     * Baseline Track Alignment KPI Card (`68% Industry Coverage`).
     * Snapshot Metadata Pill: `Source Window: Q3 2026 Sample Job Snapshot (N=182)`.
  3. **Industry Gap Priority Table:**
     * Competencies ranked by market demand percentage.
     * Current status (`Missing in Track` vs `Partially Addressed`).
     * "Simulate Addition" quick-action button connecting directly to the simulation sandbox.
  4. **Low-Demand Review Section:**
     * Cards highlighting topics identified for academic review (e.g., legacy scripting libraries).
     * Clear disclaimer: *"Review Finding only: Not designated as obsolete or recommended for unilateral removal."*

---

### Screen 6: Faculty Interactive Scenario Sandbox (`/faculty/simulate`)
* **URL:** `/faculty/simulate`
* **Layout:** Split-View Sandbox:
  * **Left Column (Additive Enhancement Catalog):**
    * Toggles for pre-configured additive proposals (e.g., `Embed Docker & Containerization into Web Systems Lab`, `Introduce Next.js & Server Components to Advanced Web Dev`).
    * Each card details: Target Course, Added Competencies, Academic Rationale.
    * Constraint Rule: Purely additive (no remove/replace/delete unit reduction allowed).
  * **Right Column (Real-Time Impact Comparison Card):**
    * Side-by-side KPI comparison:
      * **Baseline Alignment:** `68.2%`
      * **Projected Alignment:** `76.7% (+8.5%)`
      * **Remaining Gaps:** `8` $\rightarrow$ `6 (-2)`
    * Visual delta progress bar.
    * Action Buttons: `Save Scenario to Report`, `Reset to Baseline`.

---

### Screen 7: Consolidated Academic Review Report (`/faculty/report`)
* **URL:** `/faculty/report`
* **Presentation & Print Optimizations:**
  * Clean, institutional white document format with DLSU-D letterhead styling.
  * Native CSS `@media print` rules:
    ```css
    @media print {
      nav, footer, .no-print { display: none !important; }
      body { background: white !important; font-size: 11pt; }
      .print-card { border: 1px solid #ccc !important; box-shadow: none !important; }
      .page-break { page-break-before: always; }
    }
    ```
  * **Report Contents:**
    1. Executive Summary & Evidence Snapshot metadata.
    2. Track Baseline Competency Coverage Breakdown.
    3. Prioritized Industry Gaps & Demand Evidence.
    4. Low-Demand Academic Review Topics.
    5. Hypothetical Scenario Section (explicitly labeled *"Hypothetical Revision Scenario — Non-Official"* if enhancements are active).
    6. Sign-off block for Department Curriculum Committee review.
  * **Action Bar:** "Print / Save to PDF" button triggering `window.print()`.

---

### Screen 8: Future Syllabus Upload Extension Preview (`/faculty/upload-preview`)
* **URL:** `/faculty/upload-preview`
* **Presentation:**
  * Header Banner: *"Planned Faculty Syllabus Extension — Future Feature Preview"*.
  * **Interactive Dropzone:**
    * Drag-and-drop area accepting `.pdf` syllabi.
    * Pre-loaded with workspace sample button: `Load Sample: S-ITWB311LA Web Development Lab.pdf`.
  * **Simulated Extraction Pipeline:**
    * File progress bar mimicking multi-stage Python parsing (Extracting text $\rightarrow$ Detecting outcomes $\rightarrow$ Mapping competencies).
    * Extracted Metadata Cards: Course Code, Course Title, Extracted Outcomes count, Source Page references.
    * Sample extraction table showing extracted competencies and confidence indicators.
  * **Non-Production Warning:** Explains that automatic extraction serves as a review aid and does not constitute formal curriculum adoption.

---

## 8. Step-by-Step Execution Plan

### Step 1: Initialize Project Scaffold
* Run `npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"` in the target worktree.
* Install dependencies: `npm install zustand lucide-react clsx tailwind-merge`.
* Verify Next.js dev server starts cleanly.

### Step 2: Establish Design Tokens & Typography
* Configure `app/layout.tsx` with `next/font/google` for **Plus Jakarta Sans**.
* Extend `tailwind.config.ts` with the DLSU-D color palette (`#007041`, `#00502E`, `#0284C7`, `#D97706`).
* Add 3D button utility classes and keyframe animations into `app/globals.css`.

### Step 3: Implement TypeScript Fixtures & Evaluator Engine
* Create `types/index.ts` with all models defined in Section 4.
* Create fixture catalogs in `lib/fixtures/` using the 4 curriculum CSVs as source text.
* Create `lib/evaluator.ts` implementing `evaluateStudent` and `evaluateFacultyTrack`.
* Create `lib/store.ts` implementing the Zustand store with `persist`.

### Step 4: Build Core UI & Navigation Shell
* Build `components/ui/button-3d.tsx`, `components/ui/badge.tsx`, `components/ui/card.tsx`.
* Build top navigation bar with DLSU-D branding, role switcher, and demo data disclaimer banner.
* Implement `/` landing page with role cards and context restoration check.

### Step 5: Implement Student Flow
* Build `/student/setup/page.tsx` (wizard with lecture/lab checkboxes).
* Build `/student/careers/page.tsx` (career cards with live alignment match).
* Build `/student/roadmap/page.tsx`:
  * Implement `winding-path.tsx` and `milestone-node.tsx`.
  * Implement `skill-drawer.tsx` and sticky alignment summary widget.

### Step 6: Implement Faculty Flow
* Build `/faculty/page.tsx` (track selector, KPI banner, gap table, low-demand findings).
* Build `/faculty/simulate/page.tsx` (split-screen scenario sandbox with delta preview).
* Build `/faculty/report/page.tsx` (institutional review report with `@media print` styling).
* Build `/faculty/upload-preview/page.tsx` (drag-and-drop parse simulation).

### Step 7: Verification & Acceptance Testing
* Test persistence across page refreshes and role switches via `localStorage`.
* Verify all 4 tracks display distinct, coherent data without code collisions.
* Verify `@media print` cleanly prints the academic report without UI navigation artifacts.
* Validate that all anti-AI slop and demo disclaimer rules are strictly adhered to.

---

## 9. Acceptance Criteria Checklist

| ID | Criteria | Verification Method |
|---|---|---|
| **AC-01** | **Role Context & Restoration** | Select student courses $\rightarrow$ switch to faculty $\rightarrow$ return to student $\rightarrow$ verify selections remain intact. |
| **AC-02** | **Track Completeness** | Verify all 4 tracks (BSCS IS/GD, BSIT NT/WD) can be selected in both Student and Faculty views. |
| **AC-03** | **Lecture/Lab Code Collisions** | Verify courses with matching base codes but separate LEC/LAB sections are rendered and selected independently. |
| **AC-04** | **Duolingo S-Curve Roadmap** | Verify student roadmap displays serpentine winding milestone nodes with checkmarks, current pulse, and gap states. |
| **AC-05** | **Skill Inspection Drawer** | Click any roadmap node $\rightarrow$ verify slide-out drawer displays skill details, course basis, and valid external learning links. |
| **AC-06** | **Deterministic Scoring** | Toggling courses on/off dynamically recalculates alignment score and gap lists without errors or hardcoded mismatches. |
| **AC-07** | **Interactive Scenario Sandbox** | Toggle additive enhancements $\rightarrow$ verify real-time baseline vs. projected deltas recalculate immediately. |
| **AC-08** | **Printable Academic Report** | Open `/faculty/report` $\rightarrow$ trigger print preview $\rightarrow$ verify letterhead formatting, page breaks, and absence of nav headers. |
| **AC-09** | **Planned Upload Preview** | Navigate to `/faculty/upload-preview` $\rightarrow$ trigger sample PDF parse $\rightarrow$ verify progress state and disclaimer badge. |
| **AC-10** | **Anti-AI Slop & Branding** | Verify DLSU-D `#007041` green branding, tactile 3D buttons, zero generic purple gradients, and visible demo notices. |
