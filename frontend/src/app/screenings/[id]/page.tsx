"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, ScreeningDetail, EvidenceItem } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { DataRow } from "@/components/ui/DataRow";

export default function ScreeningDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [screening, setScreening] = useState<ScreeningDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchScreening();
  }, [id]);

  const fetchScreening = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getScreening(id);
      setScreening(data);
    } catch (err: any) {
      setError(err.message || "Failed to load screening record");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-12 space-y-4">
        <div className="h-4 w-40 bg-line animate-pulse rounded-sm" />
        <div className="h-8 w-64 bg-line animate-pulse rounded-sm" />
        <div className="h-48 w-full bg-surface border border-line animate-pulse rounded-sm mt-8" />
      </div>
    );
  }

  if (error || !screening) {
    return (
      <div className="py-12 max-w-lg mx-auto text-center space-y-4">
        <div className="p-4 bg-danger/10 border border-danger/20 text-danger rounded-sm text-sm">
          <strong>Screening Lookup Failed:</strong> {error || "Record not found"}
        </div>
        <div className="flex justify-center gap-4">
          <button
            onClick={fetchScreening}
            className="px-4 py-2 border border-line bg-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:bg-bg"
          >
            Retry
          </button>
          <Link
            href="/"
            className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90"
          >
            Return to Queue
          </Link>
        </div>
      </div>
    );
  }

  // Extract fields helper
  const getField = (name: string) => {
    const found = screening.extracted_fields.find(
      (f) => f.field_name.toLowerCase() === name.toLowerCase()
    );
    return found?.value_text || "—";
  };

  const doc = screening.documents[0];

  return (
    <div className="max-w-4xl mx-auto py-6 space-y-8">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center justify-between border-b border-line pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="text-xs font-semibold uppercase tracking-wider text-muted hover:text-text transition-colors"
          >
            ← Queue
          </Link>
          <span className="text-muted text-xs">/</span>
          <span className="text-xs font-mono font-bold text-text uppercase">
            {screening.id}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs font-mono text-muted uppercase">
            Station: {screening.checkpoint_id}
          </span>
          <StatusBadge status={screening.status} />
        </div>
      </div>

      {/* Screen Header Banner */}
      <div>
        <span className="text-xs font-mono uppercase tracking-widest text-muted">
          Screening Verification Workstation
        </span>
        <div className="flex items-baseline justify-between mt-1">
          <h1 className="text-2xl font-bold tracking-tight text-text">
            {doc?.type || "Unclassified Identity Document"}
          </h1>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase text-muted font-medium">Review Priority:</span>
            <StatusBadge status={screening.review_priority} />
          </div>
        </div>
      </div>

      {/* Main Verification Panels */}
      <div className="border-t border-line divide-y divide-line">
        {/* IDENTITY SECTION */}
        <div className="section">
          <h2 className="text-xs font-bold uppercase tracking-widest text-muted mb-3">
            Identity
          </h2>
          <DataRow label="Name" value={getField("name") !== "—" ? getField("name") : "Awaiting document intake"} />
          <DataRow label="Nationality" value={getField("nationality")} />
          <DataRow label="Date of Birth" value={getField("date_of_birth")} />
        </div>

        {/* DOCUMENT SECTION */}
        <div className="section">
          <h2 className="text-xs font-bold uppercase tracking-widest text-muted mb-3">
            Document
          </h2>
          <DataRow label="Document Number" value={getField("document_number")} />
          <DataRow label="Expiry">
            <StatusBadge status={doc?.expiry_date ? "VALID" : "PENDING"} label={doc?.expiry_date ? String(doc.expiry_date) : "Pending intake"} />
          </DataRow>
          <DataRow label="MRZ">
            <StatusBadge status={screening.verification.mrz} />
          </DataRow>
        </div>

        {/* VERIFICATION SECTION */}
        <div className="section">
          <h2 className="text-xs font-bold uppercase tracking-widest text-muted mb-3">
            Verification
          </h2>
          <DataRow label="External Registry">
            <StatusBadge status={screening.verification.external} />
          </DataRow>
          <DataRow label="Face Comparison">
            <StatusBadge status={screening.verification.face} />
          </DataRow>
        </div>

        {/* ANALYSIS SECTION */}
        <div className="section">
          <h2 className="text-xs font-bold uppercase tracking-widest text-muted mb-3">
            Analysis
          </h2>
          <DataRow label="Photo Region">
            <StatusBadge status={screening.analysis.photo} />
          </DataRow>
          <DataRow label="Text Integrity">
            <StatusBadge status={screening.analysis.text} />
          </DataRow>
          <DataRow label="Security Stamp">
            <StatusBadge status={screening.analysis.stamp} />
          </DataRow>
        </div>

        {/* REASONS FOR REVIEW SECTION */}
        {screening.reasons && screening.reasons.length > 0 && (
          <div className="section bg-warning/5 p-4 rounded-sm border border-warning/20">
            <h2 className="text-xs font-bold uppercase tracking-widest text-warning mb-2">
              Reasons for Review
            </h2>
            <ul className="list-disc list-inside space-y-1 text-sm text-text">
              {screening.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="pt-4 flex items-center justify-between border-t border-line">
        <div className="text-xs text-muted font-mono">
          Created {new Date(screening.created_at).toLocaleString()}
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowEvidenceModal(true)}
            className="px-4 py-2 border border-line bg-surface text-xs font-semibold uppercase tracking-wider text-text rounded-sm hover:bg-bg transition-colors"
          >
            View Evidence ({screening.evidence_items.length})
          </button>
          <button
            type="button"
            onClick={() => alert(`Manual review recorded for ${screening.id}`)}
            className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 transition-opacity"
          >
            Manual Review
          </button>
        </div>
      </div>

      {/* Evidence Modal Drawer */}
      {showEvidenceModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-surface border border-line max-w-xl w-full p-6 rounded-sm space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-text">
                Evidence Items • {screening.id}
              </h3>
              <button
                onClick={() => setShowEvidenceModal(false)}
                className="text-muted hover:text-text text-sm font-mono"
              >
                ✕
              </button>
            </div>

            <div className="max-h-80 overflow-y-auto space-y-3">
              {screening.evidence_items.length === 0 ? (
                <p className="text-xs text-muted py-6 text-center">
                  No evidence flags generated yet. Document intake pending.
                </p>
              ) : (
                screening.evidence_items.map((e) => (
                  <div key={e.id} className="p-3 border border-line bg-bg rounded-sm space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold uppercase text-text">
                        {e.category}
                      </span>
                      <StatusBadge status={e.severity} />
                    </div>
                    <p className="text-xs text-text">{e.explanation}</p>
                    <span className="text-[10px] font-mono text-muted block">
                      Module: {e.source_module}
                    </span>
                  </div>
                ))
              )}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowEvidenceModal(false)}
                className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
