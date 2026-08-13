'use client';

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';

export default function FunnelChart({ data, highlightStage }) {
  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 24, right: 10, left: 0, bottom: 0 }} layout="vertical" barGap={12}>
          <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} horizontal={false} />
          <XAxis type="number" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="stage" width={140} tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
          <Bar dataKey="count" radius={[8, 8, 8, 8]} barSize={18} label={{ position: 'right', fill: '#cbd5e1' }}>
            {data.map((entry) => (
              <Cell key={entry.stage} fill={entry.stage === highlightStage ? '#fb7185' : '#38bdf8'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
