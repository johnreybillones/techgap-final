'use client';

import { useState } from 'react';
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Info,
  BookOpen,
  Layers,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { Button3D } from '@/components/ui/button-3d';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';

interface ExtractedCompetency {
  code: string;
  name: string;
  category: string;
  confidence: number;
  sourceContext: string;
}

const sampleExtractedData = {
  courseCode: 'ITWB311LA',
  courseTitle: 'Web Development (Laboratory)',
  academicTerm: '1st Semester, A.Y. 2026-2027',
  units: 1,
  totalOutcomes: 5,
  competencies: [
    {
      code: 'SKILL-01',
      name: 'HTML5 & Semantic Web',
      category: 'Core Computing',
      confidence: 0.98,
      sourceContext: 'Laboratory Exercise 1 & 2: Semantic HTML5 Structure, W3C validation compliance.',
    },
    {
      code: 'SKILL-02',
      name: 'CSS3 & Responsive Layouts',
      category: 'Core Computing',
      confidence: 0.96,
      sourceContext: 'Laboratory Exercise 3: Flexbox, CSS Grid systems, mobile-first media queries.',
    },
    {
      code: 'SKILL-03',
      name: 'JavaScript (ES6+)',
      category: 'Core Computing',
      confidence: 0.94,
      sourceContext: 'Laboratory Exercise 4-6: DOM manipulation, asynchronous Fetch API, event handling.',
    },
    {
      code: 'SKILL-07',
      name: 'RESTful API Integration',
      category: 'Specialization',
      confidence: 0.91,
      sourceContext: 'Midterm Practical Exam: Consuming third-party JSON endpoints with token headers.',
    },
    {
      code: 'SKILL-04',
      name: 'Git & Version Control',
      category: 'Tool/Framework',
      confidence: 0.88,
      sourceContext: 'Laboratory Continuous Assessment: GitHub repository branch workflows and PR submissions.',
    },
  ] as ExtractedCompetency[],
};

export default function FacultyUploadPreviewPage() {
  const [dragActive, setDragActive] = useState(false);
  const [fileSelected, setFileSelected] = useState<string | null>(null);
  const [pipelineState, setPipelineState] = useState<'idle' | 'parsing' | 'completed'>('idle');
  const [progressStage, setProgressStage] = useState<number>(0);

  const stages = [
    'Reading PDF binary stream & OCR verification...',
    'Extracting Syllabus Intended Learning Outcomes (SILOs)...',
    'Normalizing Bloom taxonomy action verbs & keywords...',
    'Mapping extracted competencies against TechGap industry ontology...',
  ];

  const handleSimulateExtraction = (filename = 'S-ITWB311LA_Web_Development_Lab.pdf') => {
    setFileSelected(filename);
    setPipelineState('parsing');
    setProgressStage(0);

    const timer1 = setTimeout(() => setProgressStage(1), 600);
    const timer2 = setTimeout(() => setProgressStage(2), 1200);
    const timer3 = setTimeout(() => setProgressStage(3), 1800);
    const timer4 = setTimeout(() => setPipelineState('completed'), 2400);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  };

  const handleReset = () => {
    setFileSelected(null);
    setPipelineState('idle');
    setProgressStage(0);
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Planned Feature Banner */}
      <div className="mb-8 p-5 bg-gradient-to-r from-sky-50 via-white to-sky-50 border-2 border-sky-200 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-sky-500 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Sparkles size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-extrabold text-slate-900">
                Planned Faculty Syllabus Extension — Future Feature Preview
              </h2>
              <Badge variant="blue">v2.0 Roadmap Concept</Badge>
            </div>
            <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">
              This interactive mockup demonstrates the envisioned institutional pipeline where faculty can upload course syllabi in PDF format to automatically extract learning outcomes and evaluate competency alignment without manual tagging.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold">
            <ShieldAlert size={14} className="text-amber-600" />
            <span>Interactive Prototype Simulation</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Upload Dropzone & Quick Action */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6">
            <h3 className="text-base font-extrabold text-slate-900 mb-2 flex items-center gap-2">
              <Upload size={18} className="text-primary-green" />
              Upload Course Syllabus
            </h3>
            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
              Drop an official DLSU-D Course Syllabus (.pdf) to simulate the automated text extraction and outcome taxonomy parser.
            </p>

            {/* Dropzone Area */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                const files = e.dataTransfer.files;
                if (files && files[0]) {
                  handleSimulateExtraction(files[0].name);
                }
              }}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                dragActive
                  ? 'border-primary-green bg-green-50/50 scale-[1.01]'
                  : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
              }`}
            >
              <div className="w-14 h-14 mx-auto rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3">
                <FileText size={28} />
              </div>

              <div className="text-xs font-bold text-slate-700 mb-1">
                Drag and drop your syllabus file here
              </div>
              <p className="text-[11px] text-slate-400 mb-4">
                Supported formats: PDF (OCR compliant) • Max size: 10MB
              </p>

              <button
                type="button"
                onClick={() => handleSimulateExtraction('Manual_Upload_ITWB311LA.pdf')}
                disabled={pipelineState === 'parsing'}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-primary-green hover:underline cursor-pointer"
              >
                Or browse files from your computer
              </button>
            </div>

            {/* Preloaded Sample Trigger */}
            <div className="mt-6 pt-5 border-t border-slate-100">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                Quick Demonstration
              </span>
              <button
                type="button"
                onClick={() => handleSimulateExtraction('S-ITWB311LA_Web_Development_Lab.pdf')}
                disabled={pipelineState === 'parsing'}
                className="w-full flex items-center justify-between p-3.5 rounded-xl border border-primary-green/30 bg-[#F0FDF4] hover:bg-[#DCFCE7] text-left transition-colors group cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary-green text-white flex items-center justify-center shrink-0">
                    <FileText size={16} />
                  </div>
                  <div>
                    <div className="text-xs font-extrabold text-slate-900 group-hover:text-primary-green transition-colors">
                      Load Sample: S-ITWB311LA Web Dev Lab.pdf
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Standard BSIT 3rd Year Laboratory Syllabus (DLSU-D Format)
                    </div>
                  </div>
                </div>
                <ChevronRight size={16} className="text-primary-green group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          </Card>

          {/* Institutional Compliance Notice */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
            <div className="flex items-start gap-2.5">
              <Info size={16} className="text-slate-500 shrink-0 mt-0.5" />
              <div className="text-xs text-slate-600 leading-relaxed">
                <strong className="text-slate-800">Non-Production Warning:</strong> Automatic extraction serves as an advisory review aid. Any official curriculum change requires Department Curriculum Committee deliberation, Dean endorsement, and Academic Council ratification.
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Pipeline State & Extracted Results */}
        <div className="lg:col-span-7">
          {pipelineState === 'idle' && (
            <div className="h-full min-h-[420px] rounded-2xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center p-8 text-center bg-white">
              <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 mb-4">
                <Layers size={32} />
              </div>
              <h3 className="text-sm font-extrabold text-slate-800 mb-1">
                No Syllabus Processed Yet
              </h3>
              <p className="text-xs text-slate-500 max-w-sm mb-6 leading-relaxed">
                Upload a syllabus document or click the pre-loaded sample button on the left to observe the simulated extraction pipeline.
              </p>
              <Button3D
                variant="primary"
                onClick={() => handleSimulateExtraction('S-ITWB311LA_Web_Development_Lab.pdf')}
              >
                Run Sample Pipeline Demo
              </Button3D>
            </div>
          )}

          {pipelineState === 'parsing' && (
            <Card className="p-8">
              <div className="text-center mb-6">
                <div className="w-14 h-14 mx-auto rounded-full bg-sky-100 text-sky-600 flex items-center justify-center mb-3 animate-spin">
                  <RefreshCw size={24} />
                </div>
                <h3 className="text-base font-extrabold text-slate-900">
                  Simulating Natural Language Parsing
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Processing: <span className="font-semibold text-slate-700">{fileSelected}</span>
                </p>
              </div>

              {/* Progress Steps */}
              <div className="space-y-3 max-w-md mx-auto">
                {stages.map((stage, idx) => {
                  const isDone = progressStage > idx;
                  const isCurrent = progressStage === idx;
                  return (
                    <div
                      key={idx}
                      className={`flex items-center gap-3 p-3 rounded-lg border text-xs transition-all ${
                        isDone
                          ? 'bg-green-50 border-green-200 text-green-900'
                          : isCurrent
                          ? 'bg-sky-50 border-sky-300 text-sky-900 font-bold shadow-sm'
                          : 'bg-slate-50 border-slate-200 text-slate-400'
                      }`}
                    >
                      {isDone ? (
                        <CheckCircle2 size={16} className="text-primary-green shrink-0" />
                      ) : isCurrent ? (
                        <Clock size={16} className="text-sky-600 animate-spin shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border-2 border-slate-300 shrink-0" />
                      )}
                      <span>{stage}</span>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {pipelineState === 'completed' && (
            <div className="space-y-6">
              {/* Document Overview Header */}
              <Card className="p-6 border-l-4 border-l-primary-green">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-primary-green bg-green-50 px-2.5 py-0.5 rounded-full border border-green-200">
                        {sampleExtractedData.courseCode}
                      </span>
                      <h3 className="text-base font-extrabold text-slate-900">
                        {sampleExtractedData.courseTitle}
                      </h3>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {sampleExtractedData.academicTerm} • {sampleExtractedData.units} Unit Lab
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={handleReset}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-xs font-bold text-slate-600 cursor-pointer"
                    >
                      <RefreshCw size={12} />
                      Reset
                    </button>
                    <Badge variant="green">Extraction Complete</Badge>
                  </div>
                </div>

                {/* Extraction Summary Stats */}
                <div className="grid grid-cols-3 gap-4 pt-4 text-center">
                  <div className="bg-slate-50 rounded-lg p-2.5">
                    <div className="text-lg font-black text-slate-900">
                      {sampleExtractedData.totalOutcomes}
                    </div>
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                      Identified Outcomes
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2.5">
                    <div className="text-lg font-black text-primary-green">
                      {sampleExtractedData.competencies.length}
                    </div>
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                      Mapped Skills
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2.5">
                    <div className="text-lg font-black text-sky-600">
                      93.4%
                    </div>
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                      Avg. Confidence
                    </div>
                  </div>
                </div>
              </Card>

              {/* Extracted Competencies Table */}
              <Card className="overflow-hidden">
                <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                  <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                    <BookOpen size={14} className="text-slate-500" />
                    Mapped Competencies & Evidence Context
                  </h4>
                  <span className="text-[11px] text-slate-500">
                    5 competencies tagged
                  </span>
                </div>

                <div className="divide-y divide-slate-100">
                  {sampleExtractedData.competencies.map((comp) => (
                    <div key={comp.code} className="p-4 hover:bg-slate-50/50 transition-colors">
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-2">
                          <span className="font-extrabold text-xs text-slate-900">
                            {comp.name}
                          </span>
                          <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                            {comp.category}
                          </span>
                        </div>
                        <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <span>{Math.round(comp.confidence * 100)}% Match</span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-600 font-mono bg-slate-50 p-2 rounded border border-slate-100 text-[11px]">
                        <span className="text-slate-400 font-sans mr-1">Source excerpt:</span>
                        &ldquo;{comp.sourceContext}&rdquo;
                      </p>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                  <span className="text-slate-500">
                    Ready to compare against TechGap academic tracks?
                  </span>
                  <Button3D
                    variant="primary"
                    onClick={() => {
                      window.location.href = '/faculty/simulate';
                    }}
                  >
                    Send to Simulation Sandbox
                    <ArrowRight size={14} className="ml-1 inline" />
                  </Button3D>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
