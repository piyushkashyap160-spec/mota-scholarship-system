import React from 'react';
import { CheckCircle2, Clock, XCircle, AlertTriangle, Award, FileSearch, Send, ArrowRight } from 'lucide-react';

export default function Timeline({ status, timelineLogs = [], disbursementStatus, disbursementAmount }) {
  const stages = [
    { key: 'Submitted', label: '1. Submitted', desc: 'Application & Docs Received' },
    { key: 'Under Verification', label: '2. AI Verification', desc: 'Tesseract OCR Cross-Check' },
    { key: 'Scrutiny', label: '3. Scrutiny Desk', desc: 'Officer Evaluation' },
    { key: 'Selected', label: '4. Selection & Award', desc: 'Sanction Committee Decision' },
    { key: 'Post-Selection', label: '5. Post-Selection', desc: 'DBT Direct Benefit Transfer' }
  ];

  const getStageIndex = (currentStatus) => {
    const s = (currentStatus || '').toLowerCase();
    if (s === 'submitted') return 0;
    if (s === 'under verification') return 1;
    if (s === 'needs review') return 1; // blocked at verification
    if (s === 'scrutiny') return 2;
    if (s === 'selected') return 3;
    if (s === 'post-selection') return 4;
    if (s === 'rejected') return 3;
    return 0;
  };

  const currentIndex = getStageIndex(status);
  const isRejected = (status || '').toLowerCase() === 'rejected';
  const isNeedsReview = (status || '').toLowerCase() === 'needs review';

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider mb-6 flex items-center justify-between">
        <span>Application Lifecycle & Status Timeline</span>
        <span className="text-xs font-normal normal-case text-slate-500">
          Real-time tracking for MoTA Scholars
        </span>
      </h3>

      {/* 5-Step Visual Progress Bar */}
      <div className="relative mb-8">
        <div className="hidden sm:block absolute top-5 left-8 right-8 h-1 bg-slate-200 -z-0">
          <div
            className={`h-1 transition-all duration-500 ${isRejected ? 'bg-rose-500' : 'bg-gov-navy'}`}
            style={{ width: `${Math.min(currentIndex * 25, 100)}%` }}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 relative z-10">
          {stages.map((stage, idx) => {
            const isCompleted = idx < currentIndex;
            const isCurrent = idx === currentIndex;
            const isFuture = idx > currentIndex;

            let icon = <Clock className="w-5 h-5 text-slate-400" />;
            let circleBg = 'bg-slate-100 text-slate-500 border-slate-300';

            if (isCompleted) {
              icon = <CheckCircle2 className="w-5 h-5 text-white" />;
              circleBg = 'bg-emerald-600 text-white border-emerald-600 shadow-sm';
            } else if (isCurrent) {
              if (isRejected && stage.key === 'Selected') {
                icon = <XCircle className="w-5 h-5 text-white" />;
                circleBg = 'bg-rose-600 text-white border-rose-600 shadow-md animate-pulse';
              } else if (isNeedsReview) {
                icon = <AlertTriangle className="w-5 h-5 text-white" />;
                circleBg = 'bg-amber-500 text-white border-amber-500 shadow-md animate-bounce';
              } else {
                icon = <Clock className="w-5 h-5 text-white" />;
                circleBg = 'bg-gov-navy text-white border-gov-navy shadow-md ring-4 ring-blue-100';
              }
            }

            return (
              <div key={stage.key} className="flex sm:flex-col items-center sm:text-center space-x-3 sm:space-x-0">
                <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all ${circleBg}`}>
                  {icon}
                </div>
                <div className="mt-2 text-left sm:text-center">
                  <p className={`text-xs font-bold ${isCurrent ? 'text-gov-navy' : isCompleted ? 'text-slate-800' : 'text-slate-400'}`}>
                    {stage.label}
                  </p>
                  <p className="text-[11px] text-slate-500 hidden sm:block">{stage.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Post Selection Banner (if applicable) */}
      {(disbursementStatus || disbursementAmount > 0) && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-emerald-600 text-white rounded-lg">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs uppercase font-bold text-emerald-800">PFMS / DBT Direct Benefit Status</span>
              <p className="text-sm font-bold text-emerald-950">{disbursementStatus}</p>
            </div>
          </div>
          {disbursementAmount > 0 && (
            <div className="text-right">
              <span className="text-xs text-emerald-700 font-medium">Sanctioned Fellowship Amount</span>
              <p className="text-base font-extrabold text-emerald-900">
                ₹ {disbursementAmount.toLocaleString('en-IN')}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Detailed Activity Log History */}
      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
          Activity & Audit Log History
        </h4>
        <div className="space-y-3">
          {timelineLogs && timelineLogs.length > 0 ? (
            timelineLogs.map((log, idx) => (
              <div key={idx} className="flex items-start space-x-3 p-3 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                <div className="w-2 h-2 rounded-full bg-gov-navy mt-1.5 flex-shrink-0" />
                <div className="flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between">
                    <span className="font-bold text-slate-800">{log.action}</span>
                    <span className="text-[11px] text-slate-400">
                      {new Date(log.created_at).toLocaleString('en-IN')}
                    </span>
                  </div>
                  <p className="text-slate-600 mt-0.5">{log.remarks}</p>
                  <span className="text-[10px] font-medium text-slate-400">By: {log.actor} • Stage: {log.stage}</span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-400">No activity logs recorded yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
