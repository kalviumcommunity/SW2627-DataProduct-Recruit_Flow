export const funnelData = [
  { stage: 'Applications', candidates: 6633, medianDays: 2.2 },
  { stage: 'Screening', candidates: 5105, medianDays: 3.7 },
  { stage: 'Interview', candidates: 4186, medianDays: 5.1 },
  { stage: 'Technical Round', candidates: 3061, medianDays: 6.9 },
  { stage: 'HR Round', candidates: 2603, medianDays: 3.6 },
  { stage: 'Offer', candidates: 2208, medianDays: 6.5 },
  { stage: 'Accepted', candidates: 1691, medianDays: 6.2 },
  { stage: 'Joined', candidates: 1470, medianDays: 19.9 }
];

export const departments = [
  {
    name: 'IT',
    value: 48.7,
    worstStage: 'Interview',
    applied: 2536,
    joined: 427
  },
  {
    name: 'Sales',
    value: 46,
    worstStage: 'Offer',
    applied: 1978,
    joined: 254
  },
  {
    name: 'Finance',
    value: 23.9,
    worstStage: 'Applications',
    applied: 1188,
    joined: 402
  },
  {
    name: 'Operations',
    value: 18.7,
    worstStage: 'Applications',
    applied: 931,
    joined: 387
  }
];

export const dropOffReasons = [
  { reason: 'Technical skill mismatch', count: 103 },
  { reason: 'Domain knowledge gap', count: 91 },
  { reason: 'Candidate withdrew', count: 72 },
  { reason: 'Certification missing', count: 63 },
  { reason: 'Salary expectations too high', count: 60 },
  { reason: 'Other', count: 47 },
  { reason: 'Role mismatch', count: 32 }
];

export const stageTimeData = [
  { stage: 'Applications', days: 2.2 },
  { stage: 'Screening', days: 3.7 },
  { stage: 'Interview', days: 5.1 },
  { stage: 'Technical', days: 6.9 },
  { stage: 'HR', days: 3.6 },
  { stage: 'Offer', days: 6.5 },
  { stage: 'Accepted', days: 6.2 },
  { stage: 'Joined', days: 19.9 }
];

export const roles = [
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Data Analyst',
  'Product Manager'
];

export const hiringPeriods = ['Last 30 days', 'Last 90 days', 'Last 6 months', 'Last 12 months'];

export const companyInfo = {
  name: 'ABC Technologies',
  scopeText: 'all departments'
};
