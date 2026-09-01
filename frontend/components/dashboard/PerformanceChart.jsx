'use client';

import React from 'react';

export default function PerformanceChart({ title = 'PR Volume Over Time', subtitle = 'Daily open vs merged pull requests' }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-[14px] font-bold text-white">{title}</h3>
          <p className="text-[12px] text-[#A1A1AA] mt-0.5">{subtitle}</p>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-[#D4D4D8]">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#38BDF8]"></div>Opened
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#22C55E]"></div>Merged
          </div>
        </div>
      </div>

      {/* Visual Wave Chart Graphic matching mockup */}
      <div className="h-[220px] w-full flex items-center justify-center pt-4">
        <svg viewBox="0 0 500 200" className="w-full h-full overflow-visible">
          <defs>
            <linearGradient id="openedGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.25"/>
              <stop offset="100%" stopColor="#38BDF8" stopOpacity="0.0"/>
            </linearGradient>
            <linearGradient id="mergedGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22C55E" stopOpacity="0.25"/>
              <stop offset="100%" stopColor="#22C55E" stopOpacity="0.0"/>
            </linearGradient>
          </defs>
          {/* Grid lines */}
          <line x1="0" y1="50" x2="500" y2="50" stroke="#27272A" strokeDasharray="3 3" />
          <line x1="0" y1="110" x2="500" y2="110" stroke="#27272A" strokeDasharray="3 3" />
          <line x1="0" y1="170" x2="500" y2="170" stroke="#27272A" strokeDasharray="3 3" />

          {/* Opened Curve */}
          <path d="M 0 140 Q 70 80, 140 120 T 280 60 T 420 110 T 500 40 L 500 200 L 0 200 Z" fill="url(#openedGrad)" />
          <path d="M 0 140 Q 70 80, 140 120 T 280 60 T 420 110 T 500 40" fill="none" stroke="#38BDF8" strokeWidth="2.5" />

          {/* Merged Curve */}
          <path d="M 0 160 Q 80 140, 160 130 T 320 80 T 440 70 T 500 60 L 500 200 L 0 200 Z" fill="url(#mergedGrad)" />
          <path d="M 0 160 Q 80 140, 160 130 T 320 80 T 440 70 T 500 60" fill="none" stroke="#22C55E" strokeWidth="2.5" />
        </svg>
      </div>
      <div className="flex justify-between text-[10px] text-[#71717A] px-2 pt-2 border-t border-[#27272A]">
        <span>W1</span><span>W2</span><span>W3</span><span>W4</span>
      </div>
    </div>
  );
}
