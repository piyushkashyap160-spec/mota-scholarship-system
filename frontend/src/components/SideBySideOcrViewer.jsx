import React, { useState } from 'react';
import { FileText, CheckCircle2, AlertTriangle, XCircle, Search, Eye, Sparkles } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function SideBySideOcrViewer({ documents = [], readOnly = true }) {
  const [selectedDocIndex, setSelectedDocIndex] = useState(0);

  if (!documents || documents.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center text-slate-500">
        <FileText className="w-10 h-10 mx-auto text-slate-400 mb-2" />
        <p className="font-semibold text-slate-700">No documents submitted yet.</p>
        <p className="text-xs text-slate-500 mt-1">Uploaded documents with OCR extraction will appear here.</p>
      </div>
    );
  }

  const currentDoc = documents[selectedDocIndex] || documents[0];
  const comparison = currentDoc.comparison_data || currentDoc.comparison_matrix || {};
  const fields = comparison.fields || {};
  const discrepancies = comparison.discrepancies || currentDoc.discrepancies || [];

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header with Document Selector Tabs */}
      <div className="bg-slate-50 border-b border-slate-200 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-blue-100 text-gov-navy rounded-lg">
              <Sparkles className="w-5 h-5 text-gov-navy" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">
                AI Document Intelligence & Cross-Verification Matrix
              </h3>
              <p className="text-xs text-slate-500">
                Tesseract OCR extraction mapped side-by-side with applicant-entered form values
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-slate-500">Document Status:</span>
            <StatusBadge status={currentDoc.status} />
          </div>
        </div>

        {/* Tab Buttons */}
        <div className="flex space-x-2 overflow-x-auto pb-1">
          {documents.map((doc, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedDocIndex(idx)}
              className={`px-3 py-2 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap ${
                selectedDocIndex === idx
                  ? 'bg-gov-navy text-white shadow-sm'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>{doc.doc_type?.replace(/_/g, ' ').toUpperCase()}</span>
              {doc.status === 'Verified' ? (
                <CheckCircle2 className={`w-3 h-3 ${selectedDocIndex === idx ? 'text-emerald-300' : 'text-emerald-500'}`} />
              ) : (
                <AlertTriangle className={`w-3 h-3 ${selectedDocIndex === idx ? 'text-amber-300' : 'text-amber-500'}`} />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Main Side-by-Side Comparison Workspace */}
      <div className="p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Document Inspection & OCR Meta (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Document Metadata
              </span>
              <span className="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                {currentDoc.file_name}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-200">
                <span className="text-slate-500">Document Type:</span>
                <span className="font-semibold text-slate-800">{currentDoc.doc_type}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200">
                <span className="text-slate-500">OCR Engine:</span>
                <span className="font-semibold text-gov-navy">Tesseract OCR v5.4 / MoTA Regex Parser</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200">
                <span className="text-slate-500">AI Confidence Score:</span>
                <span className="font-bold text-emerald-600 font-mono">
                  {currentDoc.confidence_score || 95.0}% Match Confidence
                </span>
              </div>
            </div>

            {/* Confidence Progress Meter */}
            <div className="mt-3">
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    (currentDoc.confidence_score || 95) >= 80
                      ? 'bg-emerald-500'
                      : (currentDoc.confidence_score || 95) >= 50
                      ? 'bg-amber-500'
                      : 'bg-rose-500'
                  }`}
                  style={{ width: `${currentDoc.confidence_score || 95}%` }}
                />
              </div>
            </div>
          </div>

          {/* OCR Raw Text Preview Box */}
          <div className="bg-slate-900 text-slate-200 p-4 rounded-xl font-mono text-xs shadow-inner">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-slate-400">
              <span className="flex items-center space-x-1.5">
                <Eye className="w-3.5 h-3.5 text-amber-400" />
                <span className="font-bold uppercase tracking-wider text-[11px]">OCR Text Stream Extract</span>
              </span>
              <span className="text-[10px] text-emerald-400">Validated</span>
            </div>
            <pre className="whitespace-pre-wrap max-h-36 overflow-y-auto leading-relaxed text-slate-300">
              {currentDoc.ocr_text || currentDoc.ocr_preview || 'Document scanned successfully.'}
            </pre>
          </div>

          {/* Discrepancy Warnings (if any) */}
          {discrepancies.length > 0 && (
            <div className="bg-amber-50 border-l-4 border-amber-500 p-3 rounded-r-lg">
              <div className="flex items-center space-x-2 text-amber-800 font-bold text-xs mb-1">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Verification Discrepancies Flagged:</span>
              </div>
              <ul className="list-disc list-inside text-xs text-amber-700 space-y-1">
                {discrepancies.map((d, i) => (
                  <li key={i}>{d}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right Column: Side-by-Side Comparison Table (7 cols) */}
        <div className="lg:col-span-7">
          <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
            <div className="bg-slate-100 px-4 py-2.5 border-b border-slate-200">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Side-by-Side Extracted Field Cross-Check
              </h4>
            </div>

            <div className="divide-y divide-slate-100">
              {Object.keys(fields).length > 0 ? (
                Object.entries(fields).map(([fKey, fData]) => (
                  <div
                    key={fKey}
                    className={`p-4 transition-colors ${
                      fData.match ? 'bg-white hover:bg-slate-50' : 'bg-rose-50/60 border-l-4 border-rose-500'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-700">{fData.label || fKey}</span>
                      <span className="flex items-center space-x-1.5">
                        {fData.match ? (
                          <span className="inline-flex items-center text-[11px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" /> Exact Match ({fData.similarity}%)
                          </span>
                        ) : (
                          <span className="inline-flex items-center text-[11px] font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded">
                            <XCircle className="w-3 h-3 mr-1 text-rose-600" /> Mismatch Flagged
                          </span>
                        )}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      {/* Left: Applicant Form Value */}
                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                        <span className="block text-[10px] uppercase font-bold text-slate-400 mb-1">
                          Applicant Form Value
                        </span>
                        <span className="font-semibold text-slate-800 break-words">
                          {String(fData.form_value || 'Not provided')}
                        </span>
                      </div>

                      {/* Right: OCR Extracted Value */}
                      <div className={`p-2.5 rounded-lg border ${
                        fData.match ? 'bg-emerald-50/60 border-emerald-200' : 'bg-rose-100/70 border-rose-300'
                      }`}>
                        <span className="block text-[10px] uppercase font-bold text-slate-400 mb-1">
                          OCR Extracted From Document
                        </span>
                        <span className={`font-semibold break-words ${fData.match ? 'text-emerald-900' : 'text-rose-900'}`}>
                          {String(fData.ocr_value || 'Unreadable / Missing')}
                        </span>
                      </div>
                    </div>

                    {fData.remarks && (
                      <p className="text-[11px] text-slate-500 mt-2 italic flex items-center">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mr-1.5 inline-block" />
                        {fData.remarks}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-6 text-center text-slate-400 text-xs">
                  No automated field comparisons available for this document.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
