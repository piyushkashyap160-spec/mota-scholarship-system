import React, { useState } from 'react';
import { Upload, CheckCircle2, AlertTriangle, FileText, Loader2, Sparkles, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import StatusBadge from './StatusBadge';

export default function DocumentUploader({ docDef, formHints, onScanComplete, existingDoc = null }) {
  const [scanning, setScanning] = useState(false);
  const [docResult, setDocResult] = useState(existingDoc);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    if (!file) return;
    setScanning(true);
    setError(null);
    try {
      const res = await api.documents.scan(docDef.doc_type, formHints, file);
      setDocResult(res);
      if (onScanComplete) {
        onScanComplete(docDef.doc_type, res);
      }
    } catch (err) {
      setError(err.message || 'Failed to scan and verify document');
    } finally {
      setScanning(false);
    }
  };

  // 1-Click Demo Document Generator (Generates a virtual valid, field mismatch, or deliberate wrong-slot document)
  const handleQuickDemoDoc = async (mode = 'valid') => {
    setScanning(true);
    setError(null);
    try {
      let dummyContent = '';
      if (mode === 'wrong_slot') {
        // Deliberately generate text of an entirely different document type
        if (docDef.doc_type === 'st_certificate') {
          dummyContent = `REVENUE AND LAND REFORMS DEPARTMENT\nGOVERNMENT OF JHARKHAND\nOFFICE OF THE TAHSILDAR\nANNUAL INCOME CERTIFICATE\nGross Annual Family Income from all sources is Rs. 2,40,000/- per annum.\nFinancial Year 2024-2025. Circle Officer Seal.`;
        } else {
          dummyContent = `GOVERNMENT OF JHARKHAND\nOFFICE OF THE SUB-DIVISIONAL OFFICER\nSCHEDULED TRIBE CASTE CERTIFICATE\nThis is to certify that candidate belongs to the Santhal community which is recognized as a Scheduled Tribe under The Constitution (Scheduled Tribes) Order 1950. SDO Seal.`;
        }
      } else if (mode === 'field_mismatch') {
        dummyContent = `GOVERNMENT CERTIFICATE\nType: ${docDef.title}\nCandidate Name: Unknown Person\nAnnual Income: Rs. 9,50,000\nMarks: 49.0%`;
      } else {
        dummyContent = `GOVERNMENT OF INDIA\nMinistry of Tribal Affairs Verified Document\nType: ${docDef.title}\nCandidate Name: ${formHints.full_name || 'Tribal Scholar'}\nCertificate No: ${formHints.st_cert_number || 'ST/2024/7810'}\nAnnual Income: Rs. ${formHints.annual_income || 250000}\nMarks: ${formHints.marks_percentage || 75.5}%`;
      }

      const blob = new Blob([dummyContent], { type: 'text/plain' });
      const file = new File([blob], `${docDef.doc_type}_sample.txt`, { type: 'text/plain' });
      const res = await api.documents.scan(docDef.doc_type, formHints, file);
      setDocResult(res);
      if (onScanComplete) {
        onScanComplete(docDef.doc_type, res);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm transition-all hover:border-slate-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-bold text-slate-800">{docDef.title}</span>
            {docDef.required && <span className="text-xs font-bold text-rose-500">*Required</span>}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{docDef.description}</p>
        </div>

        {docResult && (
          <div className="flex items-center space-x-2">
            {docResult.slot_match === false && (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                Slot Mismatch
              </span>
            )}
            <StatusBadge status={docResult.status} />
          </div>
        )}
      </div>

      {/* Upload Box */}
      {!docResult ? (
        <div className="mt-2 border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-gov-navy transition-all bg-slate-50/50">
          {scanning ? (
            <div className="py-4 space-y-2">
              <Loader2 className="w-8 h-8 mx-auto text-gov-navy animate-spin" />
              <p className="text-xs font-bold text-slate-700">Tesseract OCR & Doc Classification In Progress...</p>
              <p className="text-[11px] text-slate-500">Extracting fields, verifying slot category, and scanning quality</p>
            </div>
          ) : (
            <div>
              <Upload className="w-8 h-8 mx-auto text-slate-400 mb-2" />
              <label className="cursor-pointer">
                <span className="text-xs font-bold text-gov-navy hover:underline">Click to upload file</span>
                <span className="text-xs text-slate-500"> or drag and drop</span>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.txt"
                  className="hidden"
                  onChange={(e) => handleFileUpload(e.target.files[0])}
                />
              </label>
              <p className="text-[11px] text-slate-400 mt-1">PDF, JPG, PNG up to 10MB</p>

              {/* Demo Assist Buttons for Judging */}
              <div className="mt-4 pt-3 border-t border-slate-200 flex flex-wrap items-center justify-center gap-2">
                <span className="text-[11px] font-medium text-slate-500">Test AI Scanner:</span>
                <button
                  type="button"
                  onClick={() => handleQuickDemoDoc('valid')}
                  className="px-2.5 py-1 text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-300 rounded hover:bg-emerald-100 transition-colors flex items-center space-x-1"
                >
                  <Sparkles className="w-3 h-3 text-emerald-600" />
                  <span>Attach Valid Sample</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoDoc('wrong_slot')}
                  className="px-2.5 py-1 text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-300 rounded hover:bg-amber-100 transition-colors flex items-center space-x-1"
                >
                  <AlertTriangle className="w-3 h-3 text-amber-600" />
                  <span>Simulate Wrong Slot</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoDoc('field_mismatch')}
                  className="px-2.5 py-1 text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-300 rounded hover:bg-rose-100 transition-colors flex items-center space-x-1"
                >
                  <span>Simulate Discrepancy</span>
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Scanned Result Preview */
        <div className="mt-3 bg-slate-50 border border-slate-200 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white rounded-lg border border-slate-200 shadow-sm text-gov-navy">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-800">{docResult.file_name}</span>
                <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-500 mt-0.5">
                  <span>Confidence: {docResult.confidence_score || 95}%</span>
                  <span>•</span>
                  <span className="text-emerald-600 font-semibold">OCR Processed</span>
                  {docResult.predicted_label && (
                    <>
                      <span>•</span>
                      <span className="px-1.5 py-0.5 bg-slate-200 text-slate-700 rounded font-medium text-[10px]">
                        Detected: {docResult.predicted_label}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <label className="cursor-pointer text-xs font-semibold text-gov-navy hover:underline flex items-center space-x-1">
              <RefreshCw className="w-3 h-3" />
              <span>Change File</span>
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.txt"
                className="hidden"
                onChange={(e) => handleFileUpload(e.target.files[0])}
              />
            </label>
          </div>

          {/* Slot Mismatch Warning Banner (Priority 2) */}
          {docResult.mismatch_warning && (
            <div className="mt-3 p-3 rounded-lg bg-amber-50 border border-amber-300 flex items-start space-x-2.5 text-amber-900">
              <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
              <div>
                <span className="font-bold text-xs block text-amber-900">Document Type Slot Mismatch</span>
                <p className="text-[11px] text-amber-800 mt-0.5 leading-relaxed">{docResult.mismatch_warning}</p>
              </div>
            </div>
          )}

          {/* Quick Extracted Fields Summary Chips */}
          {docResult.extracted_data && (
            <div className="mt-3 pt-3 border-t border-slate-200 grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(docResult.extracted_data).map(([k, v]) => (
                <div key={k} className="bg-white p-2 rounded border border-slate-200 text-[11px]">
                  <span className="block text-[10px] text-slate-400 uppercase font-bold">{k.replace(/_/g, ' ')}</span>
                  <span className="font-semibold text-slate-800 truncate block">{String(v || 'N/A')}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {error && <p className="text-xs text-rose-500 font-medium mt-2">{error}</p>}
    </div>
  );
}
