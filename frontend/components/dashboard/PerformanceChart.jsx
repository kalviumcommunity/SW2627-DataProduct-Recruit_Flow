'use client';

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function PerformanceChart({ data }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Hiring velocity</h2>
          <p className="text-sm text-slate-400">Average candidates processed per week.</p>
        </div>
      </div>
      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="week" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
            <Line type="monotone" dataKey="count" stroke="#38bdf8" strokeWidth={3} dot={{ r: 3, fill: '#22d3ee' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
