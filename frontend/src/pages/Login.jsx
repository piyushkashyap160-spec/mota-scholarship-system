import React, { useState } from 'react';
import { Award, Shield, User, Lock, Mail, ArrowRight, CheckCircle2, Sparkles, AlertCircle, KeyRound, Building2 } from 'lucide-react';

import { api } from '../api/client';
import { INDIAN_STATES_AND_UTS } from '../constants';

export default function Login({ onLoginSuccess, initialTab = 'login' }) {
  const [tab, setTab] = useState(initialTab); // 'login' or 'register'
  const [role, setRole] = useState('applicant'); // 'applicant' or 'admin'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Forgot password flow state
  const [showForgot, setShowForgot] = useState(false);
  const [forgotStep, setForgotStep] = useState(1); // 1: Email, 2: OTP + new password
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotOtp, setForgotOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [forgotInfo, setForgotInfo] = useState(null);

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [stCert, setStCert] = useState('');
  const [state, setState] = useState('Jharkhand');
  const [tribe, setTribe] = useState('Santhal');
  const [institution, setInstitution] = useState('');

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.forgotPassword(forgotEmail);
      setForgotInfo(res.message || 'OTP sent to registered email');
      setForgotStep(2);
    } catch (err) {
      setError(err.message || 'Failed to request password reset OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.auth.resetPassword(forgotEmail, forgotOtp, newPassword);
      setShowForgot(false);
      setForgotStep(1);
      setForgotOtp('');
      setNewPassword('');
      setSuccessMessage('Password reset successful. Please login.');
    } catch (err) {
      setError(err.message || 'Password reset failed. Invalid or expired OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await api.auth.login(email, password);
      localStorage.setItem('mota_token', res.access_token);
      onLoginSuccess(res);
    } catch (err) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.register({
        email,
        password,
        full_name: fullName,
        st_cert_number: stCert,
        state,
        community_tribe: tribe,
        institution,
        role: 'applicant',
      });
      localStorage.setItem('mota_token', res.access_token);
      onLoginSuccess(res);
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  // Instant Demo Logins for Judges
  const triggerQuickDemo = async (demoEmail, demoPass) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.login(demoEmail, demoPass);
      localStorage.setItem('mota_token', res.access_token);
      onLoginSuccess(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gov-navy text-white p-6 text-center relative">
          <div className="w-12 h-12 rounded-xl bg-white/10 mx-auto flex items-center justify-center mb-3">
            <Award className="w-7 h-7 text-amber-400" />
          </div>
          <h2 className="text-lg font-bold">MoTA Scholarship Access Portal</h2>
          <p className="text-xs text-slate-300 mt-1">Ministry of Tribal Affairs, Government of India</p>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-200 bg-slate-50 text-xs font-bold">
          <button
            onClick={() => { setTab('login'); setError(null); }}
            className={`flex-1 py-3 text-center transition-colors ${
              tab === 'login' ? 'bg-white text-gov-navy border-b-2 border-gov-navy' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => { setTab('register'); setError(null); }}
            className={`flex-1 py-3 text-center transition-colors ${
              tab === 'register' ? 'bg-white text-gov-navy border-b-2 border-gov-navy' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            New ST Student Registration
          </button>
        </div>

        <div className="p-6 space-y-5">
          {successMessage && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-xl text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
              <span className="font-semibold">{successMessage}</span>
            </div>
          )}

          {error && (
            <div className="bg-rose-50 border border-rose-200 text-rose-700 p-3 rounded-xl text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. scholar@research.ac.in"
                    className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setShowForgot(true);
                    setForgotStep(1);
                    setForgotEmail(email || '');
                    setError(null);
                    setSuccessMessage(null);
                  }}
                  className="text-[11px] font-semibold text-gov-navy hover:underline"
                >
                  Forgot Password?
                </button>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-lg text-xs transition-colors shadow flex items-center justify-center space-x-2"
              >
                <span>{loading ? 'Authenticating...' : 'Sign In to Portal'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          ) : showForgot ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-2 border-b border-slate-100 pb-2">
                <KeyRound className="w-4 h-4 text-gov-navy" />
                <h3 className="font-bold text-xs text-slate-800">
                  {forgotStep === 1 ? 'Recover Portal Password (Step 1 of 2)' : 'Enter OTP & Set New Password (Step 2 of 2)'}
                </h3>
              </div>

              {forgotStep === 1 ? (
                <form onSubmit={handleForgotPassword} className="space-y-3">
                  <p className="text-[11px] text-slate-500">
                    Enter your registered email address. We will send a secure 6-digit verification OTP.
                  </p>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Registered Email
                    </label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                      <input
                        type="email"
                        required
                        value={forgotEmail}
                        onChange={(e) => setForgotEmail(e.target.value)}
                        placeholder="e.g. birsa.soren@stmail.in"
                        className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-lg text-xs transition-colors shadow flex items-center justify-center space-x-2"
                  >
                    <span>{loading ? 'Dispatching OTP...' : 'Send Verification OTP'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>

                  <div className="text-center pt-1">
                    <button
                      type="button"
                      onClick={() => { setShowForgot(false); setError(null); }}
                      className="text-[11px] text-slate-500 hover:text-slate-800 underline"
                    >
                      Back to Sign In
                    </button>
                  </div>
                </form>
              ) : (
                <form onSubmit={handleResetPassword} className="space-y-3">
                  {forgotInfo && (
                    <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-blue-900 text-xs flex items-center space-x-2 font-medium">
                      <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                      <span>{forgotInfo} (Check Simulated Notification Log if testing locally)</span>
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      6-Digit OTP Code
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      value={forgotOtp}
                      onChange={(e) => setForgotOtp(e.target.value)}
                      placeholder="e.g. 123456"
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-mono font-bold tracking-widest text-center focus:ring-2 focus:ring-gov-navy focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      New Password
                    </label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                      <input
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new strong password"
                        className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-xs transition-colors shadow flex items-center justify-center space-x-2"
                  >
                    <span>{loading ? 'Verifying & Updating...' : 'Reset Password & Proceed'}</span>
                    <CheckCircle2 className="w-4 h-4" />
                  </button>

                  <div className="flex justify-between items-center text-[11px] pt-1">
                    <button
                      type="button"
                      onClick={() => setForgotStep(1)}
                      className="text-slate-500 hover:text-slate-800 underline"
                    >
                      Change Email
                    </button>
                    <button
                      type="button"
                      onClick={() => { setShowForgot(false); setError(null); }}
                      className="text-gov-navy font-semibold hover:underline"
                    >
                      Back to Sign In
                    </button>
                  </div>
                </form>
              )}
            </div>
          ) : (
            <form onSubmit={handleRegister} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Full Name as on ST Certificate"
                  className="w-full px-3 py-2 rounded border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@university.ac.in"
                  className="w-full px-3 py-2 rounded border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create password"
                  className="w-full px-3 py-2 rounded border border-slate-300 text-xs focus:ring-2 focus:ring-gov-navy focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase">ST Cert No.</label>
                  <input
                    type="text"
                    required
                    value={stCert}
                    onChange={(e) => setStCert(e.target.value)}
                    placeholder="ST/JH/2024/..."
                    className="w-full px-3 py-2 rounded border border-slate-300 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase">Tribe / Sub-Caste</label>
                  <input
                    type="text"
                    required
                    value={tribe}
                    onChange={(e) => setTribe(e.target.value)}
                    placeholder="Santhal, Gond, Bhil..."
                    className="w-full px-3 py-2 rounded border border-slate-300 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase">State of Domicile</label>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full px-3 py-2 rounded border border-slate-300 text-xs"
                >
                  {INDIAN_STATES_AND_UTS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-lg text-xs transition-colors shadow mt-2"
              >
                {loading ? 'Registering...' : 'Complete ST Registration'}
              </button>
            </form>
          )}

          {/* Quick Demo Pre-Seeded Logins (for Judging / Demo) */}
          <div className="pt-4 border-t border-slate-200">
            <span className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider text-center mb-2.5">
              Instant 1-Click Demo Logins for Evaluation
            </span>

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => triggerQuickDemo('admin@mota.gov.in', 'admin123')}
                className="w-full p-2.5 rounded-lg border border-blue-200 bg-blue-50/70 hover:bg-blue-100 text-gov-navy text-left flex items-center justify-between transition-colors text-xs"
              >
                <div className="flex items-center space-x-2">
                  <Shield className="w-4 h-4 text-blue-700" />
                  <div>
                    <span className="font-bold block">MoTA Scrutiny Officer (Admin)</span>
                    <span className="text-[10px] text-slate-500">admin@mota.gov.in (Full Admin Access)</span>
                  </div>
                </div>
                <span className="font-bold text-blue-700 text-[11px]">Login →</span>
              </button>

              <button
                type="button"
                onClick={() => triggerQuickDemo('pooja.halba@stmail.in', 'scholar123')}
                className="w-full p-2.5 rounded-lg border border-amber-200 bg-amber-50/70 hover:bg-amber-100 text-amber-900 text-left flex items-center justify-between transition-colors text-xs"
              >
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-amber-700" />
                  <div>
                    <span className="font-bold block">Pooja Halba (Needs Review Demo)</span>
                    <span className="text-[10px] text-slate-500">Has active deficiency ready for resubmission</span>
                  </div>
                </div>
                <span className="font-bold text-amber-700 text-[11px]">Login →</span>
              </button>

              <button
                type="button"
                onClick={() => triggerQuickDemo('birsa.soren@research.ac.in', 'scholar123')}
                className="w-full p-2.5 rounded-lg border border-emerald-200 bg-emerald-50/70 hover:bg-emerald-100 text-emerald-900 text-left flex items-center justify-between transition-colors text-xs"
              >
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                  <div>
                    <span className="font-bold block">Birsa Soren (Selected Scholar Demo)</span>
                    <span className="text-[10px] text-slate-500">Selected NFST Fellow with active disbursement</span>
                  </div>
                </div>
                <span className="font-bold text-emerald-700 text-[11px]">Login →</span>
              </button>

              <button
                type="button"
                onClick={() => triggerQuickDemo('nodal@iitd.ac.in', 'nodal123')}
                className="w-full p-2.5 rounded-lg border border-indigo-200 bg-indigo-50/70 hover:bg-indigo-100 text-indigo-900 text-left flex items-center justify-between transition-colors text-xs"
              >
                <div className="flex items-center space-x-2">
                  <Building2 className="w-4 h-4 text-indigo-700" />
                  <div>
                    <span className="font-bold block">Institution Nodal Desk (IIT Delhi)</span>
                    <span className="text-[10px] text-slate-500">nodal@iitd.ac.in (Verify university scholars)</span>
                  </div>
                </div>
                <span className="font-bold text-indigo-700 text-[11px]">Login →</span>
              </button>

              <button
                type="button"
                onClick={() => triggerQuickDemo('nodal@cuj.ac.in', 'nodal123')}
                className="w-full p-2.5 rounded-lg border border-indigo-200 bg-indigo-50/70 hover:bg-indigo-100 text-indigo-900 text-left flex items-center justify-between transition-colors text-xs"
              >
                <div className="flex items-center space-x-2">
                  <Building2 className="w-4 h-4 text-indigo-700" />
                  <div>
                    <span className="font-bold block">Institution Nodal Desk (Central Univ of Jharkhand)</span>
                    <span className="text-[10px] text-slate-500">nodal@cuj.ac.in (CUJ Nodal Sign-off)</span>
                  </div>
                </div>
                <span className="font-bold text-indigo-700 text-[11px]">Login →</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
