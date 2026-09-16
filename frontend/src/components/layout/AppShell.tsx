import React from "react";
import Link from "next/link";

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-bg text-text flex flex-col">
      {/* Top Operational Workstation Bar */}
      <header className="border-b border-line bg-surface sticky top-0 z-30">
        <div className="page-container !py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 bg-text rounded-xs shrink-0" />
              <span className="text-sm font-bold tracking-widest uppercase text-text">
                Border Document Screening
              </span>
            </Link>
            <div className="h-4 w-px bg-line hidden sm:block" />
            <span className="text-xs font-mono text-muted uppercase hidden sm:inline-block">
              Decision Support System • Station CP-01
            </span>
          </div>

          <nav className="flex items-center gap-4">
            <Link
              href="/"
              className="text-xs font-semibold uppercase tracking-wider text-muted hover:text-text transition-colors"
            >
              Screenings
            </Link>
            <Link
              href="/screenings/new"
              className="text-xs font-semibold uppercase tracking-wider px-3 py-1.5 bg-text text-surface rounded-sm hover:opacity-90 transition-opacity"
            >
              + New Screening
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Operational Viewport */}
      <main className="flex-1 page-container">
        {children}
      </main>

      {/* Operational Footer */}
      <footer className="border-t border-line py-4 text-center text-xs text-muted">
        Border Document Screening Platform • Human-in-the-Loop Operational Workstation
      </footer>
    </div>
  );
};
