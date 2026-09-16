"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import Link from "next/link";

export default function NewScreeningPage() {
  const router = useRouter();
  const [checkpointId, setCheckpointId] = useState("CP-TERMINAL-1");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const screening = await api.createScreening(checkpointId);
      router.push(`/screenings/${screening.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create screening session");
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-8">
      <div className="mb-6">
        <Link
          href="/"
          className="text-xs font-semibold uppercase tracking-wider text-muted hover:text-text transition-colors"
        >
          ← Back to Screening Queue
        </Link>
        <h1 className="text-xl font-bold tracking-tight text-text mt-2">
          Initialize Screening Session
        </h1>
        <p className="text-xs text-muted mt-1">
          Select workstation checkpoint identifier to begin traveler document intake.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-3 bg-danger/10 border border-danger/30 text-danger text-xs rounded-sm">
          <strong>Initialization Error:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border border-line bg-surface p-6 rounded-sm space-y-5">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2">
            Checkpoint / Workstation Identifier
          </label>
          <input
            type="text"
            value={checkpointId}
            onChange={(e) => setCheckpointId(e.target.value)}
            required
            className="w-full px-3 py-2 text-sm bg-bg border border-line rounded-sm focus:outline-hidden focus:border-text font-mono"
            placeholder="e.g. CP-TERMINAL-1"
          />
        </div>

        <div className="pt-2 flex items-center justify-end gap-3">
          <Link
            href="/"
            className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-muted hover:text-text"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {isLoading ? "Creating..." : "Create Session →"}
          </button>
        </div>
      </form>
    </div>
  );
}
