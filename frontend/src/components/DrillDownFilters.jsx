'use client';
import React from 'react';
import { ChevronDown, RotateCcw } from 'lucide-react';
import { roles, hiringPeriods } from '../data/mockRecruitmentData';

export default function DrillDownFilters({ department, role, period, setDepartment, setRole, setPeriod, reset }) {
  return (
    <div className="rounded-lg border border-[#2D3E54] bg-[#0F1621] p-8 flex flex-col justify-between shadow-lg">
      <div>
        <div className="uppercase text-xs tracking-[0.1em] text-[#7B8BA8] font-bold">Filter Dashboard</div>
        <div className="text-sm text-[#D0D7E8] mt-3 font-medium">Refine your recruitment data by department, role, and period</div>
      </div>

      <div className="flex flex-wrap gap-6 items-end">
        <div>
          <label className="text-xs text-[#7B8BA8] font-bold uppercase tracking-wider block mb-2.5">Department</label>
          <div className="flex items-center gap-2 rounded-lg bg-[#1A2332] border border-[#2D3E54] px-4 h-11 w-[260px] text-[#D0D7E8] hover:border-[#4A5D7A] transition">
            <select value={department} onChange={(e)=>setDepartment(e.target.value)} className="bg-transparent w-full outline-none text-sm font-medium">
              <option>All departments</option>
              <option>IT</option>
              <option>Sales</option>
              <option>Finance</option>
              <option>Operations</option>
            </select>
            <ChevronDown size={18} className="flex-shrink-0 text-[#7B8BA8]" />
          </div>
        </div>

        <div>
          <label className="text-xs text-[#7B8BA8] font-bold uppercase tracking-wider block mb-2.5">Job role</label>
          <div className={`flex items-center gap-2 rounded-lg bg-[#1A2332] border ${role? 'border-[#19C3C3] shadow-lg shadow-cyan-500/10':'border-[#2D3E54]'} px-4 h-11 w-[280px] text-[#D0D7E8] hover:border-[#4A5D7A] transition`}>
            <select value={role} onChange={(e)=>setRole(e.target.value)} className="bg-transparent w-full outline-none text-sm font-medium">
              <option>All roles</option>
              {roles.map(r=> <option key={r}>{r}</option>)}
            </select>
            <ChevronDown size={18} className="flex-shrink-0 text-[#7B8BA8]" />
          </div>
        </div>

        <div>
          <label className="text-xs text-[#7B8BA8] font-bold uppercase tracking-wider block mb-2.5">Hiring period</label>
          <div className="flex items-center gap-2 rounded-lg bg-[#1A2332] border border-[#2D3E54] px-4 h-11 w-[240px] text-[#D0D7E8] hover:border-[#4A5D7A] transition">
            <select value={period} onChange={(e)=>setPeriod(e.target.value)} className="bg-transparent w-full outline-none text-sm font-medium">
              {hiringPeriods.map(p => <option key={p}>{p}</option>)}
            </select>
            <ChevronDown size={18} className="flex-shrink-0 text-[#7B8BA8]" />
          </div>
        </div>

        <div className="ml-auto flex items-center gap-2 cursor-pointer text-[#7B8BA8] hover:text-[#19C3C3] transition px-4 py-2.5 rounded-lg hover:bg-[#1A2332]" onClick={reset}>
          <div className="rounded-lg bg-[#1A2332] p-2.5 border border-[#2D3E54] hover:border-[#4A5D7A] transition"><RotateCcw size={18} /></div>
          <div className="text-sm font-bold">Reset Filters</div>
        </div>
      </div>
    </div>
  );
}
