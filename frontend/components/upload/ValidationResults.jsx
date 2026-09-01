'use client';

import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck, Filter, FileText } from 'lucide-react';

export default function ValidationResults({ validationErrors, sampleRecords }) {
  const [filterType, setFilterType] = useState('all');

  const errors = validationErrors || [
    {
      id: 'ERR-101',
      entity_type: 'applications',
      source_row_number: 142,
      error_message: 'Invalid ISO timestamp format for stage_entered_at',
      raw_data: '{"app_id": "APP-9821", "entered": "2026/13/45", "stage": "Interview"}'
    },
    {
      id: 'ERR-102',
      entity_type: 'candidates',
      source_row_number: 289,
      error_message: 'Duplicate candidate external ID with divergent email identity',
      raw_data: '{"ext_id": "CAND-4412", "email": "john.d@acme.io", "prev_email": "j.doe@work.net"}'
    },
    {
      id: 'ERR-103',
      entity_type: 'stage_events',
      source_row_number: 405,
      error_message: 'Stage progression anomaly: Offer stage recorded before Screening',
      raw_data: '{"app_id": "APP-1102", "order": [1, 4, 2], "issue": "chronological_violation"}'
    }
  ];

  const samples = sampleRecords || [
    {
      candidate_id: 'CAND-1001',
      name: 'Elena Rostova',
      email: 'elena.rostova@tech.co',
      department: 'Engineering',
      role: 'Staff ML Engineer',
      status: 'Joined',
      duration_days: 42
    },
    {
      candidate_id: 'CAND-1002',
      name: 'Marcus Vance',
      email: 'm.vance@venture.io',
      department: 'Sales',
      role: 'Enterprise AE',
      status: 'Offer Accepted',
      duration_days: 28
    },
    {
      candidate_id: 'CAND-1003',
      name: 'Chloe Zhang',
      email: 'chloe.z@cloudscale.com',
      department: 'Product',
      role: 'Principal PM',
      status: 'Interviewing',
      duration_days: 15
    }
  ];

  const filteredErrors = filterType === 'all' 
    ? errors 
    : errors.filter(e => e.entity_type === filterType);

  return (
    <div className="rounded-xl border border-[#27272A] bg-[#141417] p-6 shadow-xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#27272A]">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#22C55E]" />
            <h3 className="text-base font-semibold text-white">Validation Results & Quarantine Inspection</h3>
          </div>
          <p className="text-xs text-[#A1A1AA] mt-1">
            Automated schema enforcement, deduplication rules, and anomaly quarantine logs.
          </p>
        </div>
        
        {/* Filter error type pills */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#71717A] mr-1">Filter:</span>
          {['all', 'candidates', 'applications', 'stage_events'].map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-2.5 py-1 rounded text-xs font-medium capitalize transition-all ${
                filterType === type
                  ? 'bg-[#38BDF8] text-black font-semibold'
                  : 'bg-[#101014] text-[#A1A1AA] hover:text-white border border-[#27272A]'
              }`}
            >
              {type.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Validated Sample Preview */}
      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-[#A1A1AA] mb-3 flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
          Successfully Cleaned & Structured Records (Sample)
        </h4>
        <div className="overflow-x-auto rounded-lg border border-[#27272A] bg-[#101014]">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-[#27272A] bg-[#18181D] font-mono text-[#A1A1AA]">
              <tr>
                <th className="py-2.5 px-4">Candidate ID</th>
                <th className="py-2.5 px-4">Name</th>
                <th className="py-2.5 px-4">Department</th>
                <th className="py-2.5 px-4">Job Role</th>
                <th className="py-2.5 px-4">Current Status</th>
                <th className="py-2.5 px-4 text-right">Cycle Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#27272A] text-[#D4D4D8]">
              {samples.map((rec, i) => (
                <tr key={i} className="hover:bg-[#18181D]/50 transition-colors">
                  <td className="py-2.5 px-4 font-mono text-[#38BDF8]">{rec.candidate_id}</td>
                  <td className="py-2.5 px-4 font-medium text-white">{rec.name}</td>
                  <td className="py-2.5 px-4">{rec.department}</td>
                  <td className="py-2.5 px-4 text-[#A1A1AA]">{rec.role}</td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                      {rec.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono">{rec.duration_days} days</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quarantine Errors Log */}
      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-[#EF4444] mb-3 flex items-center gap-1.5">
          <XCircle className="w-4 h-4 text-[#EF4444]" />
          Quarantined Validation Errors ({filteredErrors.length})
        </h4>
        {filteredErrors.length === 0 ? (
          <div className="p-4 rounded-lg bg-[#101014] border border-[#27272A] text-center text-xs text-[#22C55E]">
            ✓ No quarantine errors found for selected filter.
          </div>
        ) : (
          <div className="space-y-2 max-h-56 overflow-y-auto">
            {filteredErrors.map((err) => (
              <div key={err.id} className="p-3 rounded-lg bg-[#1E1114] border border-[#7F1D1D]/40 text-xs">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-[#FCA5A5]">{err.id}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold bg-[#7F1D1D] text-[#FCA5A5]">
                      {err.entity_type}
                    </span>
                    {err.source_row_number && (
                      <span className="text-[#71717A]">Row #{err.source_row_number}</span>
                    )}
                  </div>
                  <span className="text-[10px] text-[#EF4444] font-medium">Validation Failure</span>
                </div>
                <p className="text-[#D4D4D8] font-medium mb-1.5">{err.error_message}</p>
                {err.raw_data && (
                  <pre className="p-2 rounded bg-black/60 font-mono text-[10px] text-[#A1A1AA] overflow-x-auto">
                    {err.raw_data}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
