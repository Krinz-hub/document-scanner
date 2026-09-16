import React from "react";

export type StatusType =
  | "VALID"
  | "PASS"
  | "MATCH"
  | "CLEAN"
  | "COMPLETED"
  | "REVIEW"
  | "REVIEW_REQUIRED"
  | "SUSPICIOUS"
  | "FLAG"
  | "WARNING"
  | "INVALID"
  | "FAIL"
  | "REJECTED"
  | "LOW_SIMILARITY"
  | "PENDING"
  | "PROCESSING"
  | "UNAVAILABLE"
  | "INSUFFICIENT_EVIDENCE"
  | "LOW_IMAGE_QUALITY"
  | "LOW"
  | "MEDIUM"
  | "HIGH";

interface StatusBadgeProps {
  status: string;
  label?: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, className = "" }) => {
  const norm = (status || "").toUpperCase();

  let dotColor = "bg-muted";
  let textColor = "text-muted";

  if (["VALID", "PASS", "MATCH", "CLEAN", "COMPLETED", "LOW"].includes(norm)) {
    dotColor = "bg-success";
    textColor = "text-success";
  } else if (["REVIEW", "REVIEW_REQUIRED", "SUSPICIOUS", "FLAG", "WARNING", "MEDIUM"].includes(norm)) {
    dotColor = "bg-warning";
    textColor = "text-warning";
  } else if (["INVALID", "FAIL", "REJECTED", "LOW_SIMILARITY", "HIGH"].includes(norm)) {
    dotColor = "bg-danger";
    textColor = "text-danger";
  }

  const displayLabel = label || status.replace(/_/g, " ");

  return (
    <span
      className={`inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider ${textColor} ${className}`}
    >
      <span className={`w-2 h-2 rounded-full shrink-0 ${dotColor}`} />
      <span>{displayLabel}</span>
    </span>
  );
};
