import React from 'react';
import { CheckCircle, AlertTriangle, Clock, XCircle, Award, FileSearch, HelpCircle } from 'lucide-react';

export default function StatusBadge({ status, className = '' }) {
  const norm = (status || '').toLowerCase();

  if (norm === 'verified' || norm === 'approved') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 ${className}`}>
        <CheckCircle className="w-3.5 h-3.5 mr-1 text-emerald-600" />
        Verified
      </span>
    );
  }

  if (norm === 'needs review' || norm === 'flagged' || norm === 'deficient') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 ${className}`}>
        <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" />
        Needs Review
      </span>
    );
  }

  if (norm === 'missing/unreadable' || norm === 'unreadable' || norm === 'rejected') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300 ${className}`}>
        <XCircle className="w-3.5 h-3.5 mr-1 text-rose-600" />
        {status || 'Rejected'}
      </span>
    );
  }

  if (norm === 'selected') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300 ${className}`}>
        <Award className="w-3.5 h-3.5 mr-1 text-blue-600" />
        Selected Scholar
      </span>
    );
  }

  if (norm === 'scrutiny' || norm === 'under scrutiny') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-300 ${className}`}>
        <FileSearch className="w-3.5 h-3.5 mr-1 text-purple-600" />
        Under Scrutiny
      </span>
    );
  }

  if (norm === 'under verification') {
    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-300 ${className}`}>
        <Clock className="w-3.5 h-3.5 mr-1 text-indigo-600 animate-spin" />
        Under Verification
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-300 ${className}`}>
      <Clock className="w-3.5 h-3.5 mr-1 text-slate-500" />
      {status || 'Submitted'}
    </span>
  );
}
