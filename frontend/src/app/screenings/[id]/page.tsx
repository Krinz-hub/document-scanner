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
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [uploadingFace, setUploadingFace] = useState(false);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [decisionAction, setDecisionAction] = useState<string>("CLEAR");
  const [decisionNotes, setDecisionNotes] = useState("");
  const [decidedBy, setDecidedBy] = useState("OFFICER-4412");
  const [submittingDecision, setSubmittingDecision] = useState(false);

  // Document Upload Form State
  const [docFile, setDocFile] = useState<File | null>(null);
  const [mrzL1, setMrzL1] = useState("");
  const [mrzL2, setMrzL2] = useState("");
  const [faceFile, setFaceFile] = useState<File | null>(null);

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

  const handleDocumentUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docFile) return;
    setUploadingDoc(true);
    setError(null);
    try {
      await api.uploadDocument(id, docFile, mrzL1, mrzL2);
      await fetchScreening();
      setDocFile(null);
    } catch (err: any) {
      setError(err.message || "Document upload failed");
    } finally {
      setUploadingDoc(false);
    }
  };

  const handleFaceUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!faceFile) return;
    setUploadingFace(true);
    setError(null);
    try {
      await api.submitFace(id, faceFile);
      await fetchScreening();
      setFaceFile(null);
    } catch (err: any) {
      setError(err.message || "Face comparison failed");
    } finally {
      setUploadingFace(false);
    }
  };

  const fillSpecimenMRZ = () => {
    setMrzL1("P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<");
    setMrzL2("L898902C36UTO7408122F1204159ZE184226B<<<<<10");
  };

  const handleDecisionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingDecision(true);
    setError(null);
    try {
      const updated = await api.submitDecision(
        id,
        decisionAction,
        decisionNotes || undefined,
        decidedBy || undefined
      );
      setScreening(updated);
      setShowDecisionModal(false);
      setDecisionNotes("");
    } catch (err: any) {
      setError(err.message || "Failed to record manual review decision");
    } finally {
      setSubmittingDecision(false);
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

  if (error && !screening) {
    return (
      <div className="py-12 max-w-lg mx-auto text-center space-y-4">
        <div className="p-4 bg-danger/10 border border-danger/20 text-danger rounded-sm text-sm">
          <strong>Screening Lookup Failed:</strong> {error}
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

  if (!screening) return null;

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
            {doc?.type || "Identity Document Intake"}
          </h1>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase text-muted font-medium">Review Priority:</span>
            <StatusBadge status={screening.review_priority} />
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-danger/10 border border-danger/30 text-danger text-xs rounded-sm">
          <strong>Notice:</strong> {error}
        </div>
      )}

      {/* DOCUMENT INTAKE / UPLOAD SECTION IF NOT UPLOADED */}
      {!doc ? (
        <div className="border border-line bg-surface p-6 rounded-sm space-y-5">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-text">
              Step 1: Document Intake
            </h2>
            <p className="text-xs text-muted mt-1">
              Upload traveler document scan or photograph (Passport, Visa, ID).
            </p>
          </div>

          <form onSubmit={handleDocumentUpload} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1">
                Document Image File
              </label>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(e) => setDocFile(e.target.files?.[0] || null)}
                required
                className="text-xs text-muted file:mr-4 file:py-2 file:px-4 file:rounded-sm file:border-0 file:text-xs file:font-semibold file:bg-text file:text-surface hover:file:opacity-90 cursor-pointer"
              />
            </div>

            <div className="pt-2 border-t border-line space-y-2">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted">
                  Machine Readable Zone (MRZ) Optional Input
                </label>
                <button
                  type="button"
                  onClick={fillSpecimenMRZ}
                  className="text-[11px] text-muted hover:text-text underline"
                >
                  Use ICAO 9303 Specimen
                </button>
              </div>
              <input
                type="text"
                value={mrzL1}
                onChange={(e) => setMrzL1(e.target.value)}
                placeholder="P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
                className="w-full px-3 py-1.5 text-xs bg-bg border border-line rounded-sm font-mono"
              />
              <input
                type="text"
                value={mrzL2}
                onChange={(e) => setMrzL2(e.target.value)}
                placeholder="L898902C36UTO7408122F1204159ZE184226B<<<<<10"
                className="w-full px-3 py-1.5 text-xs bg-bg border border-line rounded-sm font-mono"
              />
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                disabled={uploadingDoc || !docFile}
                className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 disabled:opacity-50"
              >
                {uploadingDoc ? "Processing Document..." : "Upload & Analyze Document →"}
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* DOCUMENT PREVIEW & BIOMETRIC CAPTURE PANEL */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 border border-line bg-surface rounded-sm">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted block mb-2">
              Ingested Document Scan
            </span>
            <div className="relative border border-line bg-bg rounded-sm overflow-hidden h-52 flex items-center justify-center">
              <img
                src={api.getDocumentImageUrl(screening.id)}
                alt="Document Scan Preview"
                className="max-h-full max-w-full object-contain"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = "none";
                }}
              />
            </div>
          </div>

          <div className="flex flex-col justify-between">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-muted block mb-1">
                Live Facial Biometric Verification
              </span>
              <p className="text-xs text-muted mb-3">
                Submit traveler live camera capture to compare against document portrait.
              </p>

              <form onSubmit={handleFaceUpload} className="space-y-3">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setFaceFile(e.target.files?.[0] || null)}
                  required
                  className="text-xs text-muted file:mr-3 file:py-1.5 file:px-3 file:rounded-sm file:border-0 file:text-[11px] file:font-semibold file:bg-text file:text-surface hover:file:opacity-90 cursor-pointer"
                />
                <button
                  type="submit"
                  disabled={uploadingFace || !faceFile}
                  className="px-3 py-1.5 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 disabled:opacity-50"
                >
                  {uploadingFace ? "Verifying Face..." : "Compare Live Face"}
                </button>
              </form>
            </div>

            <div className="pt-3 border-t border-line">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-muted">Face Status:</span>
                <StatusBadge status={screening.verification.face} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Verification Panels */}
      <div className="border-t border-line divide-y divide-line">
        {/* IDENTITY SECTION */}
        <div className="section">
          <h2 className="text-xs font-bold uppercase tracking-widest text-muted mb-3">
            Identity
          </h2>
          <DataRow label="Name" value={getField("name")} />
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
            <StatusBadge
              status={getField("expiry_date") !== "—" ? "VALID" : "PENDING"}
              label={getField("expiry_date") !== "—" ? getField("expiry_date") : "Pending Intake"}
            />
          </DataRow>
          <DataRow label="MRZ Checksum">
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
              Reasons for Review ({screening.reasons.length})
            </h2>
            <ul className="list-disc list-inside space-y-1 text-sm text-text">
              {screening.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
        {/* OFFICER DECISION BANNER IF RECORDED */}
        {screening.officer_action && (
          <div className="section bg-surface p-4 rounded-sm border border-line space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-widest text-muted">
                Recorded Officer Decision
              </span>
              <StatusBadge
                status={screening.officer_action === "CLEAR" ? "ACCEPTED" : screening.officer_action === "REJECT" ? "REJECTED" : "REVIEW_REQUIRED"}
                label={screening.officer_action}
              />
            </div>
            <div className="text-xs text-text space-y-1">
              <div>
                <span className="text-muted">Officer ID:</span>{" "}
                <span className="font-mono">{screening.decided_by || "OFFICER"}</span>
                {screening.decided_at && (
                  <span className="text-muted ml-3">
                    Decided at: {new Date(screening.decided_at).toLocaleString()}
                  </span>
                )}
              </div>
              {screening.officer_notes && (
                <div>
                  <span className="text-muted">Officer Notes:</span> {screening.officer_notes}
                </div>
              )}
            </div>
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
            onClick={() => setShowDecisionModal(true)}
            className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 transition-opacity"
          >
            {screening.officer_action ? "Update Action" : "Officer Decision"}
          </button>
        </div>
      </div>

      {/* Evidence Modal Drawer */}
      {showEvidenceModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-surface border border-line max-w-xl w-full p-6 rounded-sm space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-text">
                Structured Evidence • {screening.id}
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
                  No evidence flags generated yet. All checks passed cleanly.
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

      {/* Manual Officer Decision Modal */}
      {showDecisionModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-surface border border-line max-w-md w-full p-6 rounded-sm space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-text">
                  Officer Manual Decision
                </h3>
                <span className="text-[11px] font-mono text-muted">
                  Session: {screening.id}
                </span>
              </div>
              <button
                onClick={() => setShowDecisionModal(false)}
                className="text-muted hover:text-text text-sm font-mono"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleDecisionSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1">
                  Determination Action
                </label>
                <select
                  value={decisionAction}
                  onChange={(e) => setDecisionAction(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-bg border border-line rounded-sm text-text font-semibold"
                >
                  <option value="CLEAR">CLEAR (Allow Entry / Cleared)</option>
                  <option value="REFER_SECONDARY">REFER_SECONDARY (Secondary Inspection)</option>
                  <option value="REJECT">REJECT (Deny Clearance / Revoke)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1">
                  Officer Badge / ID
                </label>
                <input
                  type="text"
                  value={decidedBy}
                  onChange={(e) => setDecidedBy(e.target.value)}
                  placeholder="OFFICER-4412"
                  required
                  className="w-full px-3 py-1.5 text-xs bg-bg border border-line rounded-sm font-mono text-text"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1">
                  Decision Justification & Notes
                </label>
                <textarea
                  value={decisionNotes}
                  onChange={(e) => setDecisionNotes(e.target.value)}
                  rows={3}
                  placeholder="Record officer observation, secondary referral reason, or physical inspection notes..."
                  className="w-full px-3 py-1.5 text-xs bg-bg border border-line rounded-sm text-text"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-line">
                <button
                  type="button"
                  onClick={() => setShowDecisionModal(false)}
                  className="px-4 py-2 border border-line bg-surface text-xs font-semibold uppercase tracking-wider text-text rounded-sm hover:bg-bg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingDecision}
                  className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 disabled:opacity-50"
                >
                  {submittingDecision ? "Recording..." : "Confirm Decision"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
