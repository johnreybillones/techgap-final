import { CareerRole } from '@/types';

// ─── Career Roles Fixture ─────────────────────────────────────────────────────
// Industry roles with required competencies and recommended S-curve order.
// recommendedOrder defines the progressive skill acquisition path shown in roadmap.
// ─────────────────────────────────────────────────────────────────────────────

export const rolesFixture: CareerRole[] = [
  // ── BSIT Web Development Roles ────────────────────────────────────────────
  {
    id: 'role-fullstack-dev',
    title: 'Full Stack Developer',
    applicableTrack: 'BSIT_WEB_DEVELOPMENT',
    description:
      'Designs and builds end-to-end web applications, owning both the frontend (React, HTML/CSS) and backend (Node.js, REST APIs) alongside cloud deployment and DevOps practices.',
    requiredSkillIds: [
      'skill-html-css',
      'skill-javascript',
      'skill-typescript',
      'skill-react',
      'skill-nodejs',
      'skill-sql-db',
      'skill-git',
      'skill-rest-api',
      'skill-docker',
      'skill-cloud-deploy',
    ],
    recommendedOrder: [
      'skill-html-css',
      'skill-javascript',
      'skill-git',
      'skill-sql-db',
      'skill-oop',
      'skill-rest-api',
      'skill-react',
      'skill-nodejs',
      'skill-typescript',
      'skill-docker',
      'skill-cloud-deploy',
    ],
  },
  {
    id: 'role-frontend-engineer',
    title: 'Frontend Engineer',
    applicableTrack: 'BSIT_WEB_DEVELOPMENT',
    description:
      'Specializes in building pixel-perfect, performant user interfaces using modern frameworks (React, Next.js) with strong TypeScript and responsive design fundamentals.',
    requiredSkillIds: [
      'skill-html-css',
      'skill-javascript',
      'skill-typescript',
      'skill-react',
      'skill-nextjs',
      'skill-responsive-design',
      'skill-git',
      'skill-unit-testing',
    ],
    recommendedOrder: [
      'skill-html-css',
      'skill-responsive-design',
      'skill-javascript',
      'skill-git',
      'skill-react',
      'skill-typescript',
      'skill-nextjs',
      'skill-unit-testing',
    ],
  },
  {
    id: 'role-backend-developer',
    title: 'Backend Developer',
    applicableTrack: 'BSIT_WEB_DEVELOPMENT',
    description:
      'Architects and maintains server-side applications, RESTful APIs, database schemas, and cloud infrastructure with a focus on scalability and security.',
    requiredSkillIds: [
      'skill-nodejs',
      'skill-sql-db',
      'skill-rest-api',
      'skill-oop',
      'skill-git',
      'skill-docker',
      'skill-cloud-deploy',
      'skill-unit-testing',
    ],
    recommendedOrder: [
      'skill-oop',
      'skill-sql-db',
      'skill-git',
      'skill-rest-api',
      'skill-nodejs',
      'skill-unit-testing',
      'skill-docker',
      'skill-cloud-deploy',
    ],
  },

  // ── BSIT Network Technology Roles ─────────────────────────────────────────
  {
    id: 'role-network-engineer',
    title: 'Network Engineer',
    applicableTrack: 'BSIT_NETWORK_TECHNOLOGY',
    description:
      'Designs, deploys, and maintains enterprise network infrastructure including routing/switching, security, and cloud integration.',
    requiredSkillIds: [
      'skill-tcp-ip',
      'skill-network-security',
      'skill-cisco-routing',
      'skill-linux-admin',
      'skill-cloud-infra',
      'skill-virtualization',
      'skill-wireless-net',
      'skill-monitoring',
    ],
    recommendedOrder: [
      'skill-tcp-ip',
      'skill-cisco-routing',
      'skill-linux-admin',
      'skill-network-security',
      'skill-wireless-net',
      'skill-virtualization',
      'skill-monitoring',
      'skill-cloud-infra',
    ],
  },
  {
    id: 'role-cloud-sysadmin',
    title: 'Cloud Systems Administrator',
    applicableTrack: 'BSIT_NETWORK_TECHNOLOGY',
    description:
      'Manages cloud-based infrastructure on AWS/Azure, implements CI/CD pipelines, and automates network tasks using Python scripting.',
    requiredSkillIds: [
      'skill-cloud-infra',
      'skill-linux-admin',
      'skill-devops-ci',
      'skill-scripting-python',
      'skill-virtualization',
      'skill-monitoring',
      'skill-network-security',
    ],
    recommendedOrder: [
      'skill-linux-admin',
      'skill-tcp-ip',
      'skill-network-security',
      'skill-scripting-python',
      'skill-virtualization',
      'skill-cloud-infra',
      'skill-devops-ci',
      'skill-monitoring',
    ],
  },
  {
    id: 'role-cybersecurity-analyst',
    title: 'Cybersecurity Analyst',
    applicableTrack: 'BSIT_NETWORK_TECHNOLOGY',
    description:
      'Identifies vulnerabilities, monitors threats, and implements security protocols across enterprise network environments.',
    requiredSkillIds: [
      'skill-network-security',
      'skill-tcp-ip',
      'skill-linux-admin',
      'skill-scripting-python',
      'skill-monitoring',
      'skill-cloud-infra',
    ],
    recommendedOrder: [
      'skill-tcp-ip',
      'skill-linux-admin',
      'skill-network-security',
      'skill-monitoring',
      'skill-scripting-python',
      'skill-cloud-infra',
    ],
  },

  // ── BSCS Intelligent Systems Roles ────────────────────────────────────────
  {
    id: 'role-ml-engineer',
    title: 'Machine Learning Engineer',
    applicableTrack: 'BSCS_INTELLIGENT_SYSTEMS',
    description:
      'Develops, trains, and deploys ML models using Python (scikit-learn, PyTorch, TensorFlow) with MLOps practices for production deployment on cloud platforms.',
    requiredSkillIds: [
      'skill-python-ml',
      'skill-ml-fundamentals',
      'skill-deep-learning',
      'skill-data-wrangling',
      'skill-sql-analytics',
      'skill-ml-ops',
      'skill-cloud-ml',
      'skill-data-viz',
    ],
    recommendedOrder: [
      'skill-python-ml',
      'skill-sql-analytics',
      'skill-data-wrangling',
      'skill-data-viz',
      'skill-ml-fundamentals',
      'skill-deep-learning',
      'skill-ml-ops',
      'skill-cloud-ml',
    ],
  },
  {
    id: 'role-data-scientist',
    title: 'Data Scientist',
    applicableTrack: 'BSCS_INTELLIGENT_SYSTEMS',
    description:
      'Analyzes complex datasets, builds predictive models, and communicates insights to stakeholders through data visualization and statistical analysis.',
    requiredSkillIds: [
      'skill-python-ml',
      'skill-ml-fundamentals',
      'skill-data-wrangling',
      'skill-sql-analytics',
      'skill-data-viz',
      'skill-nlp',
    ],
    recommendedOrder: [
      'skill-python-ml',
      'skill-sql-analytics',
      'skill-data-wrangling',
      'skill-data-viz',
      'skill-ml-fundamentals',
      'skill-nlp',
    ],
  },
  {
    id: 'role-ai-researcher',
    title: 'AI Research Engineer',
    applicableTrack: 'BSCS_INTELLIGENT_SYSTEMS',
    description:
      'Conducts applied AI research focusing on NLP, computer vision, and deep learning, contributing to novel model architectures and benchmark evaluations.',
    requiredSkillIds: [
      'skill-python-ml',
      'skill-deep-learning',
      'skill-nlp',
      'skill-computer-vision',
      'skill-ml-fundamentals',
      'skill-data-wrangling',
      'skill-ml-ops',
    ],
    recommendedOrder: [
      'skill-python-ml',
      'skill-data-wrangling',
      'skill-ml-fundamentals',
      'skill-deep-learning',
      'skill-nlp',
      'skill-computer-vision',
      'skill-ml-ops',
    ],
  },

  // ── BSCS Game Development Roles ───────────────────────────────────────────
  {
    id: 'role-unity-developer',
    title: 'Unity Game Developer',
    applicableTrack: 'BSCS_GAME_DEVELOPMENT',
    description:
      'Builds cross-platform games using Unity and C#, implementing gameplay mechanics, physics systems, game AI, and 2D/3D asset pipelines.',
    requiredSkillIds: [
      'skill-unity',
      'skill-csharp',
      'skill-game-physics',
      'skill-game-ai',
      'skill-2d-3d-art',
      'skill-mobile-game',
      'skill-multiplayer-net',
    ],
    recommendedOrder: [
      'skill-csharp',
      'skill-unity',
      'skill-2d-3d-art',
      'skill-game-physics',
      'skill-game-ai',
      'skill-mobile-game',
      'skill-multiplayer-net',
    ],
  },
  {
    id: 'role-game-programmer',
    title: 'Game Programmer (Generalist)',
    applicableTrack: 'BSCS_GAME_DEVELOPMENT',
    description:
      'Develops gameplay systems, tools, and engine-level features across Unity and Unreal Engine, with expertise in graphics pipelines and real-time rendering.',
    requiredSkillIds: [
      'skill-csharp',
      'skill-unity',
      'skill-unreal',
      'skill-game-physics',
      'skill-2d-3d-art',
      'skill-game-ai',
      'skill-vr-ar',
    ],
    recommendedOrder: [
      'skill-csharp',
      'skill-unity',
      'skill-game-physics',
      'skill-2d-3d-art',
      'skill-game-ai',
      'skill-unreal',
      'skill-vr-ar',
    ],
  },
  {
    id: 'role-mobile-game-dev',
    title: 'Mobile Game Developer',
    applicableTrack: 'BSCS_GAME_DEVELOPMENT',
    description:
      'Specializes in optimizing and publishing games for iOS and Android with Unity, focusing on performance, monetization, and store compliance.',
    requiredSkillIds: [
      'skill-unity',
      'skill-csharp',
      'skill-mobile-game',
      'skill-game-physics',
      'skill-2d-3d-art',
    ],
    recommendedOrder: [
      'skill-csharp',
      'skill-unity',
      'skill-2d-3d-art',
      'skill-game-physics',
      'skill-mobile-game',
    ],
  },
];
