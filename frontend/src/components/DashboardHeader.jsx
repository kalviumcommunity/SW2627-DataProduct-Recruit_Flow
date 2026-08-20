'use client';
import React from 'react';
import { Download, Upload } from 'lucide-react';
import { companyInfo } from '../data/mockRecruitmentData';
import { funnelData } from '../data/mockRecruitmentData';

const fmt = (v) => new Intl.NumberFormat().format(v);

export default function DashboardHeader() {
  const applications = funnelData[0]?.candidates ?? 0;
  return (
    <div className="flex items-center justify-between mb-6 pb-6 border-b border-[#1a2535]">
      <div>
        <h1 className="text-4xl font-bold text-[#F0F4F8] tracking-tight leading-tight">Recruitment Funnel Overview</h1>
        <p className="text-sm text-[#7B8BA8] mt-3 font-normal">{companyInfo.name} • {companyInfo.scopeText} • {fmt(applications)} candidates in scope</p>
      </div>
      <div className="flex gap-3">
        <button className="flex items-center gap-2 rounded-lg bg-[#1A2332] border border-[#2D3E54] px-5 h-12 text-[#B8C2D4] hover:bg-[#212D3D] hover:border-[#3d5070] transition text-sm font-medium">
          <Download size={19} />
          <span>Export report</span>
        </button>
        <button className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-[#19C3C3] to-[#13a8a8] px-5 h-12 text-white font-bold hover:from-[#17b0b0] hover:to-[#119999] transition text-sm shadow-lg shadow-cyan-500/20">
          <Upload size={19} />
          <span>Upload data</span>
        </button>
      </div>
    </div>
  );
}
