'use client';
import React, { useMemo, useState } from 'react';
import DashboardHeader from '../components/DashboardHeader';
import BiggestLeakAlert from '../components/BiggestLeakAlert';
import DrillDownFilters from '../components/DrillDownFilters';
import KPIGrid from '../components/KPIGrid';
import RecruitmentFunnel from '../components/RecruitmentFunnel';
import DepartmentComparison from '../components/DepartmentComparison';
import StageWiseDropoff from '../components/StageWiseDropoff';
import DropOffReasons from '../components/DropOffReasons';
import StageTimeChart from '../components/StageTimeChart';

import { funnelData, departments, dropOffReasons, stageTimeData, companyInfo } from '../data/mockRecruitmentData';
import { findBiggestLeak, calculateLostCandidates } from '../utils/recruitmentAnalytics';

export default function Dashboard() {
  const [department, setDepartment] = useState('All departments');
  const [role, setRole] = useState('All roles');
  const [period, setPeriod] = useState('Last 90 days');

  const reset = () => {
    setDepartment('All departments');
    setRole('All roles');
    setPeriod('Last 90 days');
  };

  // For now we use funnelData directly. Filters are wired for future backend.
  const filteredFunnel = funnelData;

  const biggest = useMemo(() => findBiggestLeak(filteredFunnel), [filteredFunnel]);
  const totalLost = useMemo(() => {
    let sum = 0;
    for (let i=0;i<filteredFunnel.length-1;i++) {
      sum += calculateLostCandidates(filteredFunnel[i].candidates, filteredFunnel[i+1].candidates);
    }
    return sum;
  }, [filteredFunnel]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0E1A] via-[#0B111A] to-[#0F1623] text-[#E7EDF5] px-8 py-12">
      <div className="mx-auto max-w-[1500px] space-y-10">
        <DashboardHeader />

        <BiggestLeakAlert leak={biggest} />

        <DrillDownFilters department={department} role={role} period={period} setDepartment={setDepartment} setRole={setRole} setPeriod={setPeriod} reset={reset} />

        <div>
          <KPIGrid applications={funnelData[0].candidates} interviewed={funnelData[2].candidates} offers={funnelData[5].candidates} accepted={funnelData[6].candidates} joined={funnelData[7].candidates} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <RecruitmentFunnel funnel={filteredFunnel} biggestLeakFrom={biggest?.from} />
          </div>
          <div>
            <DepartmentComparison departments={departments} />
          </div>
        </div>

        <StageWiseDropoff funnel={filteredFunnel} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <DropOffReasons data={dropOffReasons} totalLost={totalLost} />
          </div>
          <div>
            <StageTimeChart data={stageTimeData} />
          </div>
        </div>
      </div>
    </div>
  );
}
