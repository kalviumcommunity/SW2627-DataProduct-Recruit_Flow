import React from 'react';

export default function FunnelStage({ stage, candidates, pctOfApps, median, isHighlight }) {
  return (
    <div className={`flex items-center justify-between py-4 px-1 group ${isHighlight? 'border border-[#FF5C6F] rounded-lg p-4 bg-[#2a1315] shadow-lg shadow-red-500/20':''}`}>
      <div className="w-36">
        <div className={`text-sm font-bold ${isHighlight ? 'text-[#FF5C6F]' : 'text-[#D0D7E8]'}`}>{stage}</div>
      </div>
      <div className="flex-1 px-6">
        <div className={`h-6 rounded-full shadow-lg ${isHighlight ? 'bg-gradient-to-r from-[#FF5C6F] to-[#FF7F8F]' : 'bg-gradient-to-r from-[#19C3C3] to-[#13a8a8]'}`} style={{ width: `${pctOfApps}%` }} />
      </div>
      <div className="w-44 text-right">
        <div className={`text-xs font-bold tracking-wider ${isHighlight ? 'text-[#FF5C6F]' : 'text-[#7B8BA8]'}`}>{median}d median</div>
        <div className={`text-xl mt-2 font-black ${isHighlight ? 'text-[#FF5C6F]' : 'text-[#F0F4F8]'}`}>{new Intl.NumberFormat().format(candidates)}</div>
      </div>
    </div>
  );
}
