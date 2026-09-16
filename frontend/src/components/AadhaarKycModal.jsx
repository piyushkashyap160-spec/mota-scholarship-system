import React, { useState } from 'react';
import { X, ShieldCheck, CheckCircle2, ArrowRight, Loader2, KeyRound, Lock, UserCheck } from 'lucide-react';
import { api } from '../api/client';

export default function AadhaarKycModal({ isOpen, onClose, currentName, onKycComplete }) {
  const [step, setStep] = useState('input_aadhaar'); // 'input_aadhaar', 'input_otp', 'success'
  const [aadhaarNumber, setAadhaarNumber] = useState('981244018892');
  const [otp, setOtp] = useState('');
  const [txnId, setTxnId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verifiedResult, setVerifiedResult] = useState(null);

  if (!isOpen) return null;

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.integrations.sendAadhaarOtp(aadhaarNumber);
      setTxnId(res.txn_id);
      setStep('input_otp');
    } catch (err) {
      setError(err.message || 'Failed to dispatch Aadhaar OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.integrations.verifyAadhaarOtp({
        txn_id: txnId,
        otp: otp,
        aadhaar_number: aadhaarNumber,
        applicant_name: currentName
      });
      setVerifiedResult(res);
      setStep('success');
      if (onKycComplete) {
        onKycComplete(res);
      }
    } catch (err) {
      setError(err.message || 'Invalid Aadhaar OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
        {/* Header with UIDAI Aadhaar Branding */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 via-amber-600 to-yellow-500 text-white flex items-center justify-center font-bold shadow">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-slate-900">Aadhaar e-KYC Verification</h3>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                UIDAI Authentication & Certified Demographic Verification
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

        {step === 'input_aadhaar' && (
          <form onSubmit={handleSendOtp} className="my-5 space-y-4 text-xs">
            <p className="text-slate-600 leading-relaxed">
              Verify your identity via Aadhaar OTP. On successful verification, your Full Name and State of Domicile will be certified and locked to prevent fraudulent impersonation.
            </p>

            <div>
              <label className="block text-slate-700 font-bold mb-1">Enter 12-Digit Aadhaar Number</label>
              <input
                type="text"
                maxLength={12}
                value={aadhaarNumber}
                onChange={(e) => setAadhaarNumber(e.target.value)}
                placeholder="e.g. 981244018892"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 font-mono text-sm tracking-widest focus:ring-2 focus:ring-gov-navy focus:outline-none"
                required
              />
              <span className="text-[11px] text-slate-400 mt-1 block">
                OTP will be simulated to your Aadhaar-registered mobile.
              </span>
            </div>

            {error && <p className="text-rose-600 font-medium">{error}</p>}

            <button
              type="submit"
              disabled={loading || aadhaarNumber.length !== 12}
              className="w-full py-2.5 bg-gov-navy hover:bg-blue-900 text-white rounded-xl font-bold shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4 text-amber-300" />}
              <span>Send Aadhaar OTP</span>
            </button>
          </form>
        )}

        {step === 'input_otp' && (
          <form onSubmit={handleVerifyOtp} className="my-5 space-y-4 text-xs">
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-blue-900">
              <span className="font-bold block">OTP Dispatched!</span>
              <p className="text-[11px] text-blue-800 mt-0.5">
                Enter the 6-digit code sent to your linked phone.
                <strong className="block mt-1 text-gov-navy font-mono">Prototype Sandbox Test OTP: 123456</strong>
              </p>
            </div>

            <div>
              <label className="block text-slate-700 font-bold mb-1">Enter 6-Digit OTP</label>
              <input
                type="text"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="123456"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 font-mono text-center text-lg tracking-widest focus:ring-2 focus:ring-gov-navy focus:outline-none"
                required
              />
            </div>

            {error && <p className="text-rose-600 font-medium">{error}</p>}

            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={() => setStep('input_aadhaar')}
                className="w-1/3 py-2.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl font-semibold transition-all"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-2/3 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4 text-white" />}
                <span>Verify & Lock Profile</span>
              </button>
            </div>
          </form>
        )}

        {step === 'success' && verifiedResult && (
          <div className="my-5 space-y-4 text-xs animate-in fade-in">
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 flex items-start space-x-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-sm text-emerald-950 block">Aadhaar e-KYC Verified!</span>
                <p className="text-[11px] text-emerald-800 mt-0.5 leading-relaxed">
                  Identity certified with UIDAI authentication servers. Verified demographic profile has been linked to this application.
                </p>
              </div>
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-200">
                <span className="text-slate-500">Certified Scholar Name:</span>
                <span className="font-bold text-slate-800">{verifiedResult.demographics?.full_name}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200">
                <span className="text-slate-500">Aadhaar Token:</span>
                <span className="font-mono font-semibold text-slate-800">{verifiedResult.aadhaar_masked}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200">
                <span className="text-slate-500">State of Domicile:</span>
                <span className="font-bold text-gov-navy">{verifiedResult.demographics?.state}</span>
              </div>
              <div className="flex items-center space-x-1.5 pt-1 text-[11px] text-slate-500">
                <Lock className="w-3.5 h-3.5 text-slate-400" />
                <span>Certified fields have been securely locked in the application form.</span>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="w-full py-2.5 bg-gov-navy text-white rounded-xl font-bold transition-all shadow"
            >
              Continue with Verified Application
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
