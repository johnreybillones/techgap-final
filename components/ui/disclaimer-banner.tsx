import { AlertTriangle, FlaskConical } from 'lucide-react';

export function DisclaimerBanner() {
  return (
    <div className="w-full bg-amber-50 border-b border-amber-200 px-4 py-2 no-print">
      <div className="max-w-7xl mx-auto flex items-center gap-2 text-amber-800 text-xs font-medium">
        <FlaskConical size={14} className="shrink-0" />
        <span>
          <strong>Illustrative Prototype / Mock Data</strong> — TechGap demo using curated fixture data
          (Q3 2026 snapshot, N=182). Results are for academic review and demonstration purposes only.
          Not connected to any live database, scraping pipeline, or trained ML model.
        </span>
        <AlertTriangle size={14} className="shrink-0 ml-auto text-amber-600" />
      </div>
    </div>
  );
}

export function MockDataBadge({ className }: { className?: string }) {
  return (
    <span className={`badge-mock ${className ?? ''}`}>
      <FlaskConical size={11} />
      Illustrative Mock Data
    </span>
  );
}
