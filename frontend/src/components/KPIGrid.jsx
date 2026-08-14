import React from 'react';
import KPICard from './KPICard';
import { Users, Calendar, File, UserCheck, AlertTriangle, Clock } from 'lucide-react';
import { funnelData } from '../data/mockRecruitmentData';
import { calculateEndToEndConversion, calculateOfferAcceptance, calculateAcceptedNeverJoined } from '../utils/recruitmentAnalytics';

export default function KPIGrid({ applications, interviewed, offers, accepted, joined }) {
  const apps = applications ?? funnelData[0].candidates;
  const interviewedNum = interviewed ?? funnelData[2].candidates;
  const offersNum = offers ?? funnelData[5].candidates;
  const acceptedNum = accepted ?? funnelData[6].candidates;
  const joinedNum = joined ?? funnelData[7].candidates;

  const offersAcceptedPct = calculateOfferAcceptance(offersNum, acceptedNum); // accepted / offers
  const endToEnd = calculateEndToEndConversion(apps, joinedNum);
  const acceptedNeverJoined = calculateAcceptedNeverJoined(acceptedNum, joinedNum);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="flex gap-6 flex-col">
        <KPICard label="APPLICATIONS" value={apps} description="entered the funnel" icon={<Users />} />
        <KPICard label="OFFERS MADE" value={offersNum} description={`${offersAcceptedPct}% accepted`} icon={<File />} />
        <KPICard label="ACCEPTED, NEVER JOINED" value={acceptedNeverJoined} description="invisible losses without onboarding data" icon={<AlertTriangle />} color="red" />
      </div>

      <div className="flex gap-6 flex-col">
        <KPICard label="INTERVIEWED" value={interviewedNum} description="reached interview stage" icon={<Calendar />} />
        <KPICard label="JOINED" value={joinedNum} description={`${endToEnd}% end-to-end conversion`} icon={<UserCheck />} color="green" />
        <KPICard label="MEDIAN TIME TO HIRE" value={`54 days`} description="application to joining" icon={<Clock />} />
      </div>
    </div>
  );
}
