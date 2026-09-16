import React from 'react';
import { AlertCircle, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function DynamicFormRenderer({ scheme, formData, onChange, errors = {} }) {
  if (!scheme || !scheme.form_fields) {
    return <div className="text-slate-500 py-4">No field configuration available for this scheme.</div>;
  }

  // Group fields by section
  const sections = {};
  scheme.form_fields.forEach((field) => {
    const sectionName = field.section || 'General Information';
    if (!sections[sectionName]) {
      sections[sectionName] = [];
    }
    sections[sectionName].push(field);
  });

  const handleFieldChange = (id, val) => {
    onChange({
      ...formData,
      [id]: val,
    });
  };

  const ceiling = scheme.income_ceiling || 600000;
  const minMarks = scheme.min_marks || 55;

  return (
    <div className="space-y-8">
      {Object.entries(sections).map(([sectionName, fields]) => (
        <div key={sectionName} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3 mb-5">
            <ShieldCheck className="w-5 h-5 text-gov-navy" />
            <h3 className="text-base font-bold text-gov-navy">{sectionName}</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {fields.map((field) => {
              const val = formData[field.id] !== undefined ? formData[field.id] : (field.default || '');
              const error = errors[field.id];

              // Live eligibility hints
              let liveHint = null;
              if (field.id === 'annual_income' && val !== '') {
                const inc = parseFloat(val);
                if (inc > ceiling) {
                  liveHint = (
                    <span className="text-xs font-semibold text-rose-600 flex items-center mt-1">
                      <AlertCircle className="w-3 h-3 mr-1" />
                      Income ₹{inc.toLocaleString('en-IN')} exceeds scheme ceiling of ₹{ceiling.toLocaleString('en-IN')}
                    </span>
                  );
                } else if (inc > 0) {
                  liveHint = (
                    <span className="text-xs font-semibold text-emerald-600 flex items-center mt-1">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      Within allowable income ceiling (≤ ₹{ceiling.toLocaleString('en-IN')})
                    </span>
                  );
                }
              }

              if (field.id === 'marks_percentage' && val !== '') {
                const marks = parseFloat(val);
                if (marks < minMarks) {
                  liveHint = (
                    <span className="text-xs font-semibold text-rose-600 flex items-center mt-1">
                      <AlertCircle className="w-3 h-3 mr-1" />
                      Marks {marks}% below mandatory threshold of {minMarks}%
                    </span>
                  );
                } else if (marks >= minMarks) {
                  liveHint = (
                    <span className="text-xs font-semibold text-emerald-600 flex items-center mt-1">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      Satisfies academic criteria (≥ {minMarks}%)
                    </span>
                  );
                }
              }

              return (
                <div key={field.id} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    {field.label} {field.required && <span className="text-rose-500">*</span>}
                  </label>

                  {field.type === 'select' ? (
                    <select
                      value={val}
                      onChange={(e) => handleFieldChange(field.id, e.target.value)}
                      disabled={field.read_only}
                      className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-gov-navy focus:border-transparent transition-all shadow-sm"
                    >
                      <option value="">-- Select Option --</option>
                      {field.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  ) : field.type === 'textarea' ? (
                    <textarea
                      rows={3}
                      value={val}
                      onChange={(e) => handleFieldChange(field.id, e.target.value)}
                      placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                      className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-gov-navy focus:border-transparent transition-all shadow-sm"
                    />
                  ) : (
                    <input
                      type={field.type || 'text'}
                      value={val}
                      readOnly={field.read_only}
                      onChange={(e) => handleFieldChange(field.id, e.target.value)}
                      placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                      className={`w-full px-3.5 py-2.5 rounded-lg border ${
                        field.read_only ? 'bg-slate-100 text-slate-600 cursor-not-allowed' : 'bg-white text-slate-800'
                      } border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-gov-navy focus:border-transparent transition-all shadow-sm`}
                    />
                  )}

                  {liveHint}
                  {error && <p className="text-xs text-rose-500 font-medium mt-1">{error}</p>}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
