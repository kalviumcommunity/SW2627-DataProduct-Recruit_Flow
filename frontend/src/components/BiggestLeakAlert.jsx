import React from 'react';
import { AlertTriangle, Sparkles } from 'lucide-react';

export default function BiggestLeakAlert({ leak }) {
  if (!leak) return null;
  return (
    <div className="flex items-center justify-between rounded-lg border border-[#FF5C6F] bg-gradient-to-r from-[#1A0D0D] to-[#0F1621] p-6 h-28 shadow-lg shadow-red-500/10"> 
      <div className="flex items-center gap-5">
        <div className="p-3 rounded-lg bg-[#3D1517] border border-[#FF5C6F]/30">
          <AlertTriangle color="#FF5C6F" size={24} strokeWidth={2.5} />
        </div>
        <div>
          <div className="text-sm font-bold text-[#FF5C6F]">Biggest leak:</div>
          <div className="text-2xl font-bold text-[#F0F4F8] mt-1">{leak.from}</div>
          <div className="text-sm text-[#B8C2D4] mt-2">{leak.percent}% drop-off • {leak.lost.toLocaleString()} candidates</div>
        </div>
      </div>
      <div className="flex items-center gap-3 text-[#19C3C3] cursor-pointer hover:text-[#15a5a5] transition px-5 py-3 rounded-lg hover:bg-[#1a2332] group">
        <Sparkles size={20} className="group-hover:scale-110 transition" />
        <div className="font-semibold text-sm">Investigate</div>
      </div>
    </div>
  );
}
