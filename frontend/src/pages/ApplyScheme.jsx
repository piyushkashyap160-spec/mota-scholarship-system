import React, { useState, useEffect } from 'react';
import { Award, ArrowLeft, ArrowRight, ShieldCheck, CheckCircle2, AlertTriangle, FileText, Send, Sparkles, Loader2 } from 'lucide-react';
import { api } from '../api/client';
import DynamicFormRenderer from '../components/DynamicFormRenderer';
import DocumentUploader from '../components/DocumentUploader';
import SideBySideOcrViewer from '../components/SideBySideOcrViewer';

export default function ApplyScheme({ schemeId, onBack, onSuccess, currentUser }) {
  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Form data state
  const [formData, setFormData] = useState({
    full_name: currentUser?.full_name || 'Birsa Soren',
    st_cert_number: currentUser?.st_cert_number || 'ST/JH/2024/9021',
    state: currentUser?.state || 'Jharkhand',
    community_tribe: currentUser?.community_tribe || 'Santhal',
    category: 'ST',
    annual_income: 260000,
    marks_percentage: 72.5,
    institution: currentUser?.institution || 'Central University of Jharkhand',
    course: currentUser?.course || 'Ph.D. in Tribal Heritage & Sustainable Sciences',
    bank_account_no: '308940029812',
    bank_ifsc: 'SBIN0001234',
    bank_name: 'State Bank of India',
    father_name: 'Budhan Soren',
    dob: '1998-08-15',
    gender: 'Male',
    phone: currentUser?.phone || '+91-98765-43210',
  });

  // Scanned documents state
  const [scannedDocs, setScannedDocs] = useState({});
  const [step, setStep] = useState(1); // 1: Form Fields, 2: Document Uploads & AI Verification, 3: Review & Submit

  useEffect(() => {
    async function fetchScheme() {
      try {
        const data = await api.schemes.getById(schemeId);
        setScheme(data);
      } catch (err) {
        setError(err.message || 'Failed to load scheme details');
      } finally {
        setLoading(false);
      }
    }
    fetchScheme();
  }, [schemeId]);

  const handleDocumentScanned = (docType, scanResult) => {
    setScannedDocs((prev) => ({
      ...prev,
      [docType]: scanResult,
    }));
  };

  const handleSubmitApplication = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const documentsList = Object.values(scannedDocs);
      const payload = {
        scheme_id: scheme.id,
        form_data: formData,
        documents: documentsList,
      };

      const result = await api.applications.submit(payload);
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      setError(err.message || 'Failed to submit application');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="py-12 text-center text-slate-500">Loading scheme configuration...</div>;
  }

  if (!scheme) {
    return <div className="py-12 text-center text-rose-500">Scheme not found.</div>;
  }

  const reqDocs = scheme.required_documents || [];
  const scannedCount = Object.keys(scannedDocs).length;
  const allDocsScanned = reqDocs.length > 0 && scannedCount >= reqDocs.length;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Top Bar with Back button */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="px-3 py-1.5 text-xs font-bold text-gov-navy hover:bg-slate-100 rounded-lg flex items-center space-x-1 transition-colors border border-slate-200"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Schemes</span>
        </button>

        <span className="text-xs font-bold text-slate-500">
          Step {step} of 3
        </span>
      </div>

      {/* Scheme Application Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 bg-gov-navy text-white text-xs font-bold rounded uppercase">
              {scheme.code}
            </span>
            <span className="text-xs text-slate-500 font-semibold">Scholarship Application Wizard</span>
          </div>
          <h1 className="text-xl font-bold text-gov-navy mt-1">{scheme.name}</h1>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic Form Renderer: Configured automatically according to MoTA scheme specifications.
          </p>
        </div>

        {/* Step Indicator Tabs */}
        <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-bold">
          <button
            onClick={() => setStep(1)}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              step === 1 ? 'bg-gov-navy text-white shadow' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            1. Form Fields
          </button>
          <button
            onClick={() => setStep(2)}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              step === 2 ? 'bg-gov-navy text-white shadow' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            2. AI Document Scan
          </button>
          <button
            onClick={() => setStep(3)}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              step === 3 ? 'bg-gov-navy text-white shadow' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            3. Review & Submit
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 p-4 rounded-xl text-xs flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* STEP 1: DYNAMIC FORM FIELDS */}
      {step === 1 && (
        <div className="space-y-6">
          <DynamicFormRenderer
            scheme={scheme}
            formData={formData}
            onChange={setFormData}
          />

          <div className="flex justify-end pt-4">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="px-6 py-3 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-xl text-xs flex items-center space-x-2 shadow transition-all"
            >
              <span>Proceed to Document Upload & AI Verification</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: DOCUMENT UPLOAD & AI OCR VERIFICATION */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl text-xs text-gov-navy flex items-start space-x-3">
            <Sparkles className="w-5 h-5 flex-shrink-0 mt-0.5 text-gov-navy" />
            <div>
              <p className="font-bold">AI-Assisted Document Pre-Verification Active</p>
              <p className="mt-0.5 text-slate-600">
                Upload your required certificates below. Tesseract OCR will automatically extract key parameters
                (caste certificate numbers, annual income, marks percentage) and match them against the information
                you entered in Step 1.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {reqDocs.map((docDef) => (
              <DocumentUploader
                key={docDef.doc_type}
                docDef={docDef}
                formHints={formData}
                existingDoc={scannedDocs[docDef.doc_type]}
                onScanComplete={handleDocumentScanned}
              />
            ))}
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="px-4 py-2 border border-slate-300 text-slate-700 font-bold rounded-xl text-xs hover:bg-slate-100 transition-colors"
            >
              Back to Form
            </button>

            <button
              type="button"
              onClick={() => setStep(3)}
              className="px-6 py-3 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-xl text-xs flex items-center space-x-2 shadow transition-all"
            >
              <span>Review Verification Discrepancy Matrix</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: REVIEW & SUBMISSION WITH SIDE-BY-SIDE OCR MATRIX */}
      {step === 3 && (
        <div className="space-y-6">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
            <h3 className="font-bold text-slate-800 text-sm mb-1">Pre-Submission Verification Summary</h3>
            <p className="text-slate-600">
              Inspect the AI comparison matrix below. If any discrepancies are flagged, you may review your values
              prior to formal submission to the Ministry Scrutiny Committee.
            </p>
          </div>

          {/* Side-by-side OCR comparison */}
          <SideBySideOcrViewer documents={Object.values(scannedDocs)} readOnly={true} />

          <div className="flex items-center justify-between pt-6 border-t border-slate-200">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="px-4 py-2 border border-slate-300 text-slate-700 font-bold rounded-xl text-xs hover:bg-slate-100 transition-colors"
            >
              Back to Documents
            </button>

            <button
              type="button"
              disabled={submitting}
              onClick={handleSubmitApplication}
              className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold rounded-xl text-xs flex items-center space-x-2 shadow-lg transition-all"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Submitting to Ministry Desk...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Application to Ministry of Tribal Affairs</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
