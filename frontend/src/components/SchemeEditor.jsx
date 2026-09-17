import React, { useState, useEffect } from 'react';
import { X, Sliders, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../api/client';

export default function SchemeEditor({ scheme, isOpen, onClose, onSaved }) {
  const [formData, setFormData] = useState({
    income_ceiling: 600000,
    min_marks: 55,
    financial_assistance: '',
    objective: '',
    is_active: true,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (scheme) {
      setFormData({
        income_ceiling: scheme.income_ceiling ?? 600000,
        min_marks: scheme.min_marks ?? 55,
        financial_assistance: scheme.financial_assistance || '',
        objective: scheme.objective || '',
        is_active: scheme.is_active ?? true,
      });
      setError(null);
      setSuccess(false);
    }
  }, [scheme]);

  if (!isOpen || !scheme) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const updated = await api.schemes.update(scheme.id, {
        income_ceiling: parseFloat(formData.income_ceiling),
        min_marks: parseFloat(formData.min_marks),
        financial_assistance: formData.financial_assistance,
        objective: formData.objective,
        is_active: Boolean(formData.is_active),
      });
      setSuccess(true);
      setTimeout(() => {
        if (onSaved) onSaved(updated);
        onClose();
      }, 1000);
    } catch (err) {
      setError(err.message || 'Failed to update scheme eligibility rules');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200">
        {/* Header */}
        <div className="px-6 py-4 bg-gov-navy text-white flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-blue-800 text-amber-300">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm">Configure Scheme Rules: {scheme.code}</h3>
              <p className="text-[11px] text-blue-200">{scheme.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-blue-200 hover:text-white hover:bg-blue-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Notice on structural fields */}
        <div className="bg-slate-50 border-b border-slate-200 px-6 py-2.5 text-[11px] text-slate-500">
          Threshold parameters are updated live in the eligibility engine. Structural form schemas remain versioned.
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
              <span className="font-bold">Scheme eligibility rules updated successfully! Audited in ledger.</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="font-bold text-slate-700 block mb-1">
                Income Ceiling (₹/year)
              </label>
              <input
                type="number"
                step="10000"
                required
                value={formData.income_ceiling}
                onChange={(e) => setFormData({ ...formData, income_ceiling: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gov-navy focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1">
                Min. Qualifying Marks (%)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="100"
                required
                value={formData.min_marks}
                onChange={(e) => setFormData({ ...formData, min_marks: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gov-navy focus:outline-none font-mono"
              />
            </div>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">
              Financial Assistance & Slab Details
            </label>
            <textarea
              rows={2}
              value={formData.financial_assistance}
              onChange={(e) => setFormData({ ...formData, financial_assistance: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gov-navy focus:outline-none"
              placeholder="e.g. ₹28,000/month fellowship + contingency grant"
            />
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">
              Statutory Objective / Scope
            </label>
            <textarea
              rows={2}
              value={formData.objective}
              onChange={(e) => setFormData({ ...formData, objective: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gov-navy focus:outline-none"
              placeholder="Mandate and scope of scheme"
            />
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <span className="font-bold text-slate-800 block">Scheme Active Status</span>
              <span className="text-[11px] text-slate-500">Allow new candidate submissions for this scheme</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
            </label>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end space-x-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-700 font-bold rounded-xl hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-xl shadow transition-colors flex items-center space-x-1.5"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Saving Rules...</span>
                </>
              ) : (
                <span>Save Scheme Rules</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
