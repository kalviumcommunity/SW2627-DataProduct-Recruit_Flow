import React from 'react';
export default function KPICard({ label, value, description, icon, color }) {
  const fmt = (v) => (typeof v === 'number' ? new Intl.NumberFormat().format(v) : v);
  return (
    <div className="rounded-lg border border-[#2D3E54] bg-gradient-to-br from-[#1A2332] to-[#0F1621] p-7 w-full hover:border-[#4A5D7A] hover:shadow-lg hover:shadow-cyan-500/5 transition group">
      <div className="flex items-start justify-between">
        <div className="text-xs uppercase tracking-[0.08em] text-[#7B8BA8] font-bold">{label}</div>
        <div className="text-[#19C3C3] opacity-80 group-hover:opacity-100 transition">{icon}</div>
      </div>
      <div className="mt-6 flex items-baseline justify-between">
        <div className={`text-[48px] font-black tracking-tighter ${color==='green'?'text-[#2DD4BF]': color==='red'?'text-[#FF5C6F]':'text-[#F0F4F8]'}`}>{fmt(value)}</div>
        <div className="text-xs text-[#7B8BA8] max-w-[140px] text-right font-semibold leading-tight">{description}</div>
      </div>
    </div>
  );
}
