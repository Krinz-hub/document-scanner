"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ScreeningSummary } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function HomePage() {
  const [screenings, setScreenings] = useState<ScreeningSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchScreenings();
  }, []);

  const fetchScreenings = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listScreenings();
      setScreenings(data);
    } catch (err: any) {
      setError(err.message || "Failed to load screenings from server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-line pb-6">
        <div>
          <span className="text-xs font-mono uppercase tracking-widest text-muted">
            Inspection Operations
          </span>
          <h1 className="text-2xl font-bold tracking-tight text-text">Screening Queue</h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchScreenings}
            disabled={loading}
            className="px-3 py-2 border border-line bg-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:bg-bg transition-colors disabled:opacity-50"
          >
            {loading ? "Refreshing..." : "↻ Refresh"}
          </button>
          <Link
            href="/screenings/new"
            className="inline-flex items-center justify-center px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm hover:opacity-90 transition-opacity"
          >
            + Start Screening Session
          </Link>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="p-4 bg-danger/10 border border-danger/30 text-danger text-xs rounded-sm flex items-center justify-between">
          <div>
            <strong>Backend Connection Notice:</strong> {error}
          </div>
          <button
            onClick={fetchScreenings}
            className="px-3 py-1 bg-danger text-surface font-semibold rounded-xs uppercase tracking-wider text-[10px]"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && !error && (
        <div className="border border-line bg-surface rounded-sm p-6 space-y-4">
          <div className="h-4 w-48 bg-line animate-pulse rounded-xs" />
          <div className="h-10 w-full bg-line/60 animate-pulse rounded-xs" />
          <div className="h-10 w-full bg-line/60 animate-pulse rounded-xs" />
          <div className="h-10 w-full bg-line/60 animate-pulse rounded-xs" />
        </div>
      )}

      {/* Screenings Table / List */}
      {!loading && !error && (
        <div className="border border-line bg-surface rounded-sm overflow-hidden">
          {screenings.length === 0 ? (
            /* Empty State */
            <div className="p-12 text-center space-y-3">
              <span className="w-8 h-8 rounded-full bg-line inline-flex items-center justify-center text-muted text-sm font-mono">
                0
              </span>
              <h3 className="text-sm font-bold uppercase tracking-wider text-text">
                No Screenings in Queue
              </h3>
              <p className="text-xs text-muted max-w-sm mx-auto">
                There are no active or completed screening sessions recorded yet. Start a new
                inspection session to begin document screening.
              </p>
              <div className="pt-2">
                <Link
                  href="/screenings/new"
                  className="inline-block px-4 py-2 bg-text text-surface text-xs font-semibold uppercase tracking-wider rounded-sm"
                >
                  + Start First Screening
                </Link>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-line bg-bg font-semibold text-muted uppercase tracking-wider">
                    <th className="py-3 px-4">Screening ID</th>
                    <th className="py-3 px-4">Checkpoint</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Review Priority</th>
                    <th className="py-3 px-4">Created At</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {screenings.map((s) => (
                    <tr key={s.id} className="hover:bg-bg/50 transition-colors">
                      <td className="py-3 px-4 font-mono font-medium text-text">
                        <Link href={`/screenings/${s.id}`} className="hover:underline">
                          {s.id}
                        </Link>
                      </td>
                      <td className="py-3 px-4 font-mono text-muted">{s.checkpoint_id}</td>
                      <td className="py-3 px-4">
                        <StatusBadge status={s.status} />
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={s.review_priority} />
                      </td>
                      <td className="py-3 px-4 font-mono text-muted">
                        {new Date(s.created_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          href={`/screenings/${s.id}`}
                          className="inline-block px-3 py-1 bg-text text-surface font-semibold uppercase tracking-wider text-[11px] rounded-sm hover:opacity-90 transition-opacity"
                        >
                          Inspect →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
