import React, { useState, useEffect } from 'react';
import { Building2, CheckCircle2, Clock, XCircle, ShieldCheck, UserCheck, Search, Filter, AlertCircle, RefreshCw, ChevronRight, FileText, Check, X } from 'lucide-react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';

export default function InstitutionDashboard({ currentUser }) {
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedApp, setSelectedApp] = useState(null); // For verification modal
  const [verifying, setVerifying] = useState(false);
  
  // Modal form state
  const [isEnrolled, setIsEnrolled] = useState(true);
  const [enrollmentNumber, setEnrollmentNumber] = useState('');
  const [remarks, setRemarks] = useState('');
  const [verifError, setVerifError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, appsData] = await Promise.all([
        api.institution.getStats(),
        api.institution.getApplications(),
      ]);
      setStats(statsData);
      setApplications(appsData);
    } catch (err) {
      console.error('Failed to load institution dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openVerifyModal = (app) => {
    setSelectedApp(app);
    setIsEnrolled(app.enrollment_verified !== false);
    const existingEnroll = (app.form_data || {}).get?.('enrollment_number') ||
      app.form_data?.enrollment_number ||
      app.form_data?.roll_number ||
      app.form_data?.registration_no ||
      '';
    setEnrollmentNumber(existingEnroll);
    setRemarks(app.enrollment_verified ? 'Verified active regular scholar.' : '');
    setVerifError(null);
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    if (!selectedApp) return;

    setVerifying(true);
    setVerifError(null);
    try {
      await api.institution.verifyEnrollment(selectedApp.id, {
        enrolled: isEnrolled,
        enrollment_number: enrollmentNumber,
        remarks: remarks.trim() || (isEnrolled ? 'Confirmed regular full-time enrolled student.' : 'Student not on active institutional rolls.'),
      });

      setSelectedApp(null);
      await loadData();
    } catch (err) {
      setVerifError(err.message || 'Failed to submit verification');
    } finally {
      setVerifying(false);
    }
  };

  const filteredApps = applications.filter((app) => {
    const s = search.toLowerCase();
    const matchesSearch =
      !search ||
      app.application_number.toLowerCase().includes(s) ||
      (app.applicant?.full_name || '').toLowerCase().includes(s) ||
      (app.scheme?.name || '').toLowerCase().includes(s) ||
      (app.form_data?.course || '').toLowerCase().includes(s);

    let matchesFilter = true;
    if (statusFilter === 'VERIFIED') matchesFilter = app.enrollment_verified;
    if (statusFilter === 'PENDING') matchesFilter = !app.enrollment_verified && app.status !== 'Needs Review';
    if (statusFilter === 'FLAGGED') matchesFilter = !app.enrollment_verified && app.status === 'Needs Review';

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-8 pb-16">
      {/* Institutional Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-900 text-white flex items-center justify-center font-extrabold text-xl shadow">
            <Building2 className="w-7 h-7 text-indigo-200" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-gov-navy">
                {stats?.institution_name || currentUser?.institution_name || 'University Nodal Desk'}
              </h2>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-100 text-indigo-900 border border-indigo-200">
                Authorized Nodal Officer
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Designated Officer: <strong className="text-slate-700">{currentUser?.full_name || stats?.officer_name}</strong> • Official Email: <strong className="text-slate-700">{currentUser?.email}</strong>
            </p>
          </div>
        </div>

        <button
          onClick={loadData}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors flex items-center space-x-1.5 self-start md:self-center"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Total Scholars</span>
            <Building2 className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-black text-slate-900 mt-2">
            {stats?.total_applications ?? applications.length}
          </div>
          <span className="text-[11px] text-slate-400">Assigned from your institution</span>
        </div>

        <div className="bg-emerald-50/70 p-5 rounded-2xl border border-emerald-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-800">Enrollment Verified</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-emerald-950 mt-2">
            {stats?.verified_count ?? 0}
          </div>
          <span className="text-[11px] text-emerald-700">Cleared for Ministry scrutiny</span>
        </div>

        <div className="bg-amber-50/70 p-5 rounded-2xl border border-amber-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-800">Pending Verification</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black text-amber-950 mt-2">
            {stats?.pending_count ?? 0}
          </div>
          <span className="text-[11px] text-amber-700">Awaiting your institutional sign-off</span>
        </div>

        <div className="bg-rose-50/70 p-5 rounded-2xl border border-rose-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-800">Discontinued / Flagged</span>
            <XCircle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-black text-rose-950 mt-2">
            {stats?.rejected_count ?? 0}
          </div>
          <span className="text-[11px] text-rose-700">Reported unverified/deficient</span>
        </div>
      </div>

      {/* Main Student Verification Queue */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Table Filters & Search */}
        <div className="p-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-slate-50/50">
          <div className="flex items-center space-x-2">
            <UserCheck className="w-4 h-4 text-indigo-700" />
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Student Enrollment Verification Queue
            </h3>
            <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded-full text-[10px] font-bold">
              {filteredApps.length}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search student, app ID, course..."
                className="pl-8 pr-3 py-1.5 bg-white border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-hidden w-56"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
            >
              <option value="ALL">All Statuses</option>
              <option value="PENDING">Pending Sign-off</option>
              <option value="VERIFIED">Institution Verified</option>
              <option value="FLAGGED">Flagged / Deficient</option>
            </select>
          </div>
        </div>

        {/* Applications Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Student & Category</th>
                <th className="px-4 py-3">Scheme & App #</th>
                <th className="px-4 py-3">Course & Degree</th>
                <th className="px-4 py-3">Submission Date</th>
                <th className="px-4 py-3">Nodal Status</th>
                <th className="px-4 py-3">Ministry Stage</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredApps.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-slate-400">
                    No applications matching the search criteria found.
                  </td>
                </tr>
              ) : (
                filteredApps.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-4 py-3.5">
                      <div className="font-bold text-slate-900">{app.applicant?.full_name || 'N/A'}</div>
                      <div className="text-[11px] text-slate-500 flex items-center space-x-1.5 mt-0.5">
                        <span className="font-semibold text-slate-700">{app.applicant?.community_tribe || 'ST'}</span>
                        <span>•</span>
                        <span>{app.applicant?.state || 'Jharkhand'}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="font-mono font-bold text-gov-navy">{app.application_number}</div>
                      <div className="text-[11px] text-slate-600 font-medium mt-0.5">
                        {app.scheme?.code || 'MoTA Scheme'}
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="font-semibold text-slate-800">
                        {app.form_data?.course || app.form_data?.degree || 'Ph.D. Program'}
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5 font-mono">
                        Roll: {app.form_data?.roll_number || app.form_data?.enrollment_number || 'N/A'}
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-slate-600">
                      {new Date(app.submission_date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3.5">
                      {app.enrollment_verified ? (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                          <Check className="w-3 h-3 text-emerald-700" />
                          <span>Institution Verified</span>
                        </span>
                      ) : app.status === 'Needs Review' ? (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                          <X className="w-3 h-3 text-rose-700" />
                          <span>Not Enrolled</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                          <Clock className="w-3 h-3 text-amber-700" />
                          <span>Pending Sign-off</span>
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        onClick={() => openVerifyModal(app)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-xs inline-flex items-center space-x-1 ${
                          app.enrollment_verified
                            ? 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                            : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow'
                        }`}
                      >
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>{app.enrollment_verified ? 'Update Verification' : 'Verify Enrollment'}</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* VERIFY ENROLLMENT MODAL */}
      {selectedApp && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-indigo-50 text-indigo-700 rounded-xl">
                  <ShieldCheck className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Institution Enrollment Verification</h3>
                  <p className="text-xs text-slate-500">
                    Official sign-off for application {selectedApp.application_number}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedApp(null)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {verifError && (
              <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{verifError}</span>
              </div>
            )}

            {/* Student Claimed Details Card */}
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs space-y-2 mb-4">
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Scholar Name:</span>
                <strong className="text-slate-900">{selectedApp.applicant?.full_name}</strong>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Scheme:</span>
                <strong className="text-slate-900">{selectedApp.scheme?.name}</strong>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Enrolled Degree / Course:</span>
                <strong className="text-slate-900">
                  {selectedApp.form_data?.course || selectedApp.form_data?.degree || 'Ph.D.'}
                </strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">University / College:</span>
                <strong className="text-indigo-900">
                  {stats?.institution_name || selectedApp.form_data?.institution}
                </strong>
              </div>
            </div>

            <form onSubmit={handleVerifySubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-2">
                  Enrollment Verification Decision <span className="text-rose-500">*</span>
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <label
                    className={`flex items-center space-x-2.5 p-3 rounded-xl border cursor-pointer transition-all ${
                      isEnrolled
                        ? 'border-emerald-500 bg-emerald-50/70 text-emerald-950 font-bold'
                        : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="enrolled_choice"
                      checked={isEnrolled}
                      onChange={() => setIsEnrolled(true)}
                      className="text-emerald-600 focus:ring-emerald-500 h-4 w-4"
                    />
                    <span>Confirmed Enrolled</span>
                  </label>

                  <label
                    className={`flex items-center space-x-2.5 p-3 rounded-xl border cursor-pointer transition-all ${
                      !isEnrolled
                        ? 'border-rose-500 bg-rose-50/70 text-rose-950 font-bold'
                        : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="enrolled_choice"
                      checked={!isEnrolled}
                      onChange={() => setIsEnrolled(false)}
                      className="text-rose-600 focus:ring-rose-500 h-4 w-4"
                    />
                    <span>Not Enrolled / Discontinued</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Institutional Roll / Registration / Enrollment Number
                </label>
                <input
                  type="text"
                  value={enrollmentNumber}
                  onChange={(e) => setEnrollmentNumber(e.target.value)}
                  placeholder="e.g. 2023PHD0102 / CUJ/2023/ST/041"
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden text-xs font-mono"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Nodal Officer Remarks / Authentication Notes
                </label>
                <textarea
                  rows={3}
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder={
                    isEnrolled
                      ? 'e.g. Verified against Department Admission Register; student is enrolled in full-time regular Ph.D.'
                      : 'e.g. Student record not found in institutional register / discontinued in Dec 2025.'
                  }
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden text-xs"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSelectedApp(null)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={verifying}
                  className={`px-5 py-2.5 rounded-xl font-bold text-white shadow transition-all flex items-center space-x-2 ${
                    isEnrolled
                      ? 'bg-emerald-600 hover:bg-emerald-700'
                      : 'bg-rose-600 hover:bg-rose-700'
                  }`}
                >
                  {verifying ? (
                    <span>Submitting...</span>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      <span>{isEnrolled ? 'Confirm Enrollment' : 'Report Non-Enrollment'}</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
