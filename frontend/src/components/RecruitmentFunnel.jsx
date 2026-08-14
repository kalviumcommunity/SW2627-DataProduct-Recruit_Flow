'use client';
import React from 'react';
import FunnelStage from './FunnelStage';
import { calculateDropOffPercent } from '../utils/recruitmentAnalytics';

export default function RecruitmentFunnel({ funnel, biggestLeakFrom }) {
  const applications = funnel[0]?.candidates ?? 1;
  return (
    <div className="rounded-lg border border-[#2D3E54] bg-gradient-to-br from-[#1A2332] to-[#0F1621] p-8 shadow-lg">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-2xl text-[#F0F4F8] font-bold">Recruitment Funnel</h3>
          <div className="text-sm text-[#7B8BA8] mt-3 font-medium">Candidates progressing through pipeline stages</div>
        </div>
        <div className="text-xs text-[#7B8BA8] font-bold tracking-wider">{'●'} {'<'}18% {'●'} 18–30% {'●'} {'>'}30%</div>
      </div>

      <div className="space-y-3">
        {funnel.map((s, i) => {
          const next = funnel[i + 1];
          const pct = Math.round((s.candidates / applications) * 10000) / 100;
          const isHighlight = biggestLeakFrom === s.stage;
          return (
            <div key={s.stage}>
              <FunnelStage stage={s.stage} candidates={s.candidates} pctOfApps={pct} median={s.medianDays ?? ''} isHighlight={isHighlight} />
              {next && (
                <div className="flex items-center gap-4 text-xs text-[#929EAE] px-2 py-3">
                  <div className="text-[#19C3C3] text-lg">↓</div>
                  <div className="font-semibold text-[#E7EDF5]">{calculateDropOffPercent(s.candidates, next.candidates)}%</div>
                  <div className="text-[#929EAE]">{(s.candidates - next.candidates).toLocaleString()} candidates lost</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
