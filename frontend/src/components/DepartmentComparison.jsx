import React from 'react';

export default function DepartmentComparison({ departments }) {
  return (
    <div className="rounded-lg border border-[#2D3E54] bg-gradient-to-br from-[#1A2332] to-[#0F1621] p-8 shadow-lg">
      <div className="mb-8">
        <h3 className="text-2xl text-[#F0F4F8] font-bold">Department Performance</h3>
        <div className="text-sm text-[#7B8BA8] mt-3 font-medium">Worst-case conversion rates by department</div>
      </div>
      <div className="space-y-6">
        {departments.map(d => (
          <div key={d.name} className="flex items-center justify-between gap-5 py-2 group">
            <div className="w-32 text-sm text-[#D0D7E8] font-bold">{d.name}</div>
            <div className="flex-1 px-5">
              <div className={`h-5 rounded-full shadow-lg ${d.value>30? 'bg-gradient-to-r from-[#FF5C6F] to-[#FF7F8F]': d.value>=18? 'bg-gradient-to-r from-[#F5B335] to-[#F5C449]':'bg-gradient-to-r from-[#2DD4BF] to-[#13a8a8]'}`} style={{ width: `${Math.min(100, d.value)}%` }} />
            </div>
            <div className={`w-20 text-right font-black text-lg ${d.value>30? 'text-[#FF5C6F]': d.value>=18? 'text-[#F5B335]':'text-[#2DD4BF]'}`}>{d.value}%</div>
            <div className="w-96 text-xs text-[#7B8BA8] text-right font-medium">Worst: {d.worstStage} • {d.applied.toLocaleString()} → {d.joined.toLocaleString()} ({Math.round((d.joined/d.applied)*1000)/10}%)</div>
          </div>
        ))}
      </div>
    </div>
  );
}
