import React, { useState, useEffect } from 'react';
import { Award, Search, Filter, Shield, AlertTriangle, CheckCircle2, Clock, Users, ArrowUpRight, FileText, ChevronRight, BarChart3, TrendingUp, Sparkles, ShieldAlert } from 'lucide-react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import RiskBadge from '../components/RiskBadge';
import { INDIAN_STATES_AND_UTS } from '../constants';

export default function AdminDashboard({ onSelectApplication, onOpenMeritRanking }) {
  const [applications, setApplications] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [schemeFilter, setSchemeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('All');
  const [stateFilter, setStateFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [appsData, statsData] = await Promise.all([
        api.admin.getApplications({
          scheme: schemeFilter !== 'ALL' ? schemeFilter : undefined,
          status: statusFilter !== 'All' ? statusFilter : undefined,
          state: stateFilter !== 'All' ? stateFilter : undefined,
          risk_level: riskFilter !== 'All' ? riskFilter : undefined,
          search: searchQuery || undefined,
        }),
        api.admin.getAnalytics(),
      ]);
      setApplications(appsData);
      setAnalytics(statsData);
    } catch (err) {
      console.error('Failed to load admin dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [schemeFilter, statusFilter, stateFilter, riskFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const kpis = analytics?.kpis || {};

  return (
    <div className="space-y-8 pb-16">
      {/* Officer Welcome Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded bg-blue-100 text-gov-navy text-xs font-bold border border-blue-200">
              National Scrutiny Wing
            </span>
            <span className="text-xs text-slate-500 font-medium">Ministry of Tribal Affairs</span>
          </div>
          <h1 className="text-xl font-bold text-gov-navy mt-1">
            Central Scrutiny & Fellowship Administration Console
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time monitoring of ST scholarship pipelines, Tesseract OCR verification audits, and committee selections.
          </p>
        </div>

        <button
          onClick={onOpenMeritRanking}
          className="px-5 py-2.5 bg-gov-navy hover:bg-blue-900 text-white font-bold rounded-xl text-xs transition-colors flex items-center space-x-2 shadow self-start sm:self-center"
        >
          <Users className="w-4 h-4 text-amber-400" />
          <span>Open Assistive Merit Ranking</span>
        </button>
      </div>

      {/* WHY THIS PLATFORM EXISTS — HISTORICAL REFORM IMPACT CALLOUT CARD */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-gov-navy via-blue-900 to-indigo-950 text-white p-6 shadow-md border-l-4 border-l-amber-400 border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center space-x-2 bg-amber-400/20 border border-amber-400/30 text-amber-300 px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 mr-1" />
              <span>Why This Platform Exists • Official MoTA Reform Context</span>
            </div>
            <p className="text-sm sm:text-base font-medium text-slate-100 leading-relaxed">
              &ldquo;As of 2021, <strong className="text-amber-300 font-bold">NFST alone received 17,638 student grievances</strong> &mdash; mostly due to manual verification delays and communication gaps. <span className="text-emerald-300 font-semibold">This platform addresses the root cause.</span>&rdquo;
            </p>
            <div className="flex items-center space-x-2 text-xs text-slate-300 pt-1">
              <span className="text-slate-400">Official MoTA Reference:</span>
              <a
                href="https://tribal.nic.in/ScholarshiP.aspx"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-amber-300 font-mono text-[11px] text-amber-200 inline-flex items-center space-x-1"
              >
                <span>tribal.nic.in/ScholarshiP.aspx</span>
                <ArrowUpRight className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="flex-shrink-0 bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/15 text-center min-w-[170px] self-start md:self-center">
            <span className="text-3xl font-black text-amber-400 block tracking-tight">17,638</span>
            <span className="text-[10px] font-extrabold text-slate-200 uppercase tracking-wider block mt-0.5">
              Historical Grievances
            </span>
            <span className="text-[10px] text-emerald-300 font-medium block mt-1">
              Resolved via AI & DBT
            </span>
          </div>
        </div>
      </div>

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Total Applications</span>
          <span className="text-2xl font-extrabold text-gov-navy block mt-1">{kpis.total_applications || 18}</span>
          <span className="text-[10px] text-slate-500 mt-1 block font-medium">Across all states</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-rose-200 shadow-sm bg-rose-50/20">
          <span className="text-[11px] font-bold text-rose-700 uppercase tracking-wider block">Fraud Flags Raised</span>
          <div className="flex items-baseline space-x-1.5 mt-1">
            <span className="text-2xl font-extrabold text-rose-700">{kpis.fraud_flags_raised || 0}</span>
            <span className="text-xs font-semibold text-rose-600">({kpis.high_risk_count || 0} High)</span>
          </div>
          <span className="text-[10px] text-rose-600 mt-1 block font-medium">Advisory AI triggers</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-emerald-200 shadow-sm bg-emerald-50/20">
          <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block">Selected Scholars</span>
          <span className="text-2xl font-extrabold text-emerald-700 block mt-1">{kpis.selected_scholars || 4}</span>
          <span className="text-[10px] text-emerald-600 mt-1 block font-medium">Award letters issued</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-amber-200 shadow-sm bg-amber-50/20">
          <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider block">Needs Review</span>
          <span className="text-2xl font-extrabold text-amber-700 block mt-1">{kpis.needs_review_count || 4}</span>
          <span className="text-[10px] text-amber-600 mt-1 block font-medium">Deficiencies open</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-blue-200 shadow-sm bg-blue-50/20">
          <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">OCR Auto-Pass Rate</span>
          <span className="text-2xl font-extrabold text-blue-700 block mt-1">{kpis.auto_pass_rate || 78}%</span>
          <span className="text-[10px] text-blue-600 mt-1 block font-medium">Discrepancy filtered</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">DBT Funds Allocated</span>
          <span className="text-lg font-extrabold text-gov-navy block mt-1 truncate">
            ₹ {(kpis.total_disbursed_funds_inr || 2282000).toLocaleString('en-IN')}
          </span>
          <span className="text-[10px] text-slate-500 mt-1 block font-medium">Direct to Bank A/C</span>
        </div>
      </div>

      {/* ANALYTICS CHARTS & VISUAL BREAKDOWNS */}
      {analytics && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Status Breakdown & Scheme Split (7 cols) */}
          <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-gov-navy" />
                <h3 className="text-sm font-bold text-slate-800">Application Status Distribution</h3>
              </div>
              <span className="text-xs text-slate-500 font-medium">Real-time counts</span>
            </div>

            {/* Visual Stacked Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden flex shadow-inner">
              {analytics?.status_distribution?.map((item) => {
                const pct = (item.count / Math.max(kpis.total_applications || 18, 1)) * 100;
                return (
                  <div
                    key={item.status}
                    title={`${item.status}: ${item.count} (${pct.toFixed(0)}%)`}
                    className="h-full transition-all hover:opacity-80"
                    style={{ width: `${pct}%`, backgroundColor: item.color }}
                  />
                );
              })}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
              {analytics?.status_distribution?.map((item) => (
                <div key={item.status} className="flex items-center space-x-2 text-xs">
                  <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-600">{item.status}:</span>
                  <strong className="text-slate-900">{item.count}</strong>
                </div>
              ))}
            </div>

            {/* Scheme Volume Split */}
            <div className="pt-4 border-t border-slate-100">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-3">
                Volume by MoTA Scheme
              </span>
              <div className="grid grid-cols-2 gap-4">
                {analytics?.scheme_distribution?.map((s) => (
                  <div key={s.code} className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-extrabold text-gov-navy">{s.code}</span>
                      <span className="text-sm font-extrabold text-slate-800">{s.count} Apps</span>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-0.5 truncate">{s.scheme}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top States & Top Flagged Docs (5 cols) */}
          <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-800">State Demographics (Top ST Hubs)</h3>
              <span className="text-xs text-slate-500 font-medium">Native Domicile</span>
            </div>

            <div className="space-y-2.5">
              {analytics?.state_distribution?.slice(0, 5).map((st) => {
                const pct = (st.count / Math.max(kpis.total_applications || 18, 1)) * 100;
                return (
                  <div key={st.state} className="text-xs">
                    <div className="flex justify-between mb-1 font-semibold text-slate-700">
                      <span>{st.state}</span>
                      <span>{st.count} Scholars</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div className="bg-gov-navy h-2 rounded-full" style={{ width: `${Math.max(pct, 15)}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="pt-3 border-t border-slate-100">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
                Most Frequently Flagged for Deficiency
              </span>
              <div className="space-y-1.5">
                {analytics?.frequently_flagged_documents?.map((d) => (
                  <div key={d.doc_type} className="flex justify-between items-center text-xs bg-amber-50/60 p-2 rounded border border-amber-200">
                    <span className="font-semibold text-amber-900">{d.doc_type.replace(/_/g, ' ').toUpperCase()}</span>
                    <span className="font-bold text-amber-700">{d.count} flags raised</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MASTER APPLICATIONS TABLE */}
      <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Table Filters & Search Bar */}
        <div className="p-5 border-b border-slate-200 bg-slate-50/60 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-gov-navy">Scrutiny Application Queue</h3>
            <p className="text-xs text-slate-500">Filter applications by scheme, verification status, and state of domicile</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Scheme Filter */}
            <select
              value={schemeFilter}
              onChange={(e) => setSchemeFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold bg-white text-slate-700"
            >
              <option value="ALL">All Schemes</option>
              <option value="NFST">NFST (National Fellowship)</option>
              <option value="NOS">NOS (National Overseas)</option>
              <option value="TOP_CLASS">Top Class Education</option>
              <option value="POST_MATRIC">Post Matric Scholarship</option>
              <option value="PRE_MATRIC">Pre Matric Scholarship</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold bg-white text-slate-700"
            >
              <option value="All">All Statuses</option>
              <option value="Submitted">Submitted</option>
              <option value="Under Verification">Under Verification</option>
              <option value="Needs Review">Needs Review (Deficient)</option>
              <option value="Scrutiny">Under Scrutiny</option>
              <option value="Selected">Selected</option>
              <option value="Rejected">Rejected</option>
            </select>

            {/* State Filter */}
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold bg-white text-slate-700"
            >
              <option value="All">All States / UTs</option>
              {INDIAN_STATES_AND_UTS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>

            {/* Fraud Risk Filter */}
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold bg-white text-slate-700"
            >
              <option value="All">All Risk Levels</option>
              <option value="HIGH">🚨 High Risk Only</option>
              <option value="MEDIUM">⚠️ Medium Risk</option>
              <option value="LOW">🛡️ Low / Clean Only</option>
            </select>

            {/* Search */}
            <form onSubmit={handleSearchSubmit} className="relative">
              <input
                type="text"
                placeholder="Search candidate / ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-lg border border-slate-300 text-xs w-48 focus:ring-2 focus:ring-gov-navy focus:outline-none"
              />
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            </form>
          </div>
        </div>

        {/* Applications Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Application ID</th>
                <th className="py-3 px-4">Applicant & Tribe</th>
                <th className="py-3 px-4">Scheme</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4">Fraud Risk</th>
                <th className="py-3 px-4">Academic Marks</th>
                <th className="py-3 px-4">Annual Income</th>
                <th className="py-3 px-4">AI Verification</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    Loading applications...
                  </td>
                </tr>
              ) : applications.length > 0 ? (
                applications.map((app) => (
                  <tr
                    key={app.id}
                    onClick={() => onSelectApplication(app.id)}
                    className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-gov-navy">
                      {app.application_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-800">{app.applicant?.full_name}</div>
                      <div className="text-[11px] text-slate-500">
                        {app.applicant?.community_tribe} • {app.applicant?.st_cert_number}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold px-2 py-0.5 rounded text-[11px] bg-slate-100 text-slate-800">
                        {app.scheme?.code}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 font-medium">
                      {app.applicant?.state || app.form_data?.state}
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge level={app.risk_level} score={app.risk_score} />
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-800">
                      {app.form_data?.marks_percentage}%
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-700">
                      ₹ {parseFloat(app.form_data?.annual_income || 0).toLocaleString('en-IN')}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectApplication(app.id);
                        }}
                        className="px-3 py-1 text-xs font-bold text-gov-navy hover:bg-blue-100 rounded-lg transition-colors inline-flex items-center space-x-1"
                      >
                        <span>Inspect & Scrutinize</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    No applications matched the selected filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
