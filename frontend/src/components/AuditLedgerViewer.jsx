import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertTriangle, Download, RefreshCw, FileText, Lock, Hash, ArrowDown } from 'lucide-react';
import { api } from '../api/client';

export default function AuditLedgerViewer({ applicationId, applicationNumber }) {
  const [ledgerData, setLedgerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState(null);
  const [expandedBlocks, setExpandedBlocks] = useState({});

  const loadLedger = async () => {
    setVerifying(true);
    setError(null);
    try {
      const data = await api.admin.getAuditLedger(applicationId);
      setLedgerData(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch audit ledger');
    } finally {
      setLoading(false);
      setVerifying(false);
    }
  };

  useEffect(() => {
    if (applicationId) {
      loadLedger();
    }
  }, [applicationId]);

  const toggleExpand = (blockId) => {
    setExpandedBlocks((prev) => ({
      ...prev,
      [blockId]: !prev[blockId]
    }));
  };

  const handleDownloadCsv = () => {
    const url = api.admin.exportAuditUrl(applicationId, 'csv');
    window.open(url, '_blank');
  };

  const handleDownloadJson = () => {
    const url = api.admin.exportAuditUrl(applicationId, 'json');
    window.open(url, '_blank');
  };

  if (loading) {
    return <div className="py-6 text-center text-xs text-slate-400">Loading cryptographic audit ledger...</div>;
  }

  const isValid = ledgerData?.is_integrity_valid !== false;
  const blocks = ledgerData?.ledger_blocks || [];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden text-xs">
      {/* Ledger Header */}
      <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-sm font-bold text-slate-900">Immutable Cryptographic Audit Ledger</h3>
            {isValid ? (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center space-x-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>Integrity Certified</span>
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300 flex items-center space-x-1">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                <span>Tamper Detected</span>
              </span>
            )}
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Every state transition is sealed with SHA-256 parent block hash chains for statutory audit & RTI compliance.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={loadLedger}
            disabled={verifying}
            className="px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-white text-slate-700 font-bold transition-all flex items-center space-x-1 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-gov-navy ${verifying ? 'animate-spin' : ''}`} />
            <span>Verify Chain</span>
          </button>
          <button
            type="button"
            onClick={handleDownloadCsv}
            className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold transition-all flex items-center space-x-1"
          >
            <Download className="w-3.5 h-3.5" />
            <span>CSV</span>
          </button>
          <button
            type="button"
            onClick={handleDownloadJson}
            className="px-3 py-1.5 rounded-lg bg-gov-navy hover:bg-blue-900 text-white font-bold transition-all shadow flex items-center space-x-1"
          >
            <Download className="w-3.5 h-3.5 text-amber-300" />
            <span>RTI Dossier</span>
          </button>
        </div>
      </div>

      {error && <div className="p-4 text-rose-600 font-semibold">{error}</div>}

      {/* Block Chain List */}
      <div className="p-5 space-y-4">
        {blocks.length === 0 ? (
          <p className="text-slate-400 text-center py-4">No audit entries found in ledger.</p>
        ) : (
          <div className="relative">
            <div className="space-y-3">
              {blocks.map((block, idx) => {
                const isExpanded = !!expandedBlocks[block.block_id];

                return (
                  <div key={block.block_id} className="space-y-1">
                    <div
                      onClick={() => toggleExpand(block.block_id)}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                        block.is_valid
                          ? 'bg-slate-50/70 border-slate-200 hover:border-slate-300'
                          : 'bg-rose-50 border-rose-300'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center space-x-3">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] ${
                            block.is_valid ? 'bg-gov-navy text-white' : 'bg-rose-600 text-white'
                          }`}>
                            #{idx + 1}
                          </div>
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="font-bold text-slate-900">{block.action}</span>
                              <span className="text-slate-400">•</span>
                              <span className="text-slate-600 font-semibold">{block.actor}</span>
                            </div>
                            <span className="text-[11px] text-slate-500 block mt-0.5">
                              State Transition: <strong className="text-gov-navy">{block.transition}</strong>
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3 self-end sm:self-center">
                          <span className="text-[10px] font-mono text-slate-400">
                            {new Date(block.timestamp).toLocaleString()}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            block.is_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                          }`}>
                            {block.is_valid ? 'SHA-256 Valid' : 'Corrupted'}
                          </span>
                        </div>
                      </div>

                      {/* Expanded Cryptographic Hashes & Remarks */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t border-slate-200/80 space-y-2 text-[11px] font-mono animate-in fade-in">
                          {block.remarks && (
                            <p className="font-sans text-slate-700 font-medium">
                              <strong>Remarks: </strong> {block.remarks}
                            </p>
                          )}
                          <div className="bg-white p-2.5 rounded-lg border border-slate-200 space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="text-slate-400 text-[10px] uppercase font-bold">Entry Block Hash:</span>
                              <span className="text-emerald-700 font-bold truncate ml-2">{block.entry_hash}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-slate-400 text-[10px] uppercase font-bold">Previous Block Hash:</span>
                              <span className="text-slate-600 truncate ml-2">{block.previous_hash}</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Chain link icon between blocks */}
                    {idx < blocks.length - 1 && (
                      <div className="flex justify-center py-0.5">
                        <ArrowDown className="w-3.5 h-3.5 text-slate-300" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
