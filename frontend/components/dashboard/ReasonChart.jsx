'use client';

import React from 'react';

export default function ReasonChart({ reasons, topReasonText }) {
  const defaultReasons = [
    { reason: 'Skill Mismatch', percentage: 82, color: '#FB7185' },
    { reason: 'Domain Knowledge', percentage: 68, color: '#FBBF24' },
    { reason: 'Candidate Withdrew', percentage: 50, color: '#94A3B8' },
    { reason: 'Salary Expectations', percentage: 35, color: '#64748B' }
  ];

  const data = reasons && reasons.length > 0 ? reasons : defaultReasons;

  return (
    <div>
      <div className="space-y-4 mb-6">
        {data.map((item, idx) => {
          const name = item.reason;
          const pct = item.percentage || 50;
          const barColor = item.color || (idx === 0 ? '#FB7185' : idx === 1 ? '#FBBF24' : idx === 2 ? '#94A3B8' : '#64748B');

          return (
            <div key={name} className="flex items-center gap-3">
              <div className="w-36 text-[12px] text-[#D4D4D8] truncate">{name}</div>
              <div className="flex-1 h-[8px] bg-[#27272A] rounded-r-md overflow-hidden">
                <div
                  className="h-full rounded-r-md transition-all duration-300"
                  style={{ width: `${pct}%`, backgroundColor: barColor }}
                />
              </div>
              <span className="text-[11px] font-mono text-[#A1A1AA] w-10 text-right">{pct}%</span>
            </div>
          );
        })}
      </div>

      <div className="p-3 rounded-md border border-[#27272A] bg-[#0E0E11] text-[12px] text-[#A1A1AA]">
        {topReasonText || (
          <span>
            Top reason: <span className="text-white font-semibold">Technical skill mismatch</span> — 22.5% of 458 lost candidates.
          </span>
        )}
      </div>
    </div>
  );
}
