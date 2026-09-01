'use client';

import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Database, Layers, Clock } from 'lucide-react';

export default function UploadStatus({ batchData, isUploading }) {
  const data = batchData || {
    id: 'BATCH-2026-0828-A1',
    filename: 'candidates_recruitment_q3.csv',
    status: 'journey_reconstructed',
    total_rows: 6633,
    accepted_rows: 6412,
    rejected_rows: 221,
    warning_rows: 38,
    duplicate_rows: 14,
    entities: {
      candidates: 6633,
      jobs: 48,
      applications: 6633,
      stage_events: 18840
    },
    processing_duration_ms: 420
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
      case 'journey_reconstructed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
            <CheckCircle className="w-3.5 h-3.5" /> Pipeline Live
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#38BDF8]/15 text-[#38BDF8] border border-[#38BDF8]/30">
            <Layers className="w-3.5 h-3.5 animate-spin" /> Ingesting
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#EF4444]/15 text-[#EF4444] border border-[#EF4444]/30">
            <XCircle className="w-3.5 h-3.5" /> Batch Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#EAB308]/15 text-[#EAB308] border border-[#EAB308]/30">
            <AlertTriangle className="w-3.5 h-3.5" /> Ready
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border border-[#27272A] bg-[#141417] p-6 shadow-xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#27272A]">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-base font-semibold text-white">Batch Status & Verification</h3>
            {getStatusBadge(isUploading ? 'processing' : data.status)}
          </div>
          <p className="text-xs text-[#A1A1AA] mt-1 font-mono">
            Active Batch ID: <span className="text-[#D4D4D8]">{data.id || 'N/A'}</span> • File: <span className="text-white font-medium">{data.filename || 'None'}</span>
          </p>
        </div>
        {data.processing_duration_ms && (
          <div className="flex items-center gap-1.5 text-xs text-[#A1A1AA] bg-[#101014] px-3 py-1.5 rounded-md border border-[#27272A]">
            <Clock className="w-3.5 h-3.5 text-[#38BDF8]" />
            Processed in <strong className="text-white">{data.processing_duration_ms} ms</strong>
          </div>
        )}
      </div>

      {/* Row Count Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-[#101014] border border-[#27272A]">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#A1A1AA]">Total Ingested</p>
          <p className="text-2xl font-bold text-white mt-1">{(data.total_rows || 0).toLocaleString()}</p>
          <p className="text-[11px] text-[#71717A] mt-0.5">Raw spreadsheet rows</p>
        </div>

        <div className="p-4 rounded-lg bg-[#101014] border border-[#27272A]">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#22C55E]">Accepted Records</p>
          <p className="text-2xl font-bold text-[#22C55E] mt-1">{(data.accepted_rows || 0).toLocaleString()}</p>
          <p className="text-[11px] text-[#71717A] mt-0.5">
            {data.total_rows ? `${((data.accepted_rows / data.total_rows) * 100).toFixed(1)}% valid` : '100%'}
          </p>
        </div>

        <div className="p-4 rounded-lg bg-[#101014] border border-[#27272A]">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#EAB308]">Warnings & Fixes</p>
          <p className="text-2xl font-bold text-[#EAB308] mt-1">{data.warning_rows || 0}</p>
          <p className="text-[11px] text-[#71717A] mt-0.5">Auto-standardized</p>
        </div>

        <div className="p-4 rounded-lg bg-[#101014] border border-[#27272A]">
          <p className="text-[11px] font-bold uppercase tracking-wider text-[#EF4444]">Quarantined / Errors</p>
          <p className="text-2xl font-bold text-[#EF4444] mt-1">{data.rejected_rows || 0}</p>
          <p className="text-[11px] text-[#71717A] mt-0.5">Missing essential keys</p>
        </div>
      </div>

      {/* Entity Breakdown */}
      {data.entities && (
        <div className="pt-2">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-[#38BDF8]" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">Staging Table Entity Counts</h4>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            {Object.entries(data.entities).map(([entity, count]) => (
              <div key={entity} className="flex items-center justify-between p-2.5 rounded bg-[#101014] border border-[#27272A]">
                <span className="capitalize text-[#A1A1AA]">{entity.replace('_', ' ')}</span>
                <span className="font-mono font-bold text-white">{count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
