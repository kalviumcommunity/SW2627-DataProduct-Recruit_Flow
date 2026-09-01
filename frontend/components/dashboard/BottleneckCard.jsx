'use client';

import React from 'react';
import { AlertTriangle, ArrowRight } from 'lucide-react';

export default function BottleneckCard({
  stage = 'Interview Stage',
  percent = 28.9,
  description = '28.9% of candidates are lost here. Investigate interviewer feedback timelines.',
  onInvestigate
}) {
  return (
    <div className="flex items-center justify-between px-4 py-3 mb-6 rounded-md border border-[#7F1D1D] bg-[#2A0F12] shadow-lg shadow-red-950/20">
      <div className="flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 text-[#FCA5A5] shrink-0" />
        <div>
          <span className="text-[13px] font-bold text-[#FCA5A5] mr-2">
            Biggest leak: {stage}
          </span>
          <span className="text-[13px] text-[#FCA5A5] opacity-90">
            {description}
          </span>
        </div>
      </div>
      {onInvestigate && (
        <button 
          onClick={onInvestigate}
          className="flex items-center gap-1 text-[13px] font-semibold text-[#FCA5A5] hover:text-white transition-colors underline-offset-4 hover:underline shrink-0"
        >
          Investigate <ArrowRight className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
