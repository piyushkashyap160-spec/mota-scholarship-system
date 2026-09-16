import React, { useState, useEffect } from 'react';
import { Award, Users, Sliders, ArrowLeft, CheckCircle2, ShieldCheck, ChevronRight, HelpCircle } from 'lucide-react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';

export default function AdminMeritRanking({ onBack, onSelectApplication }) {
  const [marksWeight, setMarksWeight] = useState(0.70);
  const [incomeWeight, setIncomeWeight] = useState(0.30);
  const [rankingData, setRankingData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRankings = async (mw, iw) => {
    setLoading(true);
    try {
      const res = await api.admin.getMeritRanking({ marks_weight: mw, income_weight: iw });
      setRankingData(res.rankings || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankings(marksWeight, incomeWeight);
  }, []);

  const handleSliderChange = (newMarksPct) => {
    const mw = parseFloat((newMarksPct / 100).toFixed(2));
    const iw = parseFloat((1 - mw).toFixed(2));
    setMarksWeight(mw);
    setIncomeWeight(iw);
    fetchRankings(mw, iw);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="px-3 py-1.5 text-xs font-bold text-gov-navy hover:bg-slate-100 rounded-lg flex items-center space-x-1 border border-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scrutiny Dashboard</span>
        </button>

        <span className="text-xs font-semibold text-slate-500">
          MoTA Fellowship Scrutiny Panel
        </span>
      </div>

      {/* Human-in-the-Loop Assistive Banner */}
      <div className="bg-gradient-to-r from-blue-900 to-gov-navy text-white rounded-2xl p-6 shadow-lg border border-blue-950">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-amber-400 text-slate-950 rounded-xl flex-shrink-0 mt-0.5">
            <Award className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold">Merit-Based Assistive Shortlist & Ranking</h2>
              <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded bg-white/20 text-amber-300">
                AI Assists, Human Decides
              </span>
            </div>
            <p className="text-xs text-slate-200 mt-1 leading-relaxed">
              This assistive ranking synthesizes academic excellence with economic affirmative action to aid the
              Selection Committee in shortlisting eligible Scheduled Tribe scholars. Final sanctions require Committee ratification.
            </p>
          </div>
        </div>

        {/* Dynamic Weight Configuration Controls */}
        <div className="mt-6 pt-5 border-t border-white/10 bg-white/5 p-4 rounded-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold text-amber-300 uppercase tracking-wider block">
                Configurable Assistive Scoring Weights
              </span>
              <span className="text-[11px] text-slate-300">
                Adjust sliders to dynamically tune weighting between Academic Merit and Economic Need.
              </span>
            </div>

            <div className="flex items-center space-x-6 text-xs">
              <div className="text-center">
                <span className="text-slate-300 block text-[10px] uppercase">Academic Weight</span>
                <strong className="text-amber-400 text-sm font-mono">{(marksWeight * 100).toFixed(0)}%</strong>
              </div>
              <div className="text-center">
                <span className="text-slate-300 block text-[10px] uppercase">Economic Need Weight</span>
                <strong className="text-emerald-400 text-sm font-mono">{(incomeWeight * 100).toFixed(0)}%</strong>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <input
              type="range"
              min="40"
              max="90"
              step="5"
              value={marksWeight * 100}
              onChange={(e) => handleSliderChange(e.target.value)}
              className="w-full accent-amber-400 cursor-pointer h-2 bg-slate-700 rounded-lg"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
              <span>Higher Economic Weight (40% Marks / 60% Need)</span>
              <span>Default (70% Marks / 30% Need)</span>
              <span>Pure Academic Weight (90% Marks / 10% Need)</span>
            </div>
          </div>
        </div>
      </div>

      {/* RANKED CANDIDATES TABLE */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center text-xs">
          <span className="font-bold text-slate-800">
            Eligible Scheduled Tribe Candidates Ranked ({rankingData.length} Candidates Qualified)
          </span>
          <span className="text-slate-500 font-medium">Sorted by Assistive Score Descending</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4 text-center">Rank</th>
                <th className="py-3 px-4">Application ID</th>
                <th className="py-3 px-4">Scholar Name & Tribe</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4">Scheme</th>
                <th className="py-3 px-4">Marks %</th>
                <th className="py-3 px-4">Annual Income</th>
                <th className="py-3 px-4">Assistive Score</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-400">
                    Computing real-time merit scores...
                  </td>
                </tr>
              ) : rankingData.map((item) => (
                <tr
                  key={item.application_id}
                  onClick={() => onSelectApplication(item.application_id)}
                  className="hover:bg-blue-50/40 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-4 text-center">
                    <span
                      className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs ${
                        item.rank === 1
                          ? 'bg-amber-400 text-slate-950 ring-2 ring-amber-200'
                          : item.rank === 2
                          ? 'bg-slate-300 text-slate-800'
                          : item.rank === 3
                          ? 'bg-amber-700/70 text-white'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {item.rank}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-gov-navy">
                    {item.application_number}
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-bold text-slate-800">{item.applicant_name}</div>
                    <div className="text-[11px] text-slate-500">{item.community_tribe}</div>
                  </td>
                  <td className="py-3 px-4 text-slate-700 font-medium">
                    {item.state}
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-bold px-2 py-0.5 rounded text-[11px] bg-slate-100 text-slate-800">
                      {item.scheme_code}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-slate-800">
                    {item.marks_percentage}%
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-700">
                    ₹ {parseFloat(item.annual_income || 0).toLocaleString('en-IN')}
                  </td>
                  <td className="py-3 px-4 font-mono font-extrabold text-gov-navy text-sm">
                    {item.merit_score.toFixed(2)}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectApplication(item.application_id);
                      }}
                      className="px-2.5 py-1 text-xs font-bold text-gov-navy hover:bg-blue-100 rounded-lg transition-colors inline-flex items-center space-x-1"
                    >
                      <span>Review</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
