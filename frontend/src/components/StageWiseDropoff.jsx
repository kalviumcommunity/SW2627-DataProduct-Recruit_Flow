import React from 'react';
import { calculateDropOffPercent, getStatusFromDropOff } from '../utils/recruitmentAnalytics';

export default function StageWiseDropoff({ funnel }) {
  const rows = funnel.slice(0, -1).map((s, i) => {
    const next = funnel[i+1];
    const drop = calculateDropOffPercent(s.candidates, next.candidates);
    const status = getStatusFromDropOff(drop);
    return {
      transition: `${s.stage} → ${next.stage}`,
      inCount: s.candidates,
      outCount: next.candidates,
      drop,
      vsPrev: '↘ 1%',
      status
    };
  });

  return (
    <div className="rounded-lg border border-[#2D3E54] bg-gradient-to-br from-[#1A2332] to-[#0F1621] p-8 overflow-auto shadow-lg">
      <h3 className="text-2xl text-[#F0F4F8] font-bold">Stage-wise Drop-off</h3>
      <div className="text-sm text-[#7B8BA8] mt-3 mb-8 font-medium">Performance metrics compared to previous period</div>
      <table className="w-full table-auto text-left">
        <thead className="text-[#7B8BA8] border-b border-[#2D3E54]">
          <tr>
            <th className="py-4 text-xs font-bold uppercase tracking-wider">Transition</th>
            <th className="text-xs font-bold uppercase tracking-wider">In</th>
            <th className="text-xs font-bold uppercase tracking-wider">Out</th>
            <th className="text-xs font-bold uppercase tracking-wider">Drop-off</th>
            <th className="text-xs font-bold uppercase tracking-wider">vs prev</th>
            <th className="text-xs font-bold uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.transition} className="border-b border-[#1A2332] hover:bg-[#1A2332] transition">
              <td className="py-4 text-sm text-[#D0D7E8] font-bold">{r.transition}</td>
              <td className="text-sm text-[#B8C2D4] font-semibold">{r.inCount.toLocaleString()}</td>
              <td className="text-sm text-[#B8C2D4] font-semibold">{r.outCount.toLocaleString()}</td>
              <td className="text-sm text-[#F0F4F8] font-bold">{r.drop}%</td>
              <td className="text-sm text-[#7B8BA8] font-medium">{r.vsPrev}</td>
              <td className={`font-bold text-sm ${r.status.color==='red'?'text-[#FF5C6F]': r.status.color==='amber'?'text-[#F5B335]':'text-[#2DD4BF]'}`}>{r.status.label}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
