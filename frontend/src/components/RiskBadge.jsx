import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function RiskBadge({ level = 'LOW', score = 0, showScore = true, className = '' }) {
  const norm = (level || 'LOW').toUpperCase();

  if (norm === 'HIGH') {
    return (
      <span
        title={`Advisory Fraud Signal: High Risk (Score ${score}/100)`}
        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300 shadow-xs ${className}`}
      >
        <ShieldAlert className="w-3.5 h-3.5 mr-1 text-rose-600 shrink-0" />
        <span>High Risk</span>
        {showScore && <span className="ml-1 px-1.5 py-0.2 rounded bg-rose-200 text-rose-900 font-mono text-[10px]">{score}</span>}
      </span>
    );
  }

  if (norm === 'MEDIUM') {
    return (
      <span
        title={`Advisory Fraud Signal: Medium Risk (Score ${score}/100)`}
        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs ${className}`}
      >
        <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600 shrink-0" />
        <span>Med Risk</span>
        {showScore && <span className="ml-1 px-1.5 py-0.2 rounded bg-amber-200 text-amber-900 font-mono text-[10px]">{score}</span>}
      </span>
    );
  }

  return (
    <span
      title={`Automated Fraud Scan: Low Risk / Clean (Score ${score}/100)`}
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 ${className}`}
    >
      <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-600 shrink-0" />
      <span>Low / Clean</span>
      {showScore && <span className="ml-1 px-1.5 py-0.2 rounded bg-emerald-200 text-emerald-900 font-mono text-[10px]">{score}</span>}
    </span>
  );
}
