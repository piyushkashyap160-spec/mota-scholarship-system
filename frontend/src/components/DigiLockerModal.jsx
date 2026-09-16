import React, { useState, useEffect } from 'react';
import { X, ShieldCheck, CheckCircle2, ArrowRight, Loader2, FileText, Sparkles, ExternalLink } from 'lucide-react';
import { api } from '../api/client';

export default function DigiLockerModal({ isOpen, onClose, onImportComplete }) {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfileId, setSelectedProfileId] = useState('jharkhand_birsa');
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    api.integrations.getDigiLockerProfiles()
      .then((data) => {
        setProfiles(data);
        if (data.length > 0) setSelectedProfileId(data[0].id);
      })
      .catch((err) => setError(err.message || 'Failed to connect to DigiLocker sandbox'))
      .finally(() => setLoading(false));
  }, [isOpen]);

  if (!isOpen) return null;

  const handlePullDocuments = async () => {
    setImporting(true);
    setError(null);
    try {
      const result = await api.integrations.fetchDigiLockerDocs(selectedProfileId);
      onImportComplete(result);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to pull documents from DigiLocker');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
        {/* Header with DigiLocker India Stack Branding */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold shadow">
              <ShieldCheck className="w-6 h-6 text-emerald-300" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-slate-900">DigiLocker Document Gateway</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                  India Stack / API Setu
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Pull issuer-signed, tamper-proof certificates directly from government repositories.
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

        {/* Value Proposition Alert */}
        <div className="my-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 text-xs flex items-start space-x-2.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block">Pre-Verified by Issuing Authority</span>
            <p className="text-[11px] text-emerald-800 mt-0.5">
              Documents pulled from DigiLocker skip manual OCR scrutiny and are instantly recognized with 100% authenticity.
            </p>
          </div>
        </div>

        {/* Sandbox Profiles Selector */}
        <div className="space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-600 block">
            Select Test DigiLocker Account (Sandbox Profiles)
          </span>

          {loading ? (
            <div className="py-8 text-center text-slate-400 flex items-center justify-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-gov-navy" />
              <span className="text-xs">Connecting to DigiLocker API Setu...</span>
            </div>
          ) : (
            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {profiles.map((p) => (
                <label
                  key={p.id}
                  onClick={() => setSelectedProfileId(p.id)}
                  className={`p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                    selectedProfileId === p.id
                      ? 'border-gov-navy bg-blue-50/50 shadow-xs'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <input
                      type="radio"
                      name="digilocker_profile"
                      checked={selectedProfileId === p.id}
                      onChange={() => setSelectedProfileId(p.id)}
                      className="text-gov-navy focus:ring-gov-navy"
                    />
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-xs text-slate-900">{p.full_name}</span>
                        <span className="px-1.5 py-0.2 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                          {p.state}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500 block mt-0.5">
                        Tribe: <strong>{p.community_tribe}</strong> • DigiLocker ID: {p.digilocker_id}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                    3 Issued Docs
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>

        {error && <p className="text-xs text-rose-600 font-medium mt-3">{error}</p>}

        {/* Modal Actions */}
        <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={importing || loading}
            onClick={handlePullDocuments}
            className="px-5 py-2.5 bg-gov-navy hover:bg-blue-900 text-white rounded-xl text-xs font-bold transition-all shadow flex items-center space-x-2 disabled:opacity-50"
          >
            {importing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Pulling from DigiLocker...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-emerald-300" />
                <span>Pull & Autofill Verified Data</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
