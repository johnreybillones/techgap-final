'use client';

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
  activeEnhancementIds: string[];
  datasetSnapshot: 'Q3 2026' | 'Q4 2026';
}

interface TechGapStore {
  activeRole: 'student' | 'faculty' | null;
  student: StudentState;
  faculty: FacultyState;

  setActiveRole: (role: 'student' | 'faculty' | null) => void;
  setStudentAcademicContext: (program: AcademicProgram, track: AcademicTrack, year: YearLevel) => void;
  toggleStudentCourse: (courseId: string) => void;
  selectAllEligibleCourses: (courseIds: string[]) => void;
  clearStudentCourses: () => void;
  setStudentRole: (roleId: string) => void;

  setFacultyTrack: (track: AcademicTrack) => void;
  toggleEnhancement: (enhancementId: string) => void;
  resetFacultyScenario: () => void;
  setDatasetSnapshot: (snapshot: 'Q3 2026' | 'Q4 2026') => void;

  resetAll: () => void;
}

const defaultStudent: StudentState = {
  program: 'BSIT',
  track: 'BSIT_WEB_DEVELOPMENT',
  yearLevel: '3rd Year',
  selectedCourseIds: ['ITWB311-LEC', 'ITWB311-LAB', 'ITCS111', 'ITCS226', 'ITCS227', 'ITCS214'],
  selectedRoleId: 'role-fullstack-dev',
};

const defaultFaculty: FacultyState = {
  selectedTrack: 'BSIT_WEB_DEVELOPMENT',
  activeEnhancementIds: [],
  datasetSnapshot: 'Q3 2026',
};

export const useTechGapStore = create<TechGapStore>()(
  persist(
    (set) => ({
      activeRole: null,
      student: defaultStudent,
      faculty: defaultFaculty,

      setActiveRole: (role) => set({ activeRole: role }),

      setStudentAcademicContext: (program, track, yearLevel) =>
        set((state) => ({
          student: {
            ...state.student,
            program,
            track,
            yearLevel,
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
            ...state.faculty,
            selectedTrack: track,
            activeEnhancementIds: [],
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

      setDatasetSnapshot: (snapshot) =>
        set((state) => ({
          faculty: { ...state.faculty, datasetSnapshot: snapshot },
        })),

      resetAll: () =>
        set({
          activeRole: null,
          student: defaultStudent,
          faculty: defaultFaculty,
        }),
    }),
    {
      name: 'techgap_mock_v1',
    }
  )
);
