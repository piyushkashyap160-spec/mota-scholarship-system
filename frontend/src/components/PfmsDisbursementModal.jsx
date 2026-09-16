import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, Clock, AlertCircle, Send, Loader2, IndianRupee, ShieldCheck, ArrowRight, HelpCircle } from 'lucide-react';
import { api } from '../api/client';

export default function PfmsDisbursementModal({ isOpen, onClose, applicationId, applicationNumber, schemeCode }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Grievance Form state
  const [showGrievanceForm, setShowGrievanceForm] = useState(false);
  const [grievanceType, setGrievanceType] = useState('Payment Delay');
  const [description, setDescription] = useState('');
  const [submittingGrievance, setSubmittingGrievance] = useState(false);
  const [grievanceResult, setGrievanceResult] = useState(null);

  useEffect(() => {
    if (!isOpen || !applicationId) return;
    setLoading(true);
    setShowGrievanceForm(false);
    setGrievanceResult(null);

    api.integrations.getPfmsTracker(applicationId)
      .then((res) => setData(res))
      .catch((err) => setError(err.message || 'Failed to fetch PFMS tracker'))
      .finally(() => setLoading(false));
  }, [isOpen, applicationId]);

  if (!isOpen) return null;

  const handleSubmitGrievance = async (e) => {
    e.preventDefault();
    setSubmittingGrievance(true);
    try {
      const res = await api.integrations.logGrievance(applicationId, {
        grievance_type: grievanceType,
        description: description
      });
      setGrievanceResult(res);
      setShowGrievanceForm(false);
      setDescription('');
    } catch (err) {
      alert(err.message || 'Failed to submit grievance');
    } finally {
      setSubmittingGrievance(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 max-h-[90vh] overflow-y-auto">
        {/* Header with PFMS DBT Branding */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold shadow">
              <IndianRupee className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-slate-900">PFMS Direct Benefit Transfer (DBT) Tracker</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  NPCI APBS Verified
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Public Financial Management System real-time treasury tracking for Application <strong>{applicationNumber}</strong>
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 flex items-center justify-center space-x-2">
            <Loader2 className="w-5 h-5 animate-spin text-gov-navy" />
            <span className="text-xs">Connecting to PFMS Electronic Payment Gateway...</span>
          </div>
        ) : error ? (
          <div className="py-8 text-center text-rose-600 text-xs">{error}</div>
        ) : data ? (
          <div className="my-5 space-y-6 text-xs">
            {/* Total Award Summary */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <span className="text-slate-400 block text-[10px] font-bold uppercase">Total Approved Fellowship Grant</span>
                <span className="text-xl font-extrabold text-gov-navy font-mono">
                  ₹ {data.total_disbursement_amount?.toLocaleString('en-IN')}
                </span>
              </div>
              <div className="text-right">
                <span className="text-slate-400 block text-[10px] font-bold uppercase">NPCI Aadhaar-Seeded Bank A/C</span>
                <span className="font-mono font-bold text-slate-800">{data.bank_account_masked} (Direct Bank Credit)</span>
              </div>
            </div>

            {/* 5-Stage PFMS Pipeline Stepper */}
            <div>
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                Treasury & Payment Pipeline Stages
              </h4>
              <div className="space-y-3">
                {data.stages?.map((stage, idx) => (
                  <div
                    key={stage.step}
                    className={`p-3.5 rounded-xl border flex items-start space-x-3 transition-all ${
                      stage.is_completed
                        ? 'bg-emerald-50/60 border-emerald-200'
                        : stage.is_active
                        ? 'bg-blue-50/60 border-blue-300'
                        : 'bg-slate-50/40 border-slate-200 opacity-60'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold ${
                      stage.is_completed
                        ? 'bg-emerald-600 text-white'
                        : stage.is_active
                        ? 'bg-blue-600 text-white animate-pulse'
                        : 'bg-slate-200 text-slate-500'
                    }`}>
                      {stage.is_completed ? <CheckCircle2 className="w-4 h-4" /> : stage.step}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-900">{stage.title}</span>
                        <span className="text-[10px] font-mono text-slate-500">{stage.date}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 mt-0.5">{stage.description}</p>
                      <span className="text-[10px] text-slate-400 block mt-1">Authority: {stage.authority}</span>
                      {stage.utr_number && (
                        <div className="mt-1.5 inline-flex items-center px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono text-[10px] font-bold border border-emerald-300">
                          UTR Ref: {stage.utr_number}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quarterly Instalment Schedule */}
            <div>
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                Instalment Disbursement Schedule
              </h4>
              <div className="overflow-x-auto border border-slate-200 rounded-xl">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-100 text-slate-600 font-bold uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Instalment</th>
                      <th className="p-3">Period</th>
                      <th className="p-3">Amount</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Credit Date</th>
                      <th className="p-3">UTR Reference</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {data.instalments?.map((inst) => (
                      <tr key={inst.instalment_no}>
                        <td className="p-3 font-bold text-gov-navy">Instalment #{inst.instalment_no}</td>
                        <td className="p-3 text-slate-700">{inst.period}</td>
                        <td className="p-3 font-mono font-bold text-slate-800">₹ {inst.amount.toLocaleString('en-IN')}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            inst.status === 'Credited'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {inst.status}
                          </span>
                        </td>
                        <td className="p-3 text-slate-500 font-mono text-[11px]">{inst.credit_date}</td>
                        <td className="p-3 font-mono text-[10px] text-slate-700">{inst.utr}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Grievance Resolution Section */}
            {grievanceResult && (
              <div className="p-4 rounded-xl bg-blue-50 border border-blue-300 text-blue-950 space-y-1">
                <div className="flex items-center space-x-2 font-bold text-xs">
                  <CheckCircle2 className="w-4 h-4 text-blue-600" />
                  <span>Grievance Registered Successfully!</span>
                </div>
                <p className="text-[11px]">
                  Tracking Reference Token: <strong className="font-mono">{grievanceResult.ticket_id}</strong>
                </p>
                <p className="text-[11px] text-blue-800">
                  Escalated to: {grievanceResult.escalation_desk}. Expected resolution within {grievanceResult.expected_resolution_days} working days.
                </p>
              </div>
            )}

            {!showGrievanceForm && !grievanceResult && (
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-500">Payment delayed or bank details changed?</span>
                <button
                  type="button"
                  onClick={() => setShowGrievanceForm(true)}
                  className="px-3.5 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-gov-navy font-bold text-xs transition-colors flex items-center space-x-1"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>Log Disbursement Grievance</span>
                </button>
              </div>
            )}

            {showGrievanceForm && (
              <form onSubmit={handleSubmitGrievance} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-gov-navy">Submit Payment Grievance to MoTA DBT Cell</span>
                  <button
                    type="button"
                    onClick={() => setShowGrievanceForm(false)}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">Issue Category</label>
                  <select
                    value={grievanceType}
                    onChange={(e) => setGrievanceType(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-300 text-xs bg-white"
                  >
                    <option value="Payment Delay">Payment Delayed Beyond Schedule</option>
                    <option value="Bank Account Change">Bank Account IFSC / Branch Changed</option>
                    <option value="Aadhaar Seeding Failure">NPCI Mapper Aadhaar Seeding Failure</option>
                    <option value="UTR Not Received">Bank Credit Not Reflected (UTR Trace Request)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">Description / Particulars</label>
                  <textarea
                    rows={3}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Provide details regarding the delayed fellowship instalment..."
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                    required
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowGrievanceForm(false)}
                    className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-200 rounded-lg"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingGrievance || !description.trim()}
                    className="px-4 py-1.5 bg-gov-navy text-white rounded-lg text-xs font-bold shadow flex items-center space-x-1.5 disabled:opacity-50"
                  >
                    {submittingGrievance ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                    <span>Submit Grievance</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
