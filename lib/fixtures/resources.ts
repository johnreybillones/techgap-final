import { LearningResource } from '@/types';

// ─── Learning Resources Fixture ──────────────────────────────────────────────
// Verified upskilling URLs — manually curated. NOT auto-generated.
// All URLs point to real courses/documentation as of Q3 2026.
// ─────────────────────────────────────────────────────────────────────────────

export const resourcesFixture: LearningResource[] = [
  // HTML & CSS
  {
    skillId: 'skill-html-css',
    title: 'Responsive Web Design Certification',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/learn/2022/responsive-web-design/',
    estimatedHours: 300,
    type: 'Interactive',
  },
  {
    skillId: 'skill-html-css',
    title: 'HTML: HyperText Markup Language',
    provider: 'MDN Web Docs',
    url: 'https://developer.mozilla.org/en-US/docs/Web/HTML',
    estimatedHours: 20,
    type: 'Documentation',
  },

  // JavaScript
  {
    skillId: 'skill-javascript',
    title: 'JavaScript Algorithms and Data Structures',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/',
    estimatedHours: 300,
    type: 'Interactive',
  },
  {
    skillId: 'skill-javascript',
    title: 'JavaScript — MDN Web Docs',
    provider: 'MDN Web Docs',
    url: 'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
    estimatedHours: 40,
    type: 'Documentation',
  },

  // TypeScript
  {
    skillId: 'skill-typescript',
    title: 'TypeScript Handbook',
    provider: 'Official Docs',
    url: 'https://www.typescriptlang.org/docs/handbook/intro.html',
    estimatedHours: 15,
    type: 'Documentation',
  },
  {
    skillId: 'skill-typescript',
    title: 'TypeScript for JavaScript Programmers (Course)',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/typescript',
    estimatedHours: 20,
    type: 'Video Course',
  },

  // React
  {
    skillId: 'skill-react',
    title: 'Front End Development Libraries (React)',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/learn/front-end-development-libraries/',
    estimatedHours: 300,
    type: 'Interactive',
  },
  {
    skillId: 'skill-react',
    title: 'React Official Documentation',
    provider: 'Official Docs',
    url: 'https://react.dev/learn',
    estimatedHours: 30,
    type: 'Documentation',
  },

  // Next.js
  {
    skillId: 'skill-nextjs',
    title: 'Next.js App Router — Official Docs',
    provider: 'Official Docs',
    url: 'https://nextjs.org/docs',
    estimatedHours: 20,
    type: 'Documentation',
  },
  {
    skillId: 'skill-nextjs',
    title: 'Full-Stack Web Development with Next.js',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/nextjs',
    estimatedHours: 40,
    type: 'Video Course',
  },

  // Node.js
  {
    skillId: 'skill-nodejs',
    title: 'Back End Development and APIs',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/learn/back-end-development-and-apis/',
    estimatedHours: 300,
    type: 'Interactive',
  },
  {
    skillId: 'skill-nodejs',
    title: 'Node.js Official Docs',
    provider: 'Official Docs',
    url: 'https://nodejs.org/en/docs/',
    estimatedHours: 20,
    type: 'Documentation',
  },

  // SQL
  {
    skillId: 'skill-sql-db',
    title: 'Relational Database Certification',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/learn/relational-database/',
    estimatedHours: 300,
    type: 'Interactive',
  },
  {
    skillId: 'skill-sql-db',
    title: 'Databases and SQL for Data Science with Python',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/sql-data-science',
    estimatedHours: 25,
    type: 'Video Course',
  },

  // Git
  {
    skillId: 'skill-git',
    title: 'Git and GitHub for Beginners (freeCodeCamp)',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/news/git-and-github-for-beginners/',
    estimatedHours: 8,
    type: 'Interactive',
  },

  // Docker
  {
    skillId: 'skill-docker',
    title: 'Docker — Get Started',
    provider: 'Official Docs',
    url: 'https://docs.docker.com/get-started/',
    estimatedHours: 10,
    type: 'Documentation',
  },
  {
    skillId: 'skill-docker',
    title: 'Docker for Developers (Coursera)',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/docker-for-developers',
    estimatedHours: 25,
    type: 'Video Course',
  },

  // REST API Design
  {
    skillId: 'skill-rest-api',
    title: 'REST API Design Best Practices — MDN',
    provider: 'MDN Web Docs',
    url: 'https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction',
    estimatedHours: 12,
    type: 'Documentation',
  },

  // Responsive Design
  {
    skillId: 'skill-responsive-design',
    title: 'CSS: Responsive Design — MDN Web Docs',
    provider: 'MDN Web Docs',
    url: 'https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design',
    estimatedHours: 10,
    type: 'Documentation',
  },

  // Cloud Deploy
  {
    skillId: 'skill-cloud-deploy',
    title: 'Cloud Computing Specialization',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/cloud-computing',
    estimatedHours: 120,
    type: 'Video Course',
  },

  // Unit Testing
  {
    skillId: 'skill-unit-testing',
    title: 'JavaScript Testing Fundamentals — freeCodeCamp',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/news/testing-in-javascript/',
    estimatedHours: 10,
    type: 'Interactive',
  },

  // TCP/IP
  {
    skillId: 'skill-tcp-ip',
    title: 'The Bits and Bytes of Computer Networking',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/computer-networking',
    estimatedHours: 35,
    type: 'Video Course',
  },

  // Network Security
  {
    skillId: 'skill-network-security',
    title: 'IBM Cybersecurity Analyst Professional Certificate',
    provider: 'Coursera',
    url: 'https://www.coursera.org/professional-certificates/ibm-cybersecurity-analyst',
    estimatedHours: 80,
    type: 'Video Course',
  },

  // Cloud Infra
  {
    skillId: 'skill-cloud-infra',
    title: 'AWS Cloud Practitioner Essentials',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/aws-cloud-practitioner-essentials',
    estimatedHours: 30,
    type: 'Video Course',
  },

  // Linux Admin
  {
    skillId: 'skill-linux-admin',
    title: 'Linux Foundation — Introduction to Linux',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/introduction-to-linux',
    estimatedHours: 60,
    type: 'Video Course',
  },

  // DevOps CI
  {
    skillId: 'skill-devops-ci',
    title: 'DevOps Culture and Mindset',
    provider: 'Coursera',
    url: 'https://www.coursera.org/learn/devops-culture-and-mindset',
    estimatedHours: 25,
    type: 'Video Course',
  },

  // Python ML
  {
    skillId: 'skill-python-ml',
    title: 'Machine Learning with Python Certification',
    provider: 'freeCodeCamp',
    url: 'https://www.freecodecamp.org/learn/machine-learning-with-python/',
    estimatedHours: 300,
    type: 'Interactive',
  },
  {
    skillId: 'skill-python-ml',
    title: 'Python for Everybody Specialization',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/python',
    estimatedHours: 80,
    type: 'Video Course',
  },

  // ML Fundamentals
  {
    skillId: 'skill-ml-fundamentals',
    title: 'Machine Learning Specialization (Andrew Ng)',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/machine-learning-introduction',
    estimatedHours: 100,
    type: 'Video Course',
  },
  {
    skillId: 'skill-ml-fundamentals',
    title: 'Intro to Machine Learning (Kaggle)',
    provider: 'Kaggle',
    url: 'https://www.kaggle.com/learn/intro-to-machine-learning',
    estimatedHours: 8,
    type: 'Interactive',
  },

  // Deep Learning
  {
    skillId: 'skill-deep-learning',
    title: 'Deep Learning Specialization (Andrew Ng)',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/deep-learning',
    estimatedHours: 140,
    type: 'Video Course',
  },

  // Data Wrangling
  {
    skillId: 'skill-data-wrangling',
    title: 'Pandas — Kaggle Learn',
    provider: 'Kaggle',
    url: 'https://www.kaggle.com/learn/pandas',
    estimatedHours: 4,
    type: 'Interactive',
  },

  // NLP
  {
    skillId: 'skill-nlp',
    title: 'Natural Language Processing Specialization',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/natural-language-processing',
    estimatedHours: 120,
    type: 'Video Course',
  },

  // Computer Vision
  {
    skillId: 'skill-computer-vision',
    title: 'Computer Vision Basics — Kaggle',
    provider: 'Kaggle',
    url: 'https://www.kaggle.com/learn/computer-vision',
    estimatedHours: 4,
    type: 'Interactive',
  },

  // MLOps
  {
    skillId: 'skill-ml-ops',
    title: 'Machine Learning Engineering for Production (MLOps) Specialization',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops',
    estimatedHours: 120,
    type: 'Video Course',
  },

  // Data Visualization
  {
    skillId: 'skill-data-viz',
    title: 'Data Visualization — Kaggle Learn',
    provider: 'Kaggle',
    url: 'https://www.kaggle.com/learn/data-visualization',
    estimatedHours: 4,
    type: 'Interactive',
  },

  // Unity
  {
    skillId: 'skill-unity',
    title: 'Unity Learn — Official Tutorials',
    provider: 'Official Docs',
    url: 'https://learn.unity.com/',
    estimatedHours: 60,
    type: 'Interactive',
  },
  {
    skillId: 'skill-unity',
    title: 'Game Design and Development Specialization',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/game-design-and-development',
    estimatedHours: 100,
    type: 'Video Course',
  },

  // C#
  {
    skillId: 'skill-csharp',
    title: 'C# Programming for Unity Game Development',
    provider: 'Coursera',
    url: 'https://www.coursera.org/specializations/programming-unity-game-development',
    estimatedHours: 80,
    type: 'Video Course',
  },

  // VR/AR
  {
    skillId: 'skill-vr-ar',
    title: 'Unity XR — VR/AR Development',
    provider: 'Official Docs',
    url: 'https://docs.unity3d.com/Manual/XR.html',
    estimatedHours: 30,
    type: 'Documentation',
  },
];
