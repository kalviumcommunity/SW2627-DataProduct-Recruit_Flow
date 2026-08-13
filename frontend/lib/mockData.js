export const dashboardData = {
  kpis: [
    { label: 'Total Candidates', value: '2,450', delta: '+12.4%' },
    { label: 'Offers', value: '320', delta: '13.1% conversion' },
    { label: 'Joined', value: '180', delta: '56.3% offer → join' },
    { label: 'Overall Drop-off', value: '42%', delta: 'High' }
  ],
  funnel: [
    { stage: 'Applied', count: 2450 },
    { stage: 'Screening', count: 1900 },
    { stage: 'Interview', count: 1100 },
    { stage: 'Offer', count: 320 },
    { stage: 'Joined', count: 180 }
  ],
  weeklyPerformance: [
    { week: 'Week 1', count: 380 },
    { week: 'Week 2', count: 420 },
    { week: 'Week 3', count: 470 },
    { week: 'Week 4', count: 430 },
    { week: 'Week 5', count: 500 }
  ],
  bottlenecks: [],
  reasons: [
    { reason: 'Technical skill mismatch', value: 31 },
    { reason: 'Salary', value: 24 },
    { reason: 'Interview timing', value: 18 },
    { reason: 'Location', value: 12 },
    { reason: 'Other', value: 15 }
  ]
};
