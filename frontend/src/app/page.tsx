import Link from "next/link";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { DataRow } from "@/components/ui/DataRow";

export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-line pb-6">
        <div>
          <span className="text-xs font-mono uppercase tracking-widest text-muted">Inspection Operations</span>
          <h1 className="text-2xl font-bold tracking-tight text-text">Screening Queue</h1>
        </div>
        <div>
          <Link
            href="/screenings/new"
            className="inline-flex items-center justify-center px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 transition-opacity"
          >
            + Start Screening Session
          </Link>
        </div>
      </div>

      {/* Overview Table / List Preview */}
      <div className="section !pt-0">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted mb-4">
          System Verification Preview
        </h2>
        <div className="border border-line bg-surface rounded-sm p-4">
          <DataRow label="System Mode" value="Decision Support (Officer in the Loop)" />
          <DataRow label="API Status">
            <StatusBadge status="VALID" label="Operational" />
          </DataRow>
          <DataRow label="OCR Engine">
            <StatusBadge status="PASS" label="PaddleOCR + OpenCV Preprocessing" />
          </DataRow>
          <DataRow label="MRZ Rule Engine">
            <StatusBadge status="PASS" label="ICAO 9303 Deterministic" />
          </DataRow>
          <DataRow label="Tampering Heuristics">
            <StatusBadge status="REVIEW" label="Calibrated Baseline" />
          </DataRow>
        </div>
      </div>
    </div>
  );
}
