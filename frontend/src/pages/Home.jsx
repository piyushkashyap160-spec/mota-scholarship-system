import React, { useState, useEffect } from 'react';
import { Award, Globe, ArrowRight, ShieldCheck, FileCheck, CheckCircle2, Sliders, Users, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import SchemeConfigViewer from '../components/SchemeConfigViewer';

export default function Home({ onSelectScheme, onOpenLogin, currentUser }) {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inspectingScheme, setInspectingScheme] = useState(null);

  useEffect(() => {
    async function loadSchemes() {
      try {
        const data = await api.schemes.getAll();
        setSchemes(data);
      } catch (err) {
        console.error('Failed to load schemes:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSchemes();
  }, []);

  return (
    <div className="space-y-10 pb-16">
      {/* Hero Banner with Official Gov Styling */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-gov-dark via-gov-navy to-blue-900 text-white p-8 sm:p-12 shadow-xl border border-blue-950">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 bg-amber-400/20 border border-amber-400/30 text-amber-300 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-4">
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            <span>SIH 2025 Problem Statement 26239</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight leading-tight">
            MoTA Scholarship & Fellowship Management System
          </h1>
          <p className="mt-3 text-sm sm:text-base text-slate-200 leading-relaxed">
            A unified, AI-assisted digital platform empowering Scheduled Tribe (ST) scholars across India.
            Streamlining registration, dynamic scheme configurability, automated Tesseract OCR document verification,
            and transparent merit scrutiny.
          </p>

          {currentUser?.role === 'admin' ? (
            <div className="mt-8 flex flex-wrap gap-4">
              <button
                onClick={() => onSelectScheme('admin-dashboard')}
                className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl shadow-lg transition-all flex items-center space-x-2 text-sm"
              >
                <span>Enter Central Scrutiny Portal</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => onSelectScheme('merit-ranking')}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl border border-white/20 transition-all flex items-center space-x-2 text-sm"
              >
                <span>Assistive Merit Ranking</span>
                <Users className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="mt-8 flex flex-wrap gap-4">
              <button
                onClick={() => onSelectScheme(schemes[0]?.id || 1)}
                className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl shadow-lg transition-all flex items-center space-x-2 text-sm"
              >
                <span>Apply for Fellowship (NFST)</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => onSelectScheme(schemes[1]?.id || 2)}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl border border-white/20 transition-all flex items-center space-x-2 text-sm"
              >
                <span>Apply for Overseas Studies (NOS)</span>
                <Globe className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Decorative Watermark Emblem Accent */}
        <div className="absolute right-4 -bottom-10 opacity-10 pointer-events-none">
          <Award className="w-96 h-96 text-white" />
        </div>
      </section>

      {/* Key Innovation Highlights */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-blue-50 text-gov-navy rounded-xl">
            <Sliders className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">Dynamic Scheme Configurability</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              No hardcoded forms. Schemes define their own required documents, eligibility rules, and fields dynamically via JSON.
            </p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">AI Document Scrutiny Engine</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Tesseract OCR extracts key data from ST caste, income certificates, and marksheets, cross-checking inputs side-by-side.
            </p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-purple-50 text-purple-700 rounded-xl">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">Assistive Merit Ranking</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              "AI assists, human decides" — Automated rule filtering with configurable weight formulas for scrutiny committees.
            </p>
          </div>
        </div>
      </section>

      {/* Active MoTA Schemes Selection Section */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-amber-600">Available Schemes</span>
            <h2 className="text-xl font-bold text-gov-navy">
              {currentUser?.role === 'admin'
                ? 'Statutory MoTA Schemes & Central Eligibility Rules'
                : 'Choose a Scheme to Apply or Inspect Rules'}
            </h2>
          </div>
          <span className="text-xs text-slate-500">Configured via MoTA Central Architecture</span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-500">Loading active schemes...</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {schemes.map((scheme) => (
              <div
                key={scheme.id}
                className="bg-white rounded-2xl border border-slate-200 p-7 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="px-3 py-1 bg-gov-navy text-white text-xs font-bold rounded-lg uppercase tracking-wider">
                      {scheme.code}
                    </span>
                    <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                      Applications Open
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-gov-navy">{scheme.name}</h3>
                  <p className="text-xs text-slate-600 mt-2 line-clamp-3 leading-relaxed">
                    {scheme.objective}
                  </p>

                  <div className="mt-5 bg-slate-50 p-4 rounded-xl space-y-2 text-xs border border-slate-100">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Target Beneficiaries:</span>
                      <span className="font-semibold text-slate-800">{scheme.target_group}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Max Family Income:</span>
                      <span className="font-semibold text-gov-navy font-mono">
                        ≤ ₹ {(scheme.income_ceiling || 600000).toLocaleString('en-IN')} / year
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Qualifying Marks:</span>
                      <span className="font-semibold text-gov-navy font-mono">{scheme.min_marks}% minimum</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Financial Assistance:</span>
                      <span className="font-semibold text-emerald-700 truncate max-w-[200px]">
                        {scheme.financial_assistance}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-5 border-t border-slate-100 flex items-center justify-between gap-3">
                  <button
                    type="button"
                    onClick={() => setInspectingScheme(scheme)}
                    className="px-3 py-2 text-xs font-bold text-gov-navy hover:bg-slate-100 rounded-lg transition-colors flex items-center space-x-1 border border-slate-200"
                  >
                    <Sliders className="w-3.5 h-3.5" />
                    <span>View Scheme Config JSON</span>
                  </button>

                  {currentUser?.role === 'admin' ? (
                    <button
                      type="button"
                      onClick={() => onSelectScheme('admin-dashboard')}
                      className="px-4 py-2.5 bg-blue-900 hover:bg-gov-navy text-white text-xs font-bold rounded-xl transition-colors flex items-center space-x-1.5 shadow"
                      title={`Open Central Scrutiny Portal for ${scheme.code}`}
                    >
                      <span>Review in Scrutiny</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => onSelectScheme(scheme.id)}
                      className="px-5 py-2.5 bg-gov-navy hover:bg-blue-900 text-white text-xs font-bold rounded-xl transition-colors flex items-center space-x-1.5 shadow"
                    >
                      <span>Start Application</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Scheme Config Inspector Modal */}
      {inspectingScheme && (
        <SchemeConfigViewer scheme={inspectingScheme} onClose={() => setInspectingScheme(null)} />
      )}
    </div>
  );
}
