import React, { useState } from 'react';
import { Award, Shield, User, Lock, Mail, ArrowRight, CheckCircle2, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import { INDIAN_STATES_AND_UTS } from '../constants';

export default function Login({ onLoginSuccess, initialTab = 'login' }) {
  const [tab, setTab] = useState(initialTab); // 'login' or 'register'
  const [role, setRole] = useState('applicant'); // 'applicant' or 'admin'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [stCert, setStCert] = useState('');
  const [state, setState] = useState('Jharkhand');
  const [tribe, setTribe] = useState('Santhal');
  const [institution, setInstitution] = useState('');

  const handleLogin = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);
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

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-lg text-xs transition-colors shadow flex items-center justify-center space-x-2"
              >
                <span>{loading ? 'Authenticating...' : 'Sign In to Portal'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
