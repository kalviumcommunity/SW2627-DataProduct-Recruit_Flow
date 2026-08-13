'use client';

import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

const COLORS = ['#38bdf8', '#60a5fa', '#a78bfa', '#fb7185', '#fbbf24'];

export default function ReasonChart({ data }) {
  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="reason" cx="50%" cy="50%" outerRadius={110} innerRadius={60} paddingAngle={4}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
