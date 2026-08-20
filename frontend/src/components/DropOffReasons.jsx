'use client';
import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, Tooltip, Cell } from 'recharts';

export default function DropOffReasons({ data, totalLost }) {
  const colors = ['#19C3C3','#34D399','#F5B335','#FF4F5E','#7DD3FC','#60A5FA','#93C5FD'];
  const sorted = [...data].sort((a,b)=>b.count-a.count);
  const top = sorted[0];
  const pct = totalLost>0 ? ((top.count/totalLost)*100) : 0;
  return (
    <div className="rounded-lg border border-[#2D3E54] bg-gradient-to-br from-[#1A2332] to-[#0F1621] p-8 shadow-lg">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-2xl text-[#F0F4F8] font-bold">Why Candidates Drop Off</h3>
          <div className="text-sm text-[#7B8BA8] mt-3 font-medium">Rejection reasons and withdrawal patterns</div>
        </div>
        <div className="text-xs text-[#7B8BA8] font-bold uppercase tracking-wider">After Technical Round</div>
      </div>

      <div style={{ height: 320 }}>
        <ResponsiveContainer>
          <BarChart layout="vertical" data={sorted} margin={{ left: 150, right: 20 }}>
            <XAxis type="number" stroke="#4A5D7A" style={{ fontSize: '12px', fontWeight: '600' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #2D3E54', borderRadius: '8px', padding: '12px' }}
              labelStyle={{ color: '#D0D7E8' }}
              formatter={(value) => `${value} candidates`}
            />
            <Bar dataKey="count" radius={[0, 8, 8, 0]}>
              {sorted.map((entry, idx) => (
                <Cell key={`cell-${idx}`} fill={colors[idx % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-8 border border-[#2D3E54] rounded-lg p-5 text-sm text-[#D0D7E8] bg-[#1A2332]">
        <span className="text-[#7B8BA8] font-bold uppercase tracking-wider">Top Reason:</span> <span className="font-bold text-[#F0F4F8] ml-2">{top.reason}</span> <span className="text-[#7B8BA8] font-semibold">— {pct.toFixed(1)}% of {totalLost} candidates</span>
      </div>
    </div>
  );
}
