export type AcademicProgram = 'BSCS' | 'BSIT';

export type AcademicTrack =
  | 'BSCS_INTELLIGENT_SYSTEMS'
  | 'BSCS_GAME_DEVELOPMENT'
  | 'BSIT_NETWORK_TECHNOLOGY'
  | 'BSIT_WEB_DEVELOPMENT';

export type YearLevel = '1st Year' | '2nd Year' | '3rd Year' | '4th Year';

export type CourseComponent = 'LEC' | 'LAB' | 'COMBINED';

export interface Course {
  id: string;
  code: string;
  title: string;
  component: CourseComponent;
  track: AcademicTrack;
  yearLevel: YearLevel;
  semester: '1st Sem' | '2nd Sem';
  units: number;
  isCore: boolean;
  coveredSkillIds: string[];
}

export interface Skill {
  id: string;
  name: string;
  category: 'Core Computing' | 'Specialization' | 'Tool/Framework' | 'Professional';
  demandPercentage: number;
  demandSampleCount: string;
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
  recommendedOrder: string[];
}

export interface StudentAlignmentResult {
  roleId: string;
  roleTitle: string;
  overallScore: number;
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
  projectedAlignmentGain: number;
}

export interface TrackEvaluationResult {
  track: AcademicTrack;
  trackTitle: string;
  baselineAlignment: number;
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
