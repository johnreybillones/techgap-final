import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import './globals.css';

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-plus-jakarta',
  weight: ['400', '500', '600', '700', '800'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'TechGap — Curriculum Alignment Tool | DLSU-D',
  description:
    'Illustrative prototype for TechGap: an academic curriculum gap analysis tool for De La Salle University–Dasmariñas. Explore student career alignment and faculty curriculum simulation. Mock data only.',
  keywords: ['TechGap', 'curriculum', 'DLSU-D', 'career alignment', 'gap analysis', 'BSIT', 'BSCS'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={plusJakarta.variable}>
      <body className="min-h-screen bg-surface-bg font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
