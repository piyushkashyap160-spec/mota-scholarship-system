import React, { useState } from 'react';
import { X, RefreshCw, FileText, CheckCircle2, AlertCircle, Building2, BookOpen, User, CheckSquare } from 'lucide-react';
import { api } from '../api/client';

export default function RenewalModal({ isOpen, onClose, application, onRenewalSuccess }) {
  const [progressReport, setProgressReport] = useState('');
  const [currentYearSemester, setCurrentYearSemester] = useState('Year 2 (Semester 3-4)');
  const [continuationInstitution, setContinuationInstitution] = useState(
    application?.form_data?.institution || application?.form_data?.institute_name || ''
  );
  const [continuationCourse, setContinuationCourse] = useState(
    application?.form_data?.course || application?.form_data?.degree || 'Ph.D.'
  );
  const [supervisorGuideName, setSupervisorGuideName] = useState('');
  const [marksOrGrade, setMarksOrGrade] = useState('Satisfactory (A Grade)');
  const [bankAccountConfirmed, setBankAccountConfirmed] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen || !application) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!progressReport.trim()) {
      setError('Please provide a detailed annual progress report.');
      return;
    }
    if (!bankAccountConfirmed) {
      setError('Please confirm that your active bank account is linked.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const payload = {
        progress_report: progressReport,
        continuation_institution: continuationInstitution,
        continuation_course: continuationCourse,
        bank_account_confirmed: bankAccountConfirmed,
        current_year_semester: currentYearSemester,
        supervisor_guide_name: supervisorGuideName,
        marks_or_grade: marksOrGrade,
      };

      await api.applications.applyRenewal(application.id, payload);
      if (onRenewalSuccess) {
        onRenewalSuccess();
      }
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to submit fellowship renewal application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-blue-50 text-gov-navy rounded-xl">
              <RefreshCw className="w-5 h-5 text-gov-navy" />
            </div>
            <div>
              <h3 className="text-base font-bold text-gov-navy">Fellowship Renewal Application</h3>
              <p className="text-xs text-slate-500">
                Annual Continuation for {application.scheme?.name || application.scheme?.code} ({application.application_number})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div className="bg-blue-50/70 p-3 rounded-xl border border-blue-100 flex items-center justify-between">
            <div>
              <span className="text-slate-500 block">Current Fellowship Due Date:</span>
              <strong className="text-gov-navy font-mono text-sm">
                {application.renewal_due_date || 'Due this academic term'}
              </strong>
            </div>
            <span className="px-2.5 py-1 bg-blue-100 text-blue-900 font-bold rounded-lg text-[11px]">
              Continuation Cycle
            </span>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Current Academic Year / Semester <span className="text-rose-500">*</span>
            </label>
            <select
              value={currentYearSemester}
              onChange={(e) => setCurrentYearSemester(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-hidden text-xs bg-white"
            >
              <option value="Year 2 (Semester 3-4)">Year 2 (Semester 3-4)</option>
              <option value="Year 3 (Semester 5-6)">Year 3 (Semester 5-6)</option>
              <option value="Year 4 (Semester 7-8)">Year 4 (Semester 7-8)</option>
              <option value="Year 5 (Semester 9-10)">Year 5 (Semester 9-10)</option>
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-slate-700 mb-1 flex items-center space-x-1">
                <Building2 className="w-3.5 h-3.5 text-slate-500" />
                <span>Enrolled Institution</span>
              </label>
              <input
                type="text"
                value={continuationInstitution}
                onChange={(e) => setContinuationInstitution(e.target.value)}
                required
                className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-hidden text-xs"
                placeholder="e.g. IIT Delhi / Central University"
              />
            </div>
            <div>
              <label className="block font-bold text-slate-700 mb-1 flex items-center space-x-1">
                <BookOpen className="w-3.5 h-3.5 text-slate-500" />
                <span>Ongoing Course/Degree</span>
              </label>
              <input
                type="text"
                value={continuationCourse}
                onChange={(e) => setContinuationCourse(e.target.value)}
                required
                className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-hidden text-xs"
                placeholder="e.g. Ph.D. in Tribal Studies"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-slate-700 mb-1 flex items-center space-x-1">
                <User className="w-3.5 h-3.5 text-slate-500" />
                <span>Research Supervisor / Guide</span>
              </label>
              <input
                type="text"
                value={supervisorGuideName}
                onChange={(e) => setSupervisorGuideName(e.target.value)}
                placeholder="Prof. / Dr. Name & Dept."
                className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-hidden text-xs"
              />
            </div>
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Recent Grade / Performance Assessment
              </label>
              <input
                type="text"
                value={marksOrGrade}
                onChange={(e) => setMarksOrGrade(e.target.value)}
                placeholder="e.g. CGPA 8.5 / Satisfactory"
                className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-hidden text-xs"
              />
            </div>
          </div>

          <div>
            <label className="block font-bold text-slate-700 mb-1">
              Annual Academic Progress Report & Research Milestones <span className="text-rose-500">*</span>
            </label>
            <textarea
              rows={4}
              value={progressReport}
              onChange={(e) => setProgressReport(e.target.value)}
              placeholder="Detail your research progress, courses completed, papers published, fieldwork conducted, or thesis chapters submitted during the preceding academic year..."
              className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-hidden text-xs"
              required
            />
          </div>

          <div className="pt-2">
            <label className="flex items-start space-x-2.5 cursor-pointer bg-slate-50 p-3 rounded-xl border border-slate-200 hover:bg-slate-100 transition-colors">
              <input
                type="checkbox"
                checked={bankAccountConfirmed}
                onChange={(e) => setBankAccountConfirmed(e.target.checked)}
                className="mt-0.5 rounded text-gov-navy focus:ring-blue-500 h-4 w-4"
              />
              <span className="text-xs text-slate-700 leading-snug">
                I hereby declare that I am actively continuing regular full-time studies/research at the above institution and that my bank account registered with MoTA DBT / PFMS remains valid and operative.
              </span>
            </label>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-xl shadow transition-colors flex items-center space-x-2"
            >
              {loading ? (
                <span>Submitting Renewal...</span>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span>Submit Renewal Application</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
