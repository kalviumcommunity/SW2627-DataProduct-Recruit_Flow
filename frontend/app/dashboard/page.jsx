'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import './dashboard.css';
import {
  Search, Bell, Download, Filter, Users, UserCheck, AlertTriangle, Clock,
  LayoutDashboard, Filter as FunnelIcon, Users as DeptIcon, HardDrive,
  Settings, HelpCircle, UploadCloud, ChevronDown, CheckCircle, XCircle,
  GitPullRequest, MessageSquare, AlertCircle, ArrowUpRight, ArrowDownRight,
  Sparkles, X, ChevronRight, RefreshCw, FileText, Check, ArrowRight
} from 'lucide-react';
import FunnelChart from '../../components/dashboard/FunnelChart';
import PerformanceChart from '../../components/dashboard/PerformanceChart';
import ReasonChart from '../../components/dashboard/ReasonChart';
import BottleneckCard from '../../components/dashboard/BottleneckCard';

export default function DashboardPage() {
  const [activeNav, setActiveNav] = useState('overview');
  const [selectedContributor, setSelectedContributor] = useState(null);
  const [reasonStage, setReasonStage] = useState('After Technical Round');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState('All Departments');
  const [isDeptDropdownOpen, setIsDeptDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Live API States
  const [funnelData, setFunnelData] = useState(null);
  const [dropoffReasons, setDropoffReasons] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [journeyData, setJourneyData] = useState(null);
  const [isApiLoading, setIsApiLoading] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'funnel', label: 'Funnel', icon: FunnelIcon },
    { id: 'departments', label: 'Departments', icon: DeptIcon },
    { id: 'intake', label: 'Data Intake', icon: HardDrive },
  ];

  // Fetch live backend API analytics data
  useEffect(() => {
    async function fetchAnalytics() {
      setIsApiLoading(true);
      const deptQuery = selectedDepartment !== 'All Departments' ? `?department=${encodeURIComponent(selectedDepartment)}` : '';
      
      try {
        const [funnelRes, reasonsRes, summaryRes, journeyRes] = await Promise.allSettled([
          fetch(`http://localhost:8000/analytics/funnel${deptQuery}`),
          fetch(`http://localhost:8000/analytics/dropoff-reasons?stage=${encodeURIComponent(reasonStage)}${selectedDepartment !== 'All Departments' ? `&department=${encodeURIComponent(selectedDepartment)}` : ''}`),
          fetch(`http://localhost:8000/analytics/summary${deptQuery}`),
          fetch(`http://localhost:8000/analytics/journey${deptQuery}`)
        ]);

        if (funnelRes.status === 'fulfilled' && funnelRes.value.ok) {
          const json = await funnelRes.value.json();
          setFunnelData(json);
        }
        if (reasonsRes.status === 'fulfilled' && reasonsRes.value.ok) {
          const json = await reasonsRes.value.json();
          setDropoffReasons(json);
        }
        if (summaryRes.status === 'fulfilled' && summaryRes.value.ok) {
          const json = await summaryRes.value.json();
          setSummaryData(json);
        }
        if (journeyRes.status === 'fulfilled' && journeyRes.value.ok) {
          const json = await journeyRes.value.json();
          setJourneyData(json);
        }
      } catch (err) {
        console.warn('Backend API connection unavailable, displaying optimized offline data.', err);
      } finally {
        setIsApiLoading(false);
      }
    }

    fetchAnalytics();
  }, [selectedDepartment, reasonStage]);

  const contributorsData = [
    {
      id: 'sam',
      name: 'Samir Patel',
      handle: '@sam',
      role: 'Senior Backend Engineer',
      department: 'Engineering',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
      totalReviews: 142,
      reviewsPerDay: 4.2,
      status: 'Active',
      statusColor: '#22C55E',
      metrics: {
        firstPrDays: 8,
        avgMaintainerResponse: 12,
        totalPrs: 5,
        reviewsReceived: 17,
        issuesClosed: 4,
        prsMerged: 'No'
      },
      timeline: [
        { title: 'Joined Community', date: 'Oct 12', desc: 'First login via GitHub OAuth', badge: 'Completed', color: '#22C55E' },
        { title: 'First PR Submitted', date: 'Oct 20', desc: 'Fix race condition in authentication module (#42)', badge: 'PR #42', color: '#38BDF8' },
        { title: 'Maintainer Response', date: 'Nov 01', desc: 'Reviewed by @core-dev-lead: "Thanks for the PR. We need to add tests for edge cases before merging."', badge: 'Delayed (+4 days)', color: '#EF4444' },
        { title: 'Changes Requested', date: 'Nov 02', desc: '3 distinct change requests logged regarding token refresh handling.', badge: 'Changes Needed', color: '#F59E0B' },
        { title: 'Contributor Question', date: 'Nov 05', desc: '"Could you clarify the expected behavior for token expiration in the new test suite?"', badge: 'Question', color: '#818CF8' },
        { title: 'No further contribution', date: 'Present', desc: 'Stalled waiting for maintainer clarification.', badge: 'Dormant', color: '#EF4444' },
      ],
      risk: {
        level: 'High (84%)',
        desc: 'This contributor shows signals indicating they may abandon their first PR due to friction in the review process.',
        breakdown: [
          { name: 'Response Speed', status: 'Needs Attention', color: '#EF4444' },
          { name: 'Review Expectations', status: 'Needs Attention', color: '#EF4444' },
          { name: 'Codebase Complexity', status: 'Medium', color: '#F59E0B' },
          { name: 'Maintainer Tone', status: 'Neutral', color: '#94A3B8' },
          { name: 'Peer Assistance', status: 'None', color: '#EF4444' },
        ]
      }
    },
    {
      id: 'sarah',
      name: 'Sarah Jenkins',
      handle: '@sarah',
      role: 'Senior Engineer',
      department: 'Engineering',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&auto=format&fit=crop&q=80',
      totalReviews: 142,
      reviewsPerDay: 4.2,
      status: 'Active',
      statusColor: '#22C55E'
    },
    {
      id: 'marcus',
      name: 'Marcus Rivera',
      handle: '@marcus',
      role: 'Product Designer',
      department: 'Design',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
      totalReviews: 89,
      reviewsPerDay: 2.8,
      status: 'At Capacity',
      statusColor: '#F59E0B'
    },
    {
      id: 'elena',
      name: 'Elena Lopez',
      handle: '@elena',
      role: 'Talent Lead',
      department: 'Recruiting',
      avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=100&auto=format&fit=crop&q=80',
      totalReviews: 213,
      reviewsPerDay: 6.5,
      status: 'Active',
      statusColor: '#22C55E'
    },
    {
      id: 'david',
      name: 'David Kim',
      handle: '@david',
      role: 'Backend Dev',
      department: 'Engineering',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80',
      totalReviews: 56,
      reviewsPerDay: 1.5,
      status: 'Active',
      statusColor: '#22C55E'
    },
    {
      id: 'aisha',
      name: 'Aisha Williams',
      handle: '@aisha',
      role: 'UX Researcher',
      department: 'Design',
      avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&auto=format&fit=crop&q=80',
      totalReviews: 112,
      reviewsPerDay: 3.4,
      status: 'At Capacity',
      statusColor: '#F59E0B'
    }
  ];

  return (
    <div className="dashboard-layout">
      {/* ------------------------------------------------------------- */}
      {/* SIDEBAR                                                       */}
      {/* ------------------------------------------------------------- */}
      <aside className="dashboard-sidebar">
        <div className="px-5 pt-6 pb-5">
          <div className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Recruitflow</span>
          </div>
          <div className="text-[10px] text-[#A1A1AA] font-bold uppercase tracking-widest mt-1">TALENT COMMAND</div>
        </div>

        <div className="px-4 mb-6">
          <button className="w-full flex items-center justify-center gap-2 py-2 rounded-md bg-[#27272A] border border-[#3F3F46] text-white text-[13px] font-medium hover:bg-[#3F3F46] hover:border-[#52525B] transition-all shadow-sm">
            <span className="text-[16px] leading-none mb-0.5 font-light">+</span>
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
                onClick={() => {
                  setActiveNav(item.id);
                  setSelectedContributor(null);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-[13px] font-medium transition-all ${
                  isActive ? 'bg-[#27272A] text-white shadow-sm' : 'text-[#A1A1AA] hover:bg-[#18181B] hover:text-[#D4D4D8]'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="px-3 pb-3 space-y-1">
          <Link
            href="/upload"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium text-[#38BDF8] hover:bg-[#18181B] hover:text-white transition-colors"
          >
            <UploadCloud className="w-4 h-4 shrink-0" />
            Batch Upload Hub
          </Link>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium text-[#A1A1AA] hover:bg-[#18181B] hover:text-[#D4D4D8] transition-colors">
            <Settings className="w-4 h-4 shrink-0" />
            Settings
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium text-[#A1A1AA] hover:bg-[#18181B] hover:text-[#D4D4D8] transition-colors">
            <HelpCircle className="w-4 h-4 shrink-0" />
            Support
          </button>
        </div>

        <div className="px-4 py-4 border-t border-[#27272A] flex items-center gap-3 bg-[#101013]">
          <div className="w-8 h-8 rounded-full bg-[#3F3F46] overflow-hidden shrink-0 ring-1 ring-[#52525B]">
            <img src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80" alt="Alex Mercer" className="w-full h-full object-cover" />
          </div>
          <div className="min-w-0">
            <div className="text-[13px] font-semibold text-white truncate">Alex Mercer</div>
            <div className="text-[11px] text-[#A1A1AA] truncate">Lead Recruiter</div>
          </div>
        </div>
      </aside>

      {/* ------------------------------------------------------------- */}
      {/* MAIN CONTAINER                                                */}
      {/* ------------------------------------------------------------- */}
      <main className="dashboard-main">
        {/* TOPBAR */}
        <header className="dashboard-topbar">
          <div className="flex-1 max-w-[340px] relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#71717A]" />
            <input
              type="text"
              placeholder="Search candidates, reqs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 rounded-md border border-[#27272A] bg-[#141417] text-[13px] text-white placeholder-[#71717A] focus:outline-none focus:border-[#52525B] transition-colors"
            />
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-4 text-[13px] font-medium text-[#A1A1AA]">
              <span className="hover:text-white cursor-pointer transition-colors">Department</span>
              <span className="hover:text-white cursor-pointer transition-colors">Job Role</span>
              <span className="hover:text-white cursor-pointer transition-colors">Period</span>
            </div>
            <div className="w-px h-4 bg-[#27272A]"></div>
            <button className="relative text-[#A1A1AA] hover:text-white transition-colors p-1">
              <Bell className="w-4 h-4" />
              <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-[#EF4444] rounded-full ring-2 ring-[#09090B]"></span>
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] bg-[#141417] text-[13px] font-medium text-[#D4D4D8] hover:bg-[#27272A] hover:text-white transition-all">
              <Download className="w-3.5 h-3.5" />
              Export Data
            </button>
          </div>
        </header>

        {/* ----------------------------------------------------------- */}
        {/* VIEW 1: OVERVIEW (Recruitment Funnel Overview)              */}
        {/* ----------------------------------------------------------- */}
        {activeNav === 'overview' && (
          <div className="dashboard-content">
            {/* Header row */}
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Recruitment funnel overview</h1>
                <p className="text-[13px] text-[#A1A1AA] mt-1">ABC Technologies • All departments • 6,633 candidates in scope</p>
              </div>
              <div className="flex items-center gap-3">
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] bg-[#141417] text-[13px] font-medium text-[#D4D4D8] hover:bg-[#27272A] transition-colors">
                  <Filter className="w-3.5 h-3.5" />
                  Filters
                </button>
                <div className="flex items-center gap-2 px-3 py-1.5 text-[13px] font-medium text-[#A1A1AA] border border-[#27272A] rounded-md bg-[#141417]">
                  <Clock className="w-3.5 h-3.5 text-[#71717A]" />
                  Last 90 Days
                </div>
              </div>
            </div>

            {/* Alert Banner: Bottleneck Card Component */}
            <BottleneckCard
              stage="Interview Stage"
              percent={28.9}
              description="28.9% of candidates are lost here. Investigate interviewer feedback timelines."
              onInvestigate={() => setActiveNav('funnel')}
            />

            {/* 4 KPI Cards Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="kpi-card">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">TOTAL APPLICATIONS</div>
                  <Users className="w-4 h-4 text-[#71717A]" />
                </div>
                <div className="text-3xl font-bold text-white tracking-tight">6,633</div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1.5">
                  <span className="text-[#22C55E] font-semibold">↑12%</span> vs last period
                </div>
              </div>

              <div className="kpi-card">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">TOTAL JOINED</div>
                  <UserCheck className="w-4 h-4 text-[#71717A]" />
                </div>
                <div className="text-3xl font-bold text-white tracking-tight">1,470</div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1.5">
                  <span className="text-[#22C55E] font-semibold">↑6%</span> 22.2% conversion
                </div>
              </div>

              <div className="kpi-card">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">ACCEPTED, NEVER JOINED</div>
                  <AlertTriangle className="w-4 h-4 text-[#EF4444]" />
                </div>
                <div className="text-3xl font-bold text-white tracking-tight">221</div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1.5">
                  <span className="text-[#EF4444] font-semibold">↑9%</span> invisible loss
                </div>
              </div>

              <div className="kpi-card">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA]">MEDIAN TIME TO HIRE</div>
                  <Clock className="w-4 h-4 text-[#EAB308]" />
                </div>
                <div className="text-3xl font-bold text-white tracking-tight">54 <span className="text-[14px] font-normal text-[#A1A1AA]">days</span></div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1.5">
                  <span className="text-[#EAB308] font-semibold">↑2 days</span> app to join
                </div>
              </div>
            </div>

            {/* Recruitment Funnel Section using FunnelChart component */}
            <div className="card mb-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-[14px] font-bold text-white tracking-tight">Recruitment Funnel</h3>
                  <p className="text-[12px] text-[#A1A1AA] mt-0.5">Candidates entering each stage, and drop-off rates.</p>
                </div>
                <div className="flex items-center gap-4 text-[11px] font-medium text-[#D4D4D8]">
                  <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-[#22C55E]"></div>&lt;18%</div>
                  <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-[#EAB308]"></div>18-30%</div>
                  <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-[#EF4444]"></div>&gt;30%</div>
                </div>
              </div>

              <FunnelChart
                stages={funnelData?.stages}
                highlightStage="Interview"
              />
            </div>

            {/* Two-column Comparison Grid */}
            <div className="grid grid-cols-2 gap-6 mb-6">
              {/* Department Comparison */}
              <div className="card">
                <h3 className="text-[14px] font-bold text-white tracking-tight">Department comparison</h3>
                <p className="text-[12px] text-[#A1A1AA] mt-0.5 mb-6">Compare the worst leak per department.</p>

                <div className="space-y-5">
                  <div>
                    <div className="flex justify-between text-[12px] mb-1.5">
                      <span className="text-[#D4D4D8] font-semibold">IT</span>
                      <span className="text-white font-bold">48.7% Drop-off</span>
                    </div>
                    <div className="flex gap-1 h-[6px] mb-1.5">
                      <div className="bg-[#EF4444] rounded-full h-full" style={{ width: '48.7%' }}></div>
                      <div className="bg-[#27272A] rounded-full h-full flex-1"></div>
                    </div>
                    <div className="text-[11px] text-[#71717A]">Worst stage: Interview • 2,032 applied → 627 joined (30.8%)</div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[12px] mb-1.5">
                      <span className="text-[#D4D4D8] font-semibold">Sales</span>
                      <span className="text-white font-bold">46.0% Drop-off</span>
                    </div>
                    <div className="flex gap-1 h-[6px] mb-1.5">
                      <div className="bg-[#F97316] rounded-full h-full" style={{ width: '46.0%' }}></div>
                      <div className="bg-[#27272A] rounded-full h-full flex-1"></div>
                    </div>
                    <div className="text-[11px] text-[#71717A]">Worst stage: Offer • 1,874 applied → 254 joined (13.5%)</div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[12px] mb-1.5">
                      <span className="text-[#D4D4D8] font-semibold">Finance</span>
                      <span className="text-white font-bold">23.9% Drop-off</span>
                    </div>
                    <div className="flex gap-1 h-[6px] mb-1.5">
                      <div className="bg-[#EAB308] rounded-full h-full" style={{ width: '23.9%' }}></div>
                      <div className="bg-[#27272A] rounded-full h-full flex-1"></div>
                    </div>
                    <div className="text-[11px] text-[#71717A]">Worst stage: Applications • 1,118 applied → 432 joined (38.6%)</div>
                  </div>
                </div>
              </div>

              {/* Drop-off Reasons using ReasonChart Component */}
              <div className="card">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-[14px] font-bold text-white tracking-tight">Drop-off Reasons</h3>
                    <p className="text-[12px] text-[#A1A1AA] mt-0.5">Feedback for selected stage.</p>
                  </div>
                  <div className="relative">
                    <button 
                      onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                      className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] bg-[#141417] text-[11px] font-medium text-[#D4D4D8] hover:bg-[#27272A] transition-colors"
                    >
                      {reasonStage} <ChevronDown className="w-3 h-3 text-[#71717A]" />
                    </button>
                    {isDropdownOpen && (
                      <div className="absolute right-0 mt-1 w-48 bg-[#18181B] border border-[#27272A] rounded-md shadow-xl z-20 py-1">
                        {['After Screening', 'After Technical Round', 'After HR Round', 'At Offer Stage'].map(stg => (
                          <div 
                            key={stg}
                            onClick={() => { setReasonStage(stg); setIsDropdownOpen(false); }}
                            className="px-3 py-1.5 text-[12px] text-[#D4D4D8] hover:bg-[#27272A] hover:text-white cursor-pointer"
                          >
                            {stg}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <ReasonChart
                  reasons={dropoffReasons?.reasons}
                  topReasonText={
                    <span>
                      Top reason: <span className="text-white font-semibold">Technical skill mismatch</span> — 22.5% of 458 lost candidates.
                    </span>
                  }
                />
              </div>
            </div>

            {/* Data Intake Center Teaser */}
            <div className="mb-4">
              <h3 className="text-[14px] font-bold text-white mb-3 tracking-tight">Data Intake Center</h3>
              <div 
                onClick={() => setActiveNav('intake')}
                className="border border-dashed border-[#3F3F46] bg-[#121215] rounded-lg p-10 flex flex-col items-center justify-center text-center hover:border-[#71717A] hover:bg-[#18181C] cursor-pointer transition-all"
              >
                <UploadCloud className="w-9 h-9 text-[#A1A1AA] mb-3" />
                <p className="text-[13px] font-semibold text-[#FAFAFA] mb-1">Drag and drop CSV or Excel files</p>
                <p className="text-[12px] text-[#71717A] mb-5">Update candidate statuses, feedback, or department mappings.</p>
                <button className="px-4 py-2 rounded-md bg-white text-black text-[13px] font-semibold hover:bg-gray-200 transition-colors">
                  Browse Files
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------------- */}
        {/* VIEW 2: FUNNEL / PR ANALYSIS (Stage & PR Analysis)          */}
        {/* ----------------------------------------------------------- */}
        {activeNav === 'funnel' && (
          <div className="dashboard-content">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Pull Request Analysis</h1>
                <p className="text-[13px] text-[#A1A1AA] mt-1">Deep dive into code review velocity, integration rates, and bottleneck identification across engineering departments.</p>
              </div>
              <div className="flex items-center gap-3">
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] bg-[#141417] text-[13px] font-medium text-[#D4D4D8] hover:bg-[#27272A] transition-colors">
                  <Filter className="w-3.5 h-3.5" />
                  Filters
                </button>
                <div className="flex items-center gap-2 px-3 py-1.5 text-[13px] font-medium text-[#A1A1AA] border border-[#27272A] rounded-md bg-[#141417]">
                  <Clock className="w-3.5 h-3.5 text-[#71717A]" />
                  Last 30 Days
                </div>
              </div>
            </div>

            {/* 5 KPI Metric Cards */}
            <div className="grid grid-cols-5 gap-4 mb-6">
              <div className="kpi-card">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] mb-2">TOTAL PRS</div>
                <div className="text-3xl font-bold text-white">342</div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1">
                  <span className="text-[#22C55E] font-semibold">↑12%</span> vs last period
                </div>
              </div>

              <div className="kpi-card">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] mb-2">AVG PRS / DAY</div>
                <div className="text-3xl font-bold text-white">2.4</div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1">
                  <span className="text-[#22C55E] font-semibold">↑14.0%</span> vs last period
                </div>
              </div>

              <div className="kpi-card">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] mb-2">AVG REVIEW TIME</div>
                <div className="text-3xl font-bold text-white">4.1 <span className="text-[14px] font-normal text-[#A1A1AA]">hrs</span></div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA] flex items-center gap-1">
                  <span className="text-[#22C55E] font-semibold">↓-8.6%</span> vs last period
                </div>
              </div>

              <div className="kpi-card">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] mb-2">MERGE RATE</div>
                <div className="text-3xl font-bold text-white">68%</div>
                <div className="text-[12px] mt-1.5 text-[#A1A1AA]">
                  Target: <span className="text-[#94A3B8]">75%</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[#A1A1AA] mb-2">REVERT RATE</div>
                <div className="text-3xl font-bold text-white">12%</div>
                <div className="text-[12px] mt-1.5 text-[#EF4444] font-semibold flex items-center gap-1">
                  ▲ High Attention
                </div>
              </div>
            </div>

            {/* Charts: PR Volume Over Time using PerformanceChart & Status Distribution */}
            <div className="grid grid-cols-2 gap-6">
              {/* Performance Chart Component */}
              <PerformanceChart
                title="PR Volume Over Time"
                subtitle="Daily open vs merged pull requests"
              />

              {/* Status Distribution */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-[14px] font-bold text-white">Status Distribution</h3>
                    <p className="text-[12px] text-[#A1A1AA] mt-0.5">Current state of active PRs</p>
                  </div>
                </div>

                <div className="h-[220px] flex items-end justify-between gap-6 px-6 pb-4">
                  <div className="flex-1 flex flex-col items-center gap-2">
                    <div className="text-[12px] font-bold text-white">124</div>
                    <div className="w-full bg-[#3B82F6] rounded-t-md" style={{ height: '140px' }}></div>
                    <span className="text-[11px] text-[#A1A1AA]">Review</span>
                  </div>
                  <div className="flex-1 flex flex-col items-center gap-2">
                    <div className="text-[12px] font-bold text-white">86</div>
                    <div className="w-full bg-[#EAB308] rounded-t-md" style={{ height: '100px' }}></div>
                    <span className="text-[11px] text-[#A1A1AA]">Changes</span>
                  </div>
                  <div className="flex-1 flex flex-col items-center gap-2">
                    <div className="text-[12px] font-bold text-white">152</div>
                    <div className="w-full bg-[#22C55E] rounded-t-md" style={{ height: '170px' }}></div>
                    <span className="text-[11px] text-[#A1A1AA]">Approved</span>
                  </div>
                  <div className="flex-1 flex flex-col items-center gap-2">
                    <div className="text-[12px] font-bold text-white">28</div>
                    <div className="w-full bg-[#EF4444] rounded-t-md" style={{ height: '35px' }}></div>
                    <span className="text-[11px] text-[#A1A1AA]">Draft</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------------- */}
        {/* VIEW 3: DEPARTMENTS / CONTRIBUTORS TABLE                    */}
        {/* ----------------------------------------------------------- */}
        {activeNav === 'departments' && (
          <div className="dashboard-content">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Contributors</h1>
                <p className="text-[13px] text-[#A1A1AA] mt-1">Review and manage talent pool contributors.</p>
              </div>
              <div className="flex items-center gap-3">
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#27272A] bg-[#141417] text-[13px] font-medium text-[#D4D4D8] hover:bg-[#27272A] transition-colors">
                  <Filter className="w-3.5 h-3.5" />
                  Filters
                </button>
                <div className="flex items-center gap-2 px-3 py-1.5 text-[13px] font-medium text-[#A1A1AA] border border-[#27272A] rounded-md bg-[#141417]">
                  <Clock className="w-3.5 h-3.5 text-[#71717A]" />
                  Last 90 Days
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="card p-0 overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-[#27272A] bg-[#121215] text-[11px] font-bold uppercase tracking-wider text-[#A1A1AA]">
                    <th className="py-3 px-5">CONTRIBUTOR</th>
                    <th className="py-3 px-5">DEPARTMENT</th>
                    <th className="py-3 px-5">TOTAL REVIEWS</th>
                    <th className="py-3 px-5">REVIEWS/DAY</th>
                    <th className="py-3 px-5">STATUS</th>
                    <th className="py-3 px-5 text-right">ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#27272A] text-[13px]">
                  {contributorsData.map((item) => (
                    <tr key={item.id} className="hover:bg-[#18181D] transition-colors">
                      <td className="py-3.5 px-5 flex items-center gap-3">
                        <img src={item.avatar} alt={item.name} className="w-8 h-8 rounded-full object-cover ring-1 ring-[#3F3F46]" />
                        <div>
                          <div className="font-semibold text-white">{item.name}</div>
                          <div className="text-[11px] text-[#A1A1AA]">{item.role}</div>
                        </div>
                      </td>
                      <td className="py-3.5 px-5 text-[#D4D4D8] font-medium">{item.department}</td>
                      <td className="py-3.5 px-5 text-white font-semibold">{item.totalReviews}</td>
                      <td className="py-3.5 px-5 text-[#D4D4D8]">{item.reviewsPerDay}</td>
                      <td className="py-3.5 px-5">
                        <span 
                          className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold border"
                          style={{
                            backgroundColor: `${item.statusColor}15`,
                            color: item.statusColor,
                            borderColor: `${item.statusColor}30`
                          }}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-right">
                        <button
                          onClick={() => setSelectedContributor(item.id === 'sam' ? item : contributorsData[0])}
                          className="text-[12px] font-medium text-[#38BDF8] hover:text-white transition-colors"
                        >
                          View Profile
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------------- */}
        {/* VIEW 4: DATA INTAKE (Batch Selection & Upload Page)         */}
        {/* ----------------------------------------------------------- */}
        {activeNav === 'intake' && (
          <div className="dashboard-content">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Data Intake & Batch Management</h1>
                <p className="text-[13px] text-[#A1A1AA] mt-1">Upload and manage recruitment datasets, parse logs, and trigger analytics pipelines.</p>
              </div>
              <Link
                href="/upload"
                className="px-4 py-2 rounded-md bg-[#38BDF8] text-black text-xs font-bold hover:bg-[#7dd3fc] transition-colors"
              >
                Open Full Ingestion Studio →
              </Link>
            </div>

            {/* Batch Options */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <Link href="/upload" className="card hover:border-[#38BDF8] transition-all cursor-pointer bg-[#141417] block">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-md bg-[#38BDF8]/15 flex items-center justify-center text-[#38BDF8]">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <h4 className="text-[14px] font-bold text-white">Create New Batch</h4>
                </div>
                <p className="text-[12px] text-[#A1A1AA]">Initialize a fresh isolated recruitment batch with automated schema validation.</p>
              </Link>

              <Link href="/upload" className="card hover:border-[#22C55E] transition-all cursor-pointer bg-[#141417] block">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-md bg-[#22C55E]/15 flex items-center justify-center text-[#22C55E]">
                    <RefreshCw className="w-4 h-4" />
                  </div>
                  <h4 className="text-[14px] font-bold text-white">Append to Batch</h4>
                </div>
                <p className="text-[12px] text-[#A1A1AA]">Add newly submitted candidate profiles and interview records to an active batch.</p>
              </Link>

              <Link href="/upload" className="card hover:border-[#EF4444] transition-all cursor-pointer bg-[#141417] block">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-md bg-[#EF4444]/15 flex items-center justify-center text-[#EF4444]">
                    <XCircle className="w-4 h-4" />
                  </div>
                  <h4 className="text-[14px] font-bold text-white">Clear / Reset Batch</h4>
                </div>
                <p className="text-[12px] text-[#A1A1AA]">Purge staging records and rebuild canonical candidate journey views.</p>
              </Link>
            </div>

            {/* Drag and Drop Zone */}
            <div className="card">
              <h3 className="text-[14px] font-bold text-white mb-3">Upload Recruitment Spreadsheets</h3>
              <div className="border border-dashed border-[#3F3F46] rounded-lg p-12 flex flex-col items-center justify-center text-center bg-[#101014]">
                <UploadCloud className="w-10 h-10 text-[#A1A1AA] mb-4" />
                <p className="text-[14px] font-semibold text-white mb-1">Drag and drop CSV or Excel files here</p>
                <p className="text-[12px] text-[#71717A] mb-5">Supported files: candidates.csv, interviews.csv, offers.csv, onboarding.csv</p>
                <Link
                  href="/upload"
                  className="px-5 py-2.5 rounded-md bg-white text-black text-[13px] font-semibold hover:bg-gray-200 transition-colors shadow"
                >
                  Browse Files & Ingest Batch
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------------- */}
        {/* MODAL / VIEW 5: CONTRIBUTOR JOURNEY (@sam)                  */}
        {/* ----------------------------------------------------------- */}
        {selectedContributor && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6 overflow-y-auto">
            <div className="bg-[#121215] border border-[#27272A] rounded-xl w-full max-w-5xl overflow-hidden shadow-2xl animate-in fade-in duration-200">
              {/* Modal Header */}
              <div className="px-6 py-5 border-b border-[#27272A] flex items-center justify-between bg-[#18181D]">
                <div>
                  <div className="text-[11px] text-[#A1A1AA] uppercase tracking-wider font-semibold">Contributors &gt; {selectedContributor.handle}</div>
                  <h2 className="text-xl font-bold text-white mt-0.5">Contributor Journey: {selectedContributor.handle}</h2>
                </div>
                <div className="flex items-center gap-3">
                  <button className="px-3 py-1.5 rounded-md border border-[#27272A] bg-[#27272A] text-[12px] font-medium text-white hover:bg-[#3F3F46] transition-colors">
                    Contact
                  </button>
                  <button className="px-3 py-1.5 rounded-md border border-[#7F1D1D] bg-[#450a0a] text-[12px] font-medium text-[#FCA5A5] hover:bg-[#7F1D1D] transition-colors flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Mark At Risk
                  </button>
                  <button 
                    onClick={() => setSelectedContributor(null)}
                    className="text-[#A1A1AA] hover:text-white transition-colors p-1"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* 6 Quick Metrics Row */}
              <div className="grid grid-cols-6 divide-x divide-[#27272A] border-b border-[#27272A] bg-[#141417]">
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-[#A1A1AA]">FIRST PR CONTRIBUTION</div>
                  <div className="text-xl font-bold text-white mt-1">8 <span className="text-[12px] font-normal text-[#A1A1AA]">days</span></div>
                </div>
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-[#A1A1AA]">AVG MAINTAINER RESPONSE</div>
                  <div className="text-xl font-bold text-white mt-1">12 <span className="text-[12px] font-normal text-[#A1A1AA]">days</span></div>
                  <div className="text-[10px] text-[#EF4444] font-medium">+4 days avg</div>
                </div>
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-[#A1A1AA]">TOTAL PRS</div>
                  <div className="text-xl font-bold text-white mt-1">5</div>
                </div>
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-[#A1A1AA]">REVIEWS RECEIVED</div>
                  <div className="text-xl font-bold text-white mt-1">17</div>
                </div>
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-[#A1A1AA]">ISSUES CLOSED</div>
                  <div className="text-xl font-bold text-white mt-1">4</div>
                </div>
                <div className="p-4">
                  <div className="text-[10px] font-bold uppercase text-[#A1A1AA]">PRS MERGED</div>
                  <div className="text-xl font-bold text-[#EF4444] mt-1">No</div>
                </div>
              </div>

              {/* Modal Body: Timeline Left, Risk Cards Right */}
              <div className="p-6 grid grid-cols-3 gap-6 max-h-[70vh] overflow-y-auto">
                {/* Journey Timeline (2 cols) */}
                <div className="col-span-2 space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-[14px] font-bold text-white">Journey Timeline</h3>
                    <span className="text-[11px] text-[#A1A1AA]">Chronological activity</span>
                  </div>

                  <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#27272A]">
                    {selectedContributor.timeline && selectedContributor.timeline.map((event, idx) => (
                      <div key={idx} className="relative">
                        {/* Dot */}
                        <div 
                          className="absolute -left-6 top-1 w-3 h-3 rounded-full border-2 border-[#121215]"
                          style={{ backgroundColor: event.color }}
                        ></div>
                        <div className="bg-[#18181D] border border-[#27272A] rounded-lg p-4">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-[13px] font-bold text-white">{event.title}</span>
                            <span className="text-[11px] text-[#71717A]">{event.date}</span>
                          </div>
                          <p className="text-[12px] text-[#A1A1AA] mb-2">{event.desc}</p>
                          <span 
                            className="inline-block px-2 py-0.5 rounded text-[10px] font-bold"
                            style={{ backgroundColor: `${event.color}15`, color: event.color }}
                          >
                            {event.badge}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Right Cards: Risk & Breakdown (1 col) */}
                <div className="space-y-6">
                  {/* Potential Retention Risk */}
                  <div className="card bg-[#1E1114] border-[#7F1D1D]/40">
                    <div className="flex items-center gap-2 text-[#EF4444] text-[13px] font-bold mb-2">
                      <AlertTriangle className="w-4 h-4" />
                      Potential Retention Risk
                    </div>
                    <p className="text-[12px] text-[#D4D4D8] mb-3">{selectedContributor.risk?.desc}</p>
                    <div className="flex items-center justify-between py-2 border-t border-[#7F1D1D]/30 mb-3">
                      <span className="text-[11px] text-[#A1A1AA]">Risk Level:</span>
                      <span className="text-[12px] font-bold text-[#EF4444]">{selectedContributor.risk?.level}</span>
                    </div>
                    <button className="w-full py-1.5 rounded bg-[#27272A] hover:bg-[#3F3F46] text-white text-[12px] font-medium transition-colors">
                      View Similar Contributors
                    </button>
                  </div>

                  {/* Experience Breakdown */}
                  <div className="card">
                    <h4 className="text-[13px] font-bold text-white mb-3">Experience Breakdown</h4>
                    <div className="space-y-2.5">
                      {selectedContributor.risk?.breakdown.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between text-[12px] py-1 border-b border-[#27272A] last:border-none">
                          <span className="text-[#D4D4D8]">{item.name}</span>
                          <span 
                            className="px-2 py-0.5 rounded text-[10px] font-bold"
                            style={{ backgroundColor: `${item.color}15`, color: item.color }}
                          >
                            {item.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
