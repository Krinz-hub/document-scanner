import React from "react";

interface DataRowProps {
  label: string;
  value?: React.ReactNode;
  children?: React.ReactNode;
  hint?: string;
  className?: string;
}

export const DataRow: React.FC<DataRowProps> = ({
  label,
  value,
  children,
  hint,
  className = "",
}) => {
  return (
    <div className={`data-row ${className}`}>
      <div className="flex flex-col">
        <span className="text-sm font-medium text-muted uppercase tracking-wider">{label}</span>
        {hint && <span className="text-xs text-muted/70">{hint}</span>}
      </div>
      <div className="text-sm text-text font-mono flex items-center gap-2">
        {value !== undefined ? value : children}
      </div>
    </div>
  );
};
