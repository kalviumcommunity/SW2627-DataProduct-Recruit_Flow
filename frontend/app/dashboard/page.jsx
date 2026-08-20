'use client';

import { useState } from 'react';
import './dashboard.css';
import {
  Search, Bell, Download, Filter, Users, UserCheck, AlertTriangle, Clock,
  LayoutDashboard, Filter as FunnelIcon, Users as DeptIcon, HardDrive,
  Settings, HelpCircle, UploadCloud, ChevronDown
} from 'lucide-react';

export default function DashboardPage() {
  const [activeNav, setActiveNav] = useState('overview');

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'funnel', label: 'Funnel', icon: FunnelIcon },
    { id: 'departments', label: 'Departments', icon: DeptIcon },
    { id: 'intake', label: 'Data Intake', icon: HardDrive },
  ];

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="dashboard-sidebar">
        <div className="px-5 pt-6 pb-6">
          <div className="text-xl font-bold text-white tracking-tight">Recruitflow</div>
          <div className="text-[10px] text-[#A1A1AA] font-bold uppercase tracking-widest mt-1">Talent Command</div>
        </div>

        <div className="px-4 mb-6">
          <button className="w-full flex items-center justify-center gap-2 py-2 rounded-md bg-[#27272A] border border-[#3F3F46] text-white text-[13px] font-medium hover:bg-[#3F3F46] transition-colors">
            <span className="text-[16px] leading-none mb-0.5">+</span>
            Create Requisition
          </button>
        </div>

        <nav className="flex-1 px-3 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeNav === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveNav(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium transition-colors ${
                  isActive ? 'bg-[#27272A] text-white' : 'text-[#A1A1AA] hover:bg-[#18181B] hover:text-[#D4D4D8]'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="px-3 pb-4 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium text-[#A1A1AA] hover:bg-[#18181B] hover:text-[#D4D4D8] transition-colors">
            <Settings className="w-4 h-4" />
            Settings
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium text-[#A1A1AA] hover:bg-[#18181B] hover:text-[#D4D4D8] transition-colors">
            <HelpCircle className="w-4 h-4" />
            Support
          </button>
        </div>

        <div className="px-4 py-4 border-t border-[#27272A] flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#3F3F46] flex items-center justify-center shrink-0">
            <img src="https://ui-avatars.com/api/?name=Alex+Mercer&background=3F3F46&color=fff&size=32" alt="Avatar" className="rounded-full w-full h-full" />
          </div>
          <div className="min-w-0">
            <div className="text-[13px] font-semibold text-white truncate">Alex Mercer</div>
            <div className="text-[11px] text-[#A1A1AA] truncate">Lead Recruiter</div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="dashboard-main">
        {/* Topbar */}
        <header className="dashboard-topbar">
          <div className="flex-1 max-w-[320px] relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
            <input
              type="text"
              placeholder="Search candidates, reqs..."
              className="w-full pl-9 pr-4 py-1.5 rounded-md border border-[#27272A] bg-[#18181B] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#3F3F46]"
            />
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-4 text-[13px] font-medium text-[#A1A1AA]">
              <span className="hover:text-white cursor-pointer">Department</span>
              <span className="hover:text-white cursor-pointer">Job Role</span>
              <span className="hover:text-white cursor-pointer">Period</span>
            </div>
            <div className="w-px h-4 bg-[#27272A]"></div>
            <button className="relative text-[#A1A1AA] hover:text-white transition-colors">
              <Bell className="w-4 h-4" />
              <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-[#EF4444] rounded-full border border-[#09090B]"></span>
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] text-[13px] font-medium text-[#D4D4D8] hover:bg-[#18181B] transition-colors">
              <Download className="w-3.5 h-3.5" />
              Export Data
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="dashboard-content">
          
          {/* Header row */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-xl font-bold text-white">Recruitment funnel overview</h1>
              <p className="text-[13px] text-[#A1A1AA] mt-1">ABC Technologies • All departments • 6,633 candidates in scope</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] bg-[#18181B] text-[13px] font-medium text-[#D4D4D8] hover:bg-[#27272A] transition-colors">
                <Filter className="w-3.5 h-3.5" />
                Filters
              </button>
              <div className="flex items-center gap-2 px-3 py-1.5 text-[13px] font-medium text-[#A1A1AA]">
                <Clock className="w-3.5 h-3.5" />
                Last 90 Days
              </div>
            </div>
          </div>

          {/* Alert Banner */}
          <div className="flex items-center justify-between px-4 py-3 mb-6 rounded-md border border-[#7F1D1D] bg-[#450a0a]">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-[#FCA5A5]" />
              <div>
                <span className="text-[13px] font-semibold text-[#FCA5A5] mr-2">Biggest leak: Interview Stage</span>
                <span className="text-[13px] text-[#FCA5A5] opacity-90">26.9% of candidates are lost here. Investigate Interviewer feedback timelines.</span>
              </div>
            </div>
            <button className="text-[13px] font-semibold text-[#FCA5A5] hover:text-white transition-colors">Investigate</button>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="kpi-card">
              <div className="flex items-center justify-between mb-2">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">Total Applications</div>
                <Users className="w-4 h-4 text-[#71717A]" />
              </div>
              <div className="text-2xl font-bold text-white">6,633</div>
              <div className="text-[12px] mt-1 text-[#A1A1AA]"><span className="text-[#22C55E] font-medium">↑12%</span> vs last period</div>
            </div>
            
            <div className="kpi-card">
              <div className="flex items-center justify-between mb-2">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">Total Joined</div>
                <UserCheck className="w-4 h-4 text-[#71717A]" />
              </div>
              <div className="text-2xl font-bold text-white">1,470</div>
              <div className="text-[12px] mt-1 text-[#A1A1AA]"><span className="text-[#22C55E] font-medium">↑5%</span> 22.2% conversion</div>
            </div>

            <div className="kpi-card">
              <div className="flex items-center justify-between mb-2">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">Accepted, Never Joined</div>
                <AlertTriangle className="w-4 h-4 text-[#71717A]" />
              </div>
              <div className="text-2xl font-bold text-white">221</div>
              <div className="text-[12px] mt-1 text-[#A1A1AA]"><span className="text-[#EF4444] font-medium">↑8%</span> invisible loss</div>
            </div>

            <div className="kpi-card">
              <div className="flex items-center justify-between mb-2">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">Median Time To Hire</div>
                <Clock className="w-4 h-4 text-[#71717A]" />
              </div>
              <div className="text-2xl font-bold text-white">54 <span className="text-[14px] font-normal text-[#A1A1AA]">days</span></div>
              <div className="text-[12px] mt-1 text-[#A1A1AA]"><span className="text-[#EAB308] font-medium">↑2 days</span> app to join</div>
            </div>
          </div>

          {/* Recruitment Funnel */}
          <div className="card mb-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-[14px] font-bold text-white">Recruitment Funnel</h3>
                <p className="text-[12px] text-[#A1A1AA] mt-1">Candidates entering each stage, and drop-off rates.</p>
              </div>
              <div className="flex items-center gap-4 text-[11px] font-medium text-[#D4D4D8]">
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-[#22C55E]"></div>&lt;18%</div>
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-[#EAB308]"></div>18-30%</div>
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-[#EF4444]"></div>&gt;30%</div>
              </div>
            </div>

            <div className="space-y-0 relative">
              {/* Applications */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[13px] text-[#D4D4D8]">Applications</span>
                  <span className="text-[13px] text-white">6,633</span>
                </div>
                <div className="h-[28px] bg-[#3F3F46] rounded-r-md" style={{width: '100%'}}></div>
                <div className="flex items-center gap-2 pl-4 py-1.5">
                  <span className="text-[10px] font-bold text-[#EAB308]">↓ -23%</span>
                  <span className="text-[10px] text-[#71717A]">1,528 candidates lost</span>
                </div>
              </div>

              {/* Screening */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[13px] text-[#D4D4D8]">Screening</span>
                  <span className="text-[13px] text-white">5,105</span>
                </div>
                <div className="h-[28px] bg-[#3F3F46] rounded-r-md" style={{width: '77%'}}></div>
                <div className="flex items-center gap-2 pl-4 py-1.5">
                  <span className="text-[10px] font-bold text-[#EAB308]">↓ -18%</span>
                  <span className="text-[10px] text-[#71717A]">919 candidates lost</span>
                </div>
              </div>

              {/* Interview */}
              <div className="relative">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[13px] font-bold text-[#FCA5A5]">Interview</span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#7F1D1D] text-[#FCA5A5]">BIGGEST LEAK</span>
                  </div>
                  <span className="text-[13px] text-white">4,186</span>
                </div>
                <div className="h-[28px] bg-[#EF4444] rounded-r-md border border-[#FCA5A5]/30" style={{width: '63%'}}></div>
                <div className="flex items-center gap-2 pl-4 py-1.5">
                  <span className="text-[10px] font-bold text-[#FCA5A5]">↓ -26.9%</span>
                  <span className="text-[10px] text-[#71717A]">1,125 candidates lost</span>
                </div>
              </div>

              {/* Technical Round */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[13px] text-[#D4D4D8]">Technical Round</span>
                  <span className="text-[13px] text-white">3,061</span>
                </div>
                <div className="h-[28px] bg-[#3F3F46] rounded-r-md" style={{width: '46%'}}></div>
                <div className="flex items-center gap-2 pl-4 py-1.5">
                  <span className="text-[10px] font-bold text-[#22C55E]">↓ -15%</span>
                  <span className="text-[10px] text-[#71717A]">458 candidates lost</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            {/* Department comparison */}
            <div className="card">
              <h3 className="text-[14px] font-bold text-white">Department comparison</h3>
              <p className="text-[12px] text-[#A1A1AA] mt-1 mb-6">Compare the worst leak per department.</p>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-[12px] mb-1.5">
                    <span className="text-[#D4D4D8]">IT</span>
                    <span className="text-white font-medium">48.7% Drop-off</span>
                  </div>
                  <div className="flex gap-1 h-[6px] mb-1">
                    <div className="bg-[#EF4444] rounded-full h-full" style={{width: '48.7%'}}></div>
                    <div className="bg-[#27272A] rounded-full h-full flex-1"></div>
                  </div>
                  <div className="text-[10px] text-[#71717A]">Worst stage: Interview • 2,536 applied → 427 joined (16.8%)</div>
                </div>

                <div>
                  <div className="flex justify-between text-[12px] mb-1.5">
                    <span className="text-[#D4D4D8]">Sales</span>
                    <span className="text-white font-medium">46.0% Drop-off</span>
                  </div>
                  <div className="flex gap-1 h-[6px] mb-1">
                    <div className="bg-[#F97316] rounded-full h-full" style={{width: '46%'}}></div>
                    <div className="bg-[#27272A] rounded-full h-full flex-1"></div>
                  </div>
                  <div className="text-[10px] text-[#71717A]">Worst stage: Offer • 1,978 applied → 254 joined (12.8%)</div>
                </div>

                <div>
                  <div className="flex justify-between text-[12px] mb-1.5">
                    <span className="text-[#D4D4D8]">Finance</span>
                    <span className="text-white font-medium">23.9% Drop-off</span>
                  </div>
                  <div className="flex gap-1 h-[6px] mb-1">
                    <div className="bg-[#EAB308] rounded-full h-full" style={{width: '23.9%'}}></div>
                    <div className="bg-[#27272A] rounded-full h-full flex-1"></div>
                  </div>
                  <div className="text-[10px] text-[#71717A]">Worst stage: Applications • 1,188 applied → 402 joined (33.8%)</div>
                </div>
              </div>
            </div>

            {/* Drop-off Reasons */}
            <div className="card">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h3 className="text-[14px] font-bold text-white">Drop-off Reasons</h3>
                  <p className="text-[12px] text-[#A1A1AA] mt-1">Feedback for selected stage.</p>
                </div>
                <button className="flex items-center gap-2 px-2.5 py-1.5 rounded-md border border-[#27272A] bg-[#18181B] text-[11px] text-[#D4D4D8]">
                  After Technical Round <ChevronDown className="w-3 h-3" />
                </button>
              </div>

              <div className="space-y-3.5 mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-32 text-[12px] text-[#D4D4D8] truncate">Skill Mismatch</div>
                  <div className="flex-1 h-[8px] bg-[#27272A] rounded-r-md"><div className="h-full bg-[#FCA5A5] rounded-r-md" style={{width: '85%'}}></div></div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 text-[12px] text-[#D4D4D8] truncate">Domain Knowledge</div>
                  <div className="flex-1 h-[8px] bg-[#27272A] rounded-r-md"><div className="h-full bg-[#FCD34D] rounded-r-md" style={{width: '70%'}}></div></div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 text-[12px] text-[#D4D4D8] truncate">Candidate Withdrew</div>
                  <div className="flex-1 h-[8px] bg-[#27272A] rounded-r-md"><div className="h-full bg-[#94A3B8] rounded-r-md" style={{width: '55%'}}></div></div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 text-[12px] text-[#D4D4D8] truncate">Salary Expectations</div>
                  <div className="flex-1 h-[8px] bg-[#27272A] rounded-r-md"><div className="h-full bg-[#64748B] rounded-r-md" style={{width: '40%'}}></div></div>
                </div>
              </div>

              <div className="p-3 rounded-md border border-[#27272A] bg-[#18181B] text-[12px] text-[#A1A1AA]">
                Top reason: <span className="text-white">Technical skill mismatch</span> — 22.5% of 458 lost candidates.
              </div>
            </div>
          </div>

          {/* Data Intake Center */}
          <div className="mb-8">
            <h3 className="text-[14px] font-bold text-white mb-4">Data Intake Center</h3>
            <div className="border border-dashed border-[#3F3F46] rounded-lg p-10 flex flex-col items-center justify-center text-center">
              <UploadCloud className="w-8 h-8 text-[#A1A1AA] mb-4" />
              <p className="text-[13px] text-[#D4D4D8] mb-1">Drag and drop CSV or Excel files</p>
              <p className="text-[12px] text-[#71717A] mb-5">Update candidate statuses, feedback, or department mappings.</p>
              <button className="px-4 py-2 rounded-md bg-white text-black text-[13px] font-medium hover:bg-gray-100 transition-colors">
                Browse Files
              </button>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
