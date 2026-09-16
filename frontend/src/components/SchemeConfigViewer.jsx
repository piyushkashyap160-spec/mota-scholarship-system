import React, { useState } from 'react';
import { Settings, FileCode, CheckCircle2, Shield, Layers, X, Copy, Check } from 'lucide-react';

export default function SchemeConfigViewer({ scheme, onClose }) {
  const [activeTab, setActiveTab] = useState('visual');
  const [copied, setCopied] = useState(false);

  if (!scheme) return null;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(scheme, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-gov-navy text-white p-5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/10 rounded-lg">
              <Settings className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs bg-amber-400 text-gov-navy px-2 py-0.5 rounded font-bold">
                  {scheme.code}
                </span>
                <span className="text-xs text-slate-300">Scheme Rule-Engine Configuration</span>
              </div>
              <h2 className="text-base font-bold leading-tight">{scheme.name}</h2>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="flex bg-white/10 rounded-lg p-1 text-xs">
              <button
                onClick={() => setActiveTab('visual')}
                className={`px-3 py-1 rounded-md font-semibold transition-all ${
                  activeTab === 'visual' ? 'bg-white text-gov-navy shadow' : 'text-white hover:bg-white/10'
                }`}
              >
                Visual Specs
              </button>
              <button
                onClick={() => setActiveTab('json')}
                className={`px-3 py-1 rounded-md font-semibold transition-all ${
                  activeTab === 'json' ? 'bg-white text-gov-navy shadow' : 'text-white hover:bg-white/10'
                }`}
              >
                Raw JSON Rulebase
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === 'visual' ? (
            <div className="space-y-6">
              {/* Core Scheme Objectives */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Official Title & Purpose
                </h4>
                <p className="text-sm font-bold text-slate-800">{scheme.full_title}</p>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{scheme.objective}</p>
                <div className="mt-3 text-xs bg-blue-50 border border-blue-200 text-gov-navy p-2.5 rounded-lg font-medium">
                  <strong>Financial Assistance: </strong> {scheme.financial_assistance}
                </div>
              </div>

              {/* Configured Eligibility Rules */}
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <div className="bg-slate-100 px-4 py-2.5 border-b border-slate-200">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Rule Engine: Automatic Qualification Parameters
                  </h4>
                </div>
                <div className="p-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-400 uppercase font-bold text-[10px] block">Mandatory Category</span>
                    <span className="font-extrabold text-gov-navy text-sm">
                      {scheme.eligibility_rules?.category_required || 'Scheduled Tribe (ST)'}
                    </span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-400 uppercase font-bold text-[10px] block">Max Annual Income</span>
                    <span className="font-extrabold text-gov-navy text-sm">
                      ₹ {(scheme.income_ceiling || 600000).toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-400 uppercase font-bold text-[10px] block">Min Academic Score</span>
                    <span className="font-extrabold text-gov-navy text-sm">
                      {scheme.min_marks || 55}% Aggregate
                    </span>
                  </div>
                </div>
              </div>

              {/* Configured Required Documents & OCR Target Extraction Fields */}
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <div className="bg-slate-100 px-4 py-2.5 border-b border-slate-200">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Configured Documents & AI-OCR Extraction Schemas
                  </h4>
                </div>
                <div className="divide-y divide-slate-100">
                  {scheme.required_documents?.map((d, i) => (
                    <div key={i} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-slate-800">{d.title}</span>
                          <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                            {d.doc_type}
                          </span>
                        </div>
                        <p className="text-slate-500 mt-0.5">{d.description}</p>
                      </div>

                      <div className="flex flex-wrap gap-1">
                        {d.target_fields?.map((f) => (
                          <span key={f} className="text-[10px] bg-blue-50 text-gov-navy border border-blue-200 px-2 py-0.5 rounded font-mono">
                            {f}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dynamic Form Schema Summary */}
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <div className="bg-slate-100 px-4 py-2.5 border-b border-slate-200">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Dynamic Application Fields ({scheme.form_fields?.length || 0} fields rendered automatically)
                  </h4>
                </div>
                <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  {scheme.form_fields?.map((f) => (
                    <div key={f.id} className="bg-slate-50 p-2 rounded border border-slate-200">
                      <span className="text-[10px] text-slate-400 block font-bold uppercase">{f.type}</span>
                      <span className="font-semibold text-slate-700 truncate block">{f.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="relative">
              <button
                onClick={handleCopyJson}
                className="absolute top-3 right-3 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
              </button>
              <pre className="bg-slate-900 text-emerald-400 p-5 rounded-xl text-xs font-mono overflow-x-auto leading-relaxed max-h-[60vh]">
                {JSON.stringify(scheme, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-100 px-6 py-3 border-t border-slate-200 flex justify-between items-center text-xs text-slate-500">
          <span>Demonstrating: Single Common System with Dynamic Scheme-Specific Configurations</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gov-navy text-white rounded-lg font-bold hover:bg-blue-900 transition-colors"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
}
