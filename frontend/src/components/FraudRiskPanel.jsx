import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck, Info, FileWarning, ArrowRight, ExternalLink } from 'lucide-react';
import RiskBadge from './RiskBadge';

export default function FraudRiskPanel({ riskAssessment, riskLevel, riskScore }) {
  const assessment = riskAssessment || {};
  const flags = assessment.flags || [];
  const level = (riskLevel || assessment.risk_level || 'LOW').toUpperCase();
  const score = Math.round(riskScore || assessment.risk_score || 0);

  const isHigh = level === 'HIGH';
  const isMed = level === 'MEDIUM';

  // Color theme
  const borderClass = isHigh ? 'border-rose-300 bg-rose-50/40' : isMed ? 'border-amber-300 bg-amber-50/40' : 'border-emerald-300 bg-emerald-50/30';
  const headerBg = isHigh ? 'bg-rose-100/80 text-rose-950' : isMed ? 'bg-amber-100/80 text-amber-950' : 'bg-emerald-100/80 text-emerald-950';

  return (
    <div className={`rounded-2xl border ${borderClass} shadow-sm overflow-hidden text-xs transition-all`}>
      {/* Panel Header */}
      <div className={`px-5 py-3.5 border-b flex flex-col sm:flex-row sm:items-center justify-between gap-2 ${headerBg}`}>
        <div className="flex items-center space-x-2.5">
          {isHigh ? (
            <ShieldAlert className="w-5 h-5 text-rose-700 shrink-0 animate-pulse" />
          ) : isMed ? (
            <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0" />
          ) : (
            <ShieldCheck className="w-5 h-5 text-emerald-700 shrink-0" />
          )}
          <div>
            <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
              <span>Automated Duplicate & Fraud Risk Evaluation</span>
              <RiskBadge level={level} score={score} />
            </h3>
            <p className="text-[11px] text-slate-600">
              Cross-application intelligence analyzing ST certificate uniqueness, identity collision, and bank diversion.
            </p>
          </div>
        </div>

        {/* Risk Score Progress Bar */}
        <div className="flex items-center space-x-3 self-end sm:self-center">
          <div className="text-right">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Risk Score</span>
            <span className="font-mono font-extrabold text-sm text-slate-900">{score} / 100</span>
          </div>
          <div className="w-24 h-2.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                isHigh ? 'bg-rose-600' : isMed ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(score, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Advisory Notice Disclaimer */}
      <div className="px-5 py-2 bg-slate-50 border-b border-slate-200/60 flex items-center justify-between text-[11px] text-slate-500">
        <div className="flex items-center space-x-1.5">
          <Info className="w-3.5 h-3.5 text-blue-600 shrink-0" />
          <span className="font-semibold text-slate-700">
            ADVISORY SIGNAL FOR HUMAN REVIEW:
          </span>
          <span>
            {assessment.disclaimer || 'Automated findings highlight anomalies for scrutiny officers; final approval remains with the committee.'}
          </span>
        </div>
        {assessment.evaluated_at && (
          <span className="text-[10px] text-slate-400 font-mono hidden md:inline">
            Evaluated: {new Date(assessment.evaluated_at).toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* Flags List or Clean State */}
      <div className="p-5 space-y-3">
        {flags.length > 0 ? (
          <div className="space-y-2.5">
            {flags.map((flag, idx) => {
              const flagHigh = flag.severity === 'HIGH';
              const flagMed = flag.severity === 'MEDIUM';

              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border transition-all ${
                    flagHigh
                      ? 'bg-rose-50/80 border-rose-200 text-rose-950'
                      : flagMed
                      ? 'bg-amber-50/80 border-amber-200 text-amber-950'
                      : 'bg-blue-50/60 border-blue-200 text-blue-950'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start space-x-2">
                      <FileWarning className={`w-4 h-4 mt-0.5 shrink-0 ${
                        flagHigh ? 'text-rose-600' : flagMed ? 'text-amber-600' : 'text-blue-600'
                      }`} />
                      <div>
                        <span className="font-bold text-xs block">{flag.flag_name}</span>
                        <p className="text-[11px] text-slate-700 mt-0.5 leading-relaxed">{flag.description}</p>

                        {/* Evidence Key-Value Pairs */}
                        {flag.evidence && Object.keys(flag.evidence).length > 0 && (
                          <div className="mt-2 pt-2 border-t border-slate-200/60 flex flex-wrap gap-2 text-[11px]">
                            {Object.entries(flag.evidence).map(([k, v]) => (
                              <span
                                key={k}
                                className="px-2 py-0.5 rounded bg-white/80 border border-slate-200 font-mono text-[10px] text-slate-800"
                              >
                                <strong>{k.replace(/_/g, ' ')}:</strong>{' '}
                                {Array.isArray(v) ? v.join(', ') : typeof v === 'object' ? JSON.stringify(v) : String(v)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase tracking-wider shrink-0 ${
                      flagHigh ? 'bg-rose-200 text-rose-900' : flagMed ? 'bg-amber-200 text-amber-900' : 'bg-blue-200 text-blue-900'
                    }`}>
                      +{flag.points} pts
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-white border border-emerald-200 flex items-center space-x-3">
            <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
            <div>
              <span className="font-bold text-emerald-900 text-xs block">
                No Fraud or Duplicate Identity Collisions Detected
              </span>
              <p className="text-[11px] text-emerald-700 mt-0.5">
                ST Certificate number, applicant identity, Aadhaar/DigiLocker records, and DBT bank account pass all automated cross-checks.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
