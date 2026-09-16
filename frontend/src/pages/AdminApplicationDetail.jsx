import React, { useState, useEffect } from 'react';
import { ArrowLeft, CheckCircle2, XCircle, AlertTriangle, Shield, User, FileText, Send, Award, Clock, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import SideBySideOcrViewer from '../components/SideBySideOcrViewer';
import Timeline from '../components/Timeline';
import FraudRiskPanel from '../components/FraudRiskPanel';
import AuditLedgerViewer from '../components/AuditLedgerViewer';

export default function AdminApplicationDetail({ applicationId, onBack, onActionComplete }) {
  const [app, setApp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionModal, setActionModal] = useState(null); // 'approve', 'reject', 'request_resubmission'
  const [remarks, setRemarks] = useState('');
  const [selectedDocId, setSelectedDocId] = useState('');
  const [submittingAction, setSubmittingAction] = useState(false);

  const loadDetail = async () => {
    try {
      const data = await api.admin.getApplicationDetail(applicationId);
      setApp(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetail();
  }, [applicationId]);

  const handleExecuteAction = async () => {
    if (!actionModal) return;
    setSubmittingAction(true);
    try {
      const doc = app.documents?.find((d) => String(d.id) === String(selectedDocId));
      await api.admin.takeAction(applicationId, {
        action: actionModal,
        remarks: remarks || (actionModal === 'approve' ? 'Approved by Scrutiny Committee' : 'Action taken by Desk Officer'),
        document_id: selectedDocId ? parseInt(selectedDocId) : (app.documents[0]?.id || null),
        doc_type: doc ? doc.doc_type : 'general_scrutiny',
      });
      setActionModal(null);
      setRemarks('');
      await loadDetail();
      if (onActionComplete) onActionComplete();
    } catch (err) {
      alert(err.message || 'Failed to record administrative action');
    } finally {
      setSubmittingAction(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-500">Loading application scrutiny workspace...</div>;
  }

  if (!app) {
    return <div className="py-12 text-center text-rose-500">Application not found.</div>;
  }

  const fd = app.form_data || {};
  const isEligible = app.eligibility_passed;

  return (
    <div className="space-y-6 pb-16">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="px-3 py-1.5 text-xs font-bold text-gov-navy hover:bg-slate-100 rounded-lg flex items-center space-x-1 border border-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scrutiny Table</span>
        </button>

        <div className="flex items-center space-x-3">
          <span className="text-xs font-medium text-slate-500">Current Status:</span>
          <StatusBadge status={app.status} />
        </div>
      </div>

      {/* Candidate Overview Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div className="flex items-start space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-gov-navy text-white flex items-center justify-center font-extrabold text-xl shadow flex-shrink-0">
              {app.applicant?.full_name?.charAt(0) || 'S'}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold text-slate-900">{app.applicant?.full_name}</h1>
                <span className="text-xs px-2 py-0.5 rounded font-mono font-bold bg-slate-100 text-gov-navy">
                  {app.application_number}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Scheme: <strong className="text-gov-navy">{app.scheme?.name}</strong> • State: <strong className="text-slate-700">{app.applicant?.state || fd.state}</strong> • Tribe: <strong className="text-slate-700">{app.applicant?.community_tribe || fd.community_tribe}</strong>
              </p>
            </div>
          </div>

          {/* Action Bar (Top Quick Access) */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => { setActionModal('approve'); setRemarks('All documents and eligibility criteria verified. Approved for fellowship award.'); }}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow transition-colors flex items-center space-x-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Approve & Award</span>
            </button>
            <button
              onClick={() => { setActionModal('request_resubmission'); setRemarks(''); }}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold shadow transition-colors flex items-center space-x-1.5"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Flag Deficiency</span>
            </button>
            <button
              onClick={() => { setActionModal('reject'); setRemarks('Application does not satisfy scheme requirements.'); }}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow transition-colors flex items-center space-x-1.5"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Reject</span>
            </button>
          </div>
        </div>

        {/* Key Applicant Facts Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-5 text-xs">
          <div>
            <span className="text-slate-400 uppercase font-bold text-[10px] block">ST Certificate No.</span>
            <span className="font-mono font-bold text-slate-800">{app.applicant?.st_cert_number || fd.st_cert_number}</span>
          </div>
          <div>
            <span className="text-slate-400 uppercase font-bold text-[10px] block">Annual Family Income</span>
            <span className="font-mono font-bold text-slate-800">
              ₹ {parseFloat(fd.annual_income || 0).toLocaleString('en-IN')}
            </span>
          </div>
          <div>
            <span className="text-slate-400 uppercase font-bold text-[10px] block">Qualifying Academic Marks</span>
            <span className="font-mono font-bold text-slate-800">{fd.marks_percentage}%</span>
          </div>
          <div>
            <span className="text-slate-400 uppercase font-bold text-[10px] block">Calculated Merit Score</span>
            <span className="font-mono font-extrabold text-gov-navy text-sm">
              {app.calculated_merit_score || 75.0} / 100
            </span>
          </div>
        </div>
      </div>

      {/* AUTOMATED FRAUD & DUPLICATE RISK EVALUATION */}
      <FraudRiskPanel
        riskAssessment={app.risk_assessment}
        riskLevel={app.risk_level}
        riskScore={app.risk_score}
      />

      {/* AUTOMATED SCHEME ELIGIBILITY EVALUATION RESULT */}
      <div className={`rounded-2xl border p-5 shadow-sm text-xs ${
        isEligible ? 'bg-emerald-50/60 border-emerald-200' : 'bg-rose-50/60 border-rose-200'
      }`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Shield className={`w-5 h-5 ${isEligible ? 'text-emerald-700' : 'text-rose-700'}`} />
            <h3 className="font-bold text-sm text-slate-900">
              Rule Engine Automated Eligibility Audit
            </h3>
          </div>
          <span className={`px-2.5 py-0.5 rounded-full font-bold text-xs ${
            isEligible ? 'bg-emerald-200 text-emerald-900' : 'bg-rose-200 text-rose-900'
          }`}>
            {isEligible ? 'Fully Eligible under Scheme Guidelines' : 'Ineligibility Breach Detected'}
          </span>
        </div>

        <ul className="space-y-1.5 pl-6 list-disc">
          {app.eligibility_notes?.map((n, i) => (
            <li key={i} className={n.startsWith('Ineligible') ? 'text-rose-700 font-bold' : 'text-emerald-800 font-medium'}>
              {n}
            </li>
          ))}
        </ul>
      </div>

      {/* CORE SCRUTINY: SIDE-BY-SIDE OCR VIEWER */}
      <section className="space-y-2">
        <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider">
          Side-by-Side OCR Verification Matrix & Evidence
        </h3>
        <SideBySideOcrViewer documents={app.documents} readOnly={false} />
      </section>

      {/* LIFECYCLE & AUDIT TIMELINE */}
      <Timeline
        status={app.status}
        timelineLogs={app.timeline_logs}
        disbursementStatus={app.disbursement_status}
        disbursementAmount={app.disbursement_amount}
      />

      {/* IMMUTABLE CRYPTOGRAPHIC AUDIT LEDGER */}
      <AuditLedgerViewer
        applicationId={app.id}
        applicationNumber={app.application_number}
      />

      {/* ACTION DIALOG MODAL */}
      {actionModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
                {actionModal === 'approve' && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
                {actionModal === 'request_resubmission' && <AlertTriangle className="w-5 h-5 text-amber-600" />}
                {actionModal === 'reject' && <XCircle className="w-5 h-5 text-rose-600" />}
                <span className="capitalize">
                  {actionModal === 'request_resubmission' ? 'Raise Deficiency Notice' : `${actionModal} Application`}
                </span>
              </h3>
            </div>

            {actionModal === 'request_resubmission' && (
              <div className="mb-4">
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Target Deficient Document
                </label>
                <select
                  value={selectedDocId}
                  onChange={(e) => setSelectedDocId(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs bg-white text-slate-800"
                >
                  <option value="">-- Choose Flagged Document --</option>
                  {app.documents?.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.doc_type?.replace(/_/g, ' ').toUpperCase()} ({d.status})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                {actionModal === 'request_resubmission' ? 'Deficiency Remarks (Sent to Applicant)' : 'Official Scrutiny Remarks'}
              </label>
              <textarea
                rows={4}
                required
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Specify precise feedback, required rectification, or committee rationale..."
                className="w-full p-3 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
              />
            </div>

            {/* Quick Templates for Fast Demo */}
            {actionModal === 'request_resubmission' && (
              <div className="mb-4">
                <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1.5">Quick Remark Templates:</span>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    type="button"
                    onClick={() => setRemarks('Uploaded document is low resolution/blurry and official seal is unreadable. Please upload a clear high-res scan.')}
                    className="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded"
                  >
                    Blurry Stamp / Low Res
                  </button>
                  <button
                    type="button"
                    onClick={() => setRemarks('Income Certificate must be valid for the current Financial Year 2024-25. Please upload latest certificate issued by Tehsildar.')}
                    className="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded"
                  >
                    Outdated Income Cert
                  </button>
                  <button
                    type="button"
                    onClick={() => setRemarks('Candidate name on ST Certificate has minor spelling difference from matriculation record. Please submit SDM affidavit.')}
                    className="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded"
                  >
                    Name Discrepancy
                  </button>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setActionModal(null)}
                className="px-4 py-2 border border-slate-300 text-slate-700 text-xs font-bold rounded-lg hover:bg-slate-100"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={submittingAction}
                onClick={handleExecuteAction}
                className={`px-6 py-2 text-white font-bold rounded-lg text-xs shadow ${
                  actionModal === 'approve'
                    ? 'bg-emerald-600 hover:bg-emerald-700'
                    : actionModal === 'request_resubmission'
                    ? 'bg-amber-600 hover:bg-amber-700'
                    : 'bg-rose-600 hover:bg-rose-700'
                }`}
              >
                {submittingAction ? 'Processing...' : 'Confirm Decision'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
