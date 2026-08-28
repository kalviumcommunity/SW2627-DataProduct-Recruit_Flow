'use client';

import React from 'react';

export default function FunnelChart({ stages, highlightStage = 'Interview' }) {
  const defaultStages = [
    { name: 'Applications', count: 6633, dropoff_rate: 23.0, lost: 1528, width: '100%', color: '#333338', status: 'normal' },
    { name: 'Screening', count: 5105, dropoff_rate: 18.0, lost: 919, width: '77%', color: '#333338', status: 'normal' },
    { name: 'Interview', count: 4186, dropoff_rate: 28.9, lost: 1185, width: '63%', color: '#EF4444', status: 'leak', isLeak: true },
    { name: 'Technical Round', count: 3001, dropoff_rate: 15.0, lost: 458, width: '46%', color: '#333338', status: 'good' },
    { name: 'Offer Stage', count: 1691, dropoff_rate: 13.0, lost: 221, width: '26%', color: '#333338', status: 'good' },
    { name: 'Joined', count: 1470, dropoff_rate: 0, lost: 0, width: '22%', color: '#22C55E', status: 'success' }
  ];

  const data = stages && stages.length > 0 ? stages : defaultStages;

  return (
    <div className="space-y-4">
      {data.map((stg) => {
        const isHighlight = stg.isLeak || stg.name === highlightStage || stg.stage_name === highlightStage;
        const count = stg.count || stg.applications_entered || 0;
        const dropRate = stg.dropoff_rate !== undefined ? stg.dropoff_rate : (stg.dropoff_rate || 0);
        const name = stg.name || stg.stage_name;
        const lostCount = stg.lost || stg.applications_dropped || 0;
        const widthPct = stg.width || `${Math.max(15, Math.min(100, (count / 6633) * 100))}%`;

        return (
          <div key={name}>
            <div className="flex items-center justify-between text-[13px] mb-1.5">
              <div className="flex items-center gap-2">
                <span className={`font-medium ${isHighlight ? 'text-[#FCA5A5] font-bold' : 'text-[#D4D4D8]'}`}>
                  {name}
                </span>
                {isHighlight && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#7F1D1D] text-[#FCA5A5] border border-[#991B1B]">
                    HIGHEST LEAK
                  </span>
                )}
              </div>
              <span className="text-white font-bold">{count.toLocaleString()}</span>
            </div>

            <div
              className={`h-[28px] rounded-r-md transition-all ${
                isHighlight
                  ? 'bg-[#EF4444] border border-[#F87171]/40 shadow-lg shadow-red-950/40'
                  : name === 'Joined'
                  ? 'bg-[#22C55E]'
                  : 'bg-[#333338]'
              }`}
              style={{ width: widthPct }}
            />

            {dropRate > 0 && (
              <div className="flex items-center gap-2 pl-3 pt-1">
                <span
                  className={`text-[11px] font-bold ${
                    dropRate > 25 ? 'text-[#EF4444]' : dropRate >= 18 ? 'text-[#EAB308]' : 'text-[#22C55E]'
                  }`}
                >
                  ↓ -{dropRate}%
                </span>
                {lostCount > 0 && (
                  <span className="text-[11px] text-[#71717A]">
                    {lostCount.toLocaleString()} candidates lost
                  </span>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
