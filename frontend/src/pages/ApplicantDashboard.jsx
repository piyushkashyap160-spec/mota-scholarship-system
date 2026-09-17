import React, { useState, useEffect } from 'react';
import { Award, AlertTriangle, CheckCircle2, Clock, Upload, ArrowRight, RefreshCw, FileText, User, ChevronRight, X, ShieldAlert, IndianRupee } from 'lucide-react';
import { api } from '../api/client';
import Timeline from '../components/Timeline';
import StatusBadge from '../components/StatusBadge';
import SideBySideOcrViewer from '../components/SideBySideOcrViewer';
import PfmsDisbursementModal from '../components/PfmsDisbursementModal';
import RenewalModal from '../components/RenewalModal';

export default function ApplicantDashboard({ currentUser, onNavigateApply }) {
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState(null);
  const [loading, setLoading] = useState(true);
  const [resubmitModal, setResubmitModal] = useState(null); // deficiency object
  const [resubmitting, setResubmitting] = useState(false);
  const [resubmitMsg, setResubmitMsg] = useState(null);
  const [showPfmsModal, setShowPfmsModal] = useState(false);
  const [showRenewalModal, setShowRenewalModal] = useState(false);

  const loadApplications = async () => {
    try {
      const data = await api.applications.getMy();
      setApplications(data);
      if (data.length > 0) {
        // Load detailed view for first application
        const detail = await api.applications.getDetail(data[0].id);
        setSelectedApp(detail);
      }
    } catch (err) {
      console.error('Failed to load my applications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, [currentUser?.id]);

  const handleSelectApplication = async (appId) => {
    try {
      const detail = await api.applications.getDetail(appId);
      setSelectedApp(detail);
    } catch (err) {
      console.error(err);
    }
  };

  const handleResubmitDocument = async (deficiency) => {
    setResubmitting(true);
    try {
      await api.applications.resubmit(selectedApp.id, {
        deficiency_id: deficiency.id,
        file_name: `rectified_${deficiency.doc_type}.pdf`,
      });
      setResubmitMsg('Rectified document submitted successfully! Scrutiny Officer has been notified.');
      setTimeout(() => {
        setResubmitModal(null);
        setResubmitMsg(null);
        loadApplications();
      }, 1500);
    } catch (err) {
      alert(err.message || 'Resubmission failed');
    } finally {
      setResubmitting(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-500">Loading your scholarship applications...</div>;
  }

  const openDeficiencies = selectedApp?.deficiencies?.filter((d) => d.status === 'Open') || [];
  const hasPendingRenewal = applications.some(
    (a) => a.parent_application_id === selectedApp?.id && a.status === 'Renewal - Under Review'
  );
  const isRenewalDue = selectedApp?.status === 'Selected' && selectedApp?.renewal_due_date;

  return (
    <div className="space-y-8 pb-16">
      {/* Top Profile Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-gov-navy text-white flex items-center justify-center font-extrabold text-xl shadow">
            {currentUser?.full_name?.charAt(0) || 'S'}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-gov-navy">{currentUser?.full_name}</h2>
              <span className="text-xs px-2 py-0.5 rounded font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                Verified ST Candidate
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Tribe: <strong className="text-slate-700">{currentUser?.community_tribe || 'Santhal'}</strong> • State: <strong className="text-slate-700">{currentUser?.state || 'Jharkhand'}</strong> • ST Cert: <strong className="font-mono text-slate-700">{currentUser?.st_cert_number || 'ST/JH/2023/1029'}</strong>
            </p>
          </div>
        </div>

        <button
          onClick={onNavigateApply}
          className="px-4 py-2.5 bg-gov-navy hover:bg-blue-900 text-white rounded-xl text-xs font-bold transition-colors flex items-center space-x-2 shadow self-start sm:self-center"
        >
          <span>Apply for New Scheme</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Applications Selector Tabs */}
      {applications.length > 1 && (
        <div className="flex space-x-2 overflow-x-auto pb-1">
          {applications.map((app) => (
            <button
              key={app.id}
              onClick={() => handleSelectApplication(app.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                selectedApp?.id === app.id
                  ? 'bg-gov-navy text-white shadow'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <span>
                {app.parent_application_id
                  ? `${app.scheme?.code || 'Scheme'} - Year Continuation Renewal`
                  : app.application_number}
              </span>
              <StatusBadge status={app.status} />
            </button>
          ))}
        </div>
      )}

      {selectedApp ? (
        <div className="space-y-8">
          {/* Action Bar with PFMS DBT Tracker button */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
            <div>
              <span className="text-xs text-slate-500 font-medium">Active Application:</span>
              <div className="flex items-center space-x-2 mt-0.5">
                <span className="font-mono font-bold text-gov-navy text-sm">
                  {selectedApp.parent_application_id
                    ? `${selectedApp.application_number} (Year Continuation Renewal)`
                    : selectedApp.application_number}
                </span>
                <span className="text-xs text-slate-600 font-semibold">• {selectedApp.scheme?.name}</span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowPfmsModal(true)}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow flex items-center space-x-1.5 transition-colors self-start sm:self-center"
            >
              <IndianRupee className="w-3.5 h-3.5" />
              <span>Track PFMS & DBT Payments</span>
            </button>
          </div>

          {/* FELLOWSHIP RENEWAL DUE BANNER */}
          {isRenewalDue && !hasPendingRenewal && (
            <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-6 shadow-lg border border-blue-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in">
              <div className="flex items-start space-x-3.5">
                <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl text-blue-200 mt-0.5 flex-shrink-0">
                  <RefreshCw className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] uppercase tracking-wider font-extrabold bg-blue-500/30 text-blue-200 px-2.5 py-0.5 rounded-full border border-blue-400/30">
                      Annual Continuation Required
                    </span>
                    <span className="text-xs text-blue-200 font-mono">
                      Due: {selectedApp.renewal_due_date}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-1">
                    Fellowship Renewal Due for Next Academic Year
                  </h3>
                  <p className="text-xs text-blue-100/80 mt-1 max-w-2xl leading-relaxed">
                    Your fellowship award under <strong>{selectedApp.scheme?.name}</strong> is eligible for annual continuation. Submit your annual academic progress report and continuation certification to extend DBT fellowship disbursements for another year.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowRenewalModal(true)}
                className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs shadow-md transition-all flex items-center space-x-2 whitespace-nowrap self-start sm:self-center"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Apply for Renewal</span>
              </button>
            </div>
          )}

          {/* RENEWAL UNDER REVIEW INFO BANNER */}
          {hasPendingRenewal && (
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 flex items-center space-x-3 shadow-xs">
              <div className="p-2.5 bg-blue-100 text-blue-800 rounded-xl flex-shrink-0">
                <RefreshCw className="w-5 h-5 animate-spin" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-blue-900">Fellowship Renewal Application Under Review</h4>
                <p className="text-xs text-blue-700 mt-0.5">
                  Your annual fellowship renewal is currently being scrutinized by the Ministry Scrutiny Officer. Upon approval, your fellowship award will be automatically extended by +365 days.
                </p>
              </div>
            </div>
          )}

          {/* HIGH PRIORITY DEFICIENCY ALERT BANNER */}
          {openDeficiencies.length > 0 && (
            <div className="bg-amber-50 border-2 border-amber-400 rounded-2xl p-6 shadow-md animate-in fade-in">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start space-x-3">
                  <div className="p-2.5 bg-amber-500 text-white rounded-xl flex-shrink-0 mt-0.5">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-extrabold tracking-wider text-amber-800">
                      High Priority Action Required
                    </span>
                    <h3 className="text-base font-bold text-amber-950 mt-0.5">
                      Deficiency Flagged by MoTA Scrutiny Officer
                    </h3>
                    <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                      Your application scrutiny is paused pending rectification of the flagged document below.
                      Please review the officer remarks and upload a rectified version immediately.
                    </p>

                    <div className="mt-4 space-y-3">
                      {openDeficiencies.map((defic) => (
                        <div
                          key={defic.id}
                          className="bg-white p-4 rounded-xl border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm"
                        >
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs font-bold text-slate-800">
                                Document: {defic.doc_type?.replace(/_/g, ' ').toUpperCase()}
                              </span>
                              <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">
                                Action Needed
                              </span>
                            </div>
                            <p className="text-xs text-slate-600 mt-1">
                              <strong>Officer Remark: </strong>
                              {defic.reason}
                            </p>
                          </div>

                          <button
                            onClick={() => setResubmitModal(defic)}
                            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg text-xs transition-colors flex items-center space-x-1.5 shadow"
                          >
                            <Upload className="w-3.5 h-3.5" />
                            <span>Resubmit Document</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5-STAGE STATUS TIMELINE */}
          <Timeline
            status={selectedApp.status}
            timelineLogs={selectedApp.timeline_logs}
            disbursementStatus={selectedApp.disbursement_status}
            disbursementAmount={selectedApp.disbursement_amount}
          />

          {/* SIDE-BY-SIDE OCR VERIFICATION MATRIX */}
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider">
                  Submitted Documents & AI Verification Matrix
                </h3>
                <p className="text-xs text-slate-500">
                  Inspect OCR extracted fields side-by-side with your submitted values
                </p>
              </div>
            </div>

            <SideBySideOcrViewer documents={selectedApp.documents} readOnly={true} />
          </section>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
          <FileText className="w-12 h-12 mx-auto text-slate-300 mb-3" />
          <h3 className="text-base font-bold text-slate-700">No applications found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            You have not submitted any fellowship or scholarship applications yet.
          </p>
          <button
            onClick={onNavigateApply}
            className="mt-5 px-5 py-2.5 bg-gov-navy text-white text-xs font-bold rounded-xl shadow hover:bg-blue-900 transition-colors inline-flex items-center space-x-2"
          >
            <span>Apply Now</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Resubmit Document Modal */}
      {resubmitModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center space-x-2">
                <Upload className="w-5 h-5 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-800">
                  Resubmit {resubmitModal.doc_type?.replace(/_/g, ' ').toUpperCase()}
                </h3>
              </div>
              <button
                onClick={() => setResubmitModal(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-amber-50 p-3 rounded-xl text-xs text-amber-800 mb-4">
              <strong className="block mb-1">Reason for Resubmission:</strong>
              {resubmitModal.reason}
            </div>

            {resubmitMsg ? (
              <div className="bg-emerald-50 text-emerald-800 p-4 rounded-xl text-xs text-center font-bold flex items-center justify-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <span>{resubmitMsg}</span>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center bg-slate-50">
                  <FileText className="w-8 h-8 mx-auto text-slate-400 mb-2" />
                  <p className="text-xs font-bold text-slate-700">Select rectified document file</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">PDF or high-resolution scan (max 10MB)</p>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <button
                    type="button"
                    onClick={() => setResubmitModal(null)}
                    className="px-4 py-2 border border-slate-300 text-slate-700 text-xs font-bold rounded-lg hover:bg-slate-100"
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    disabled={resubmitting}
                    onClick={() => handleResubmitDocument(resubmitModal)}
                    className="px-6 py-2.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg shadow flex items-center space-x-2"
                  >
                    <span>{resubmitting ? 'Submitting...' : 'Upload & Resolve Deficiency'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* PFMS DBT DISBURSEMENT MODAL */}
      <PfmsDisbursementModal
        isOpen={showPfmsModal}
        onClose={() => setShowPfmsModal(false)}
        applicationId={selectedApp?.id}
        applicationNumber={selectedApp?.application_number}
        schemeCode={selectedApp?.scheme?.code}
      />

      {/* FELLOWSHIP RENEWAL MODAL */}
      <RenewalModal
        isOpen={showRenewalModal}
        onClose={() => setShowRenewalModal(false)}
        application={selectedApp}
        onRenewalSuccess={() => {
          loadApplications();
        }}
      />
    </div>
  );
}
