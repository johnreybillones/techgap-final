'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle2, Circle, ChevronRight, Layers, BookOpen, FlaskConical } from 'lucide-react';
import { useTechGapStore } from '@/lib/store';
import { coursesFixture } from '@/lib/fixtures/courses';
import { tracksFixture } from '@/lib/fixtures/tracks';
import { AcademicProgram, AcademicTrack, YearLevel } from '@/types';
import Button3D from '@/components/ui/button-3d';
import { cn } from '@/lib/utils';

type TabFilter = 'all' | 'core' | 'track';

export default function StudentSetupPage() {
  const router = useRouter();
  const {
    student,
    setStudentAcademicContext,
    toggleStudentCourse,
    selectAllEligibleCourses,
    clearStudentCourses,
  } = useTechGapStore();

  const [program, setProgram] = useState<AcademicProgram>(student.program);
  const [track, setTrack] = useState<AcademicTrack>(student.track);
  const [yearLevel, setYearLevel] = useState<YearLevel>(student.yearLevel);
  const [tab, setTab] = useState<TabFilter>('all');

  // Filter tracks to the selected program
  const availableTracks = tracksFixture.filter((t) => t.program === program);

  // Get courses for the selected track
  const trackCourses = useMemo(
    () => coursesFixture.filter((c) => c.track === track),
    [track]
  );

  const filteredCourses = useMemo(() => {
    if (tab === 'core') return trackCourses.filter((c) => c.isCore);
    if (tab === 'track') return trackCourses.filter((c) => !c.isCore);
    return trackCourses;
  }, [trackCourses, tab]);

  // Keep local selections synced to the store's track
  const currentSelections = student.track === track ? student.selectedCourseIds : [];

  const isSelected = (id: string) => currentSelections.includes(id);
  const selectionCount = trackCourses.filter((c) => currentSelections.includes(c.id)).length;

  const handleProgramChange = (p: AcademicProgram) => {
    setProgram(p);
    // Default to first track in that program
    const firstTrack = tracksFixture.find((t) => t.program === p);
    if (firstTrack) setTrack(firstTrack.id);
  };

  const handleTrackChange = (t: AcademicTrack) => {
    setTrack(t);
    setStudentAcademicContext(program, t, yearLevel);
  };

  const handleToggle = (courseId: string) => {
    // Commit academic context first if needed
    if (student.track !== track) {
      setStudentAcademicContext(program, track, yearLevel);
    }
    toggleStudentCourse(courseId);
  };

  const handleSelectAll = () => {
    setStudentAcademicContext(program, track, yearLevel);
    selectAllEligibleCourses(trackCourses.map((c) => c.id));
  };

  const handleClear = () => {
    clearStudentCourses();
  };

  const handleProceed = () => {
    setStudentAcademicContext(program, track, yearLevel);
    router.push('/student/careers');
  };

  // Group courses by year level for display
  const yearGroups: YearLevel[] = ['1st Year', '2nd Year', '3rd Year', '4th Year'];

  const componentLabel = (component: string) => {
    if (component === 'LEC') return 'LEC';
    if (component === 'LAB') return 'LAB';
    return null;
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Page Title */}
      <div className="mb-8">
        <h1 className="text-2xl font-extrabold text-[#0F172A] mb-1">Academic Context & Course Selection</h1>
        <p className="text-[#64748B]">
          Select your program, specialization track, and all courses you have completed.
          This powers your personalized career alignment roadmap.
        </p>
      </div>

      {/* Step 1: Academic Context */}
      <div className="card mb-6">
        <div className="px-6 py-4 border-b border-[#E2E8F0] flex items-center gap-3">
          <div className="w-7 h-7 bg-[#007041] rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0">1</div>
          <h2 className="font-bold text-[#0F172A]">Academic Context</h2>
        </div>
        <div className="px-6 py-5 grid md:grid-cols-3 gap-5">
          {/* Program */}
          <div>
            <label className="block text-sm font-semibold text-[#0F172A] mb-2">Program</label>
            <div className="flex gap-2">
              {(['BSCS', 'BSIT'] as AcademicProgram[]).map((p) => (
                <button
                  key={p}
                  onClick={() => handleProgramChange(p)}
                  className={cn(
                    'flex-1 py-2.5 px-3 rounded-xl text-sm font-semibold border-2 transition-all',
                    program === p
                      ? 'border-[#007041] bg-[#F0FDF4] text-[#007041]'
                      : 'border-[#E2E8F0] bg-white text-[#64748B] hover:border-slate-300'
                  )}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Track */}
          <div className="md:col-span-1">
            <label className="block text-sm font-semibold text-[#0F172A] mb-2">Specialization Track</label>
            <select
              value={track}
              onChange={(e) => handleTrackChange(e.target.value as AcademicTrack)}
              className="w-full border-2 border-[#E2E8F0] rounded-xl px-3 py-2.5 text-sm font-medium text-[#0F172A] bg-white focus:border-[#007041] focus:outline-none transition-colors"
            >
              {availableTracks.map((t) => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* Year Level */}
          <div>
            <label className="block text-sm font-semibold text-[#0F172A] mb-2">Current Year Level</label>
            <select
              value={yearLevel}
              onChange={(e) => setYearLevel(e.target.value as YearLevel)}
              className="w-full border-2 border-[#E2E8F0] rounded-xl px-3 py-2.5 text-sm font-medium text-[#0F172A] bg-white focus:border-[#007041] focus:outline-none transition-colors"
            >
              {(['1st Year', '2nd Year', '3rd Year', '4th Year'] as YearLevel[]).map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Step 2: Course Selection */}
      <div className="card mb-6">
        <div className="px-6 py-4 border-b border-[#E2E8F0] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 bg-[#007041] rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0">2</div>
            <h2 className="font-bold text-[#0F172A]">Completed Courses</h2>
            <span className="badge-green text-xs">{selectionCount} selected</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSelectAll}
              className="text-xs font-semibold text-[#007041] hover:underline transition-colors"
            >
              Select All
            </button>
            <span className="text-[#E2E8F0]">|</span>
            <button
              onClick={handleClear}
              className="text-xs font-semibold text-[#64748B] hover:underline transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="px-6 pt-4 pb-2 flex gap-2 border-b border-[#E2E8F0]">
          {([
            { key: 'all', label: 'All Eligible', icon: Layers },
            { key: 'core', label: 'Core Computing', icon: BookOpen },
            { key: 'track', label: 'Track Specialization', icon: FlaskConical },
          ] as { key: TabFilter; label: string; icon: React.ElementType }[]).map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={cn(
                'flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-all',
                tab === key
                  ? 'bg-[#007041] text-white'
                  : 'bg-slate-100 text-[#64748B] hover:bg-slate-200'
              )}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>

        {/* Course Grid */}
        <div className="px-6 py-4">
          {yearGroups.map((year) => {
            const yearCourses = filteredCourses.filter((c) => c.yearLevel === year);
            if (yearCourses.length === 0) return null;
            return (
              <div key={year} className="mb-5">
                <h3 className="text-xs font-bold text-[#64748B] uppercase tracking-wider mb-3">{year}</h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {yearCourses.map((course) => {
                    const selected = isSelected(course.id);
                    return (
                      <button
                        key={course.id}
                        id={`course-${course.id}`}
                        onClick={() => handleToggle(course.id)}
                        className={cn(
                          'text-left p-3 rounded-xl border-2 transition-all duration-150 group',
                          selected
                            ? 'border-[#007041] bg-[#F0FDF4]'
                            : 'border-[#E2E8F0] bg-white hover:border-slate-300 hover:bg-slate-50'
                        )}
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <span className="font-mono text-xs font-bold text-[#007041] shrink-0">{course.code}</span>
                            {componentLabel(course.component) && (
                              <span className={cn(
                                'text-xs font-bold px-1.5 py-0.5 rounded shrink-0',
                                course.component === 'LEC'
                                  ? 'bg-sky-100 text-[#0284C7]'
                                  : 'bg-amber-100 text-amber-700'
                              )}>
                                {course.component}
                              </span>
                            )}
                          </div>
                          {selected
                            ? <CheckCircle2 size={18} className="text-[#007041] shrink-0 mt-0.5" />
                            : <Circle size={18} className="text-slate-300 shrink-0 mt-0.5 group-hover:text-slate-400" />
                          }
                        </div>
                        <p className="text-xs font-medium text-[#0F172A] leading-tight">{course.title}</p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <span className="text-xs text-[#64748B]">{course.semester}</span>
                          <span className="text-[#E2E8F0] text-xs">·</span>
                          <span className="text-xs text-[#64748B]">{course.units}u</span>
                          {course.isCore && <span className="badge-blue text-xs">Core</span>}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Validation & Proceed */}
      {selectionCount === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4 flex items-start gap-3 text-sm">
          <span className="text-amber-600 mt-0.5">⚠️</span>
          <span className="text-amber-800">
            Select at least one completed course to compute your evidence path and career alignment score.
          </span>
        </div>
      )}

      <div className="flex justify-end">
        <Button3D
          variant="primary"
          size="lg"
          onClick={handleProceed}
          disabled={selectionCount === 0}
        >
          Proceed to Career Selection
          <ChevronRight size={20} />
        </Button3D>
      </div>
    </div>
  );
}
