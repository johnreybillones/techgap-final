import { AcademicTrack } from '@/types';

// ─── Track Metadata ────────────────────────────────────────────────────────
export const tracksFixture: {
  id: AcademicTrack;
  label: string;
  shortLabel: string;
  program: 'BSCS' | 'BSIT';
  description: string;
  color: string;
}[] = [
  {
    id: 'BSIT_WEB_DEVELOPMENT',
    label: 'BSIT Web Development',
    shortLabel: 'BSIT WD',
    program: 'BSIT',
    description: 'Frontend, backend, and full-stack web engineering with modern JavaScript frameworks.',
    color: '#0284C7',
  },
  {
    id: 'BSIT_NETWORK_TECHNOLOGY',
    label: 'BSIT Network Technology',
    shortLabel: 'BSIT NT',
    program: 'BSIT',
    description: 'Network infrastructure, security, cloud administration, and DevOps automation.',
    color: '#D97706',
  },
  {
    id: 'BSCS_INTELLIGENT_SYSTEMS',
    label: 'BSCS Intelligent Systems',
    shortLabel: 'BSCS IS',
    program: 'BSCS',
    description: 'Machine learning, deep learning, NLP, computer vision, and MLOps deployment.',
    color: '#7C3AED',
  },
  {
    id: 'BSCS_GAME_DEVELOPMENT',
    label: 'BSCS Game Development',
    shortLabel: 'BSCS GD',
    program: 'BSCS',
    description: 'Unity/Unreal game engines, C# programming, 3D asset pipelines, and XR development.',
    color: '#059669',
  },
];
