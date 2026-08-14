'use client';
import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function StageTimeChart({ data }) {
  return (
    <div className="rounded-lg border border-[#2D3E54] bg-gradient-to-br from-[#1A2332] to-[#0F1621] p-8 shadow-lg">
      <h3 className="text-2xl text-[#F0F4F8] font-bold">Time Spent Per Stage</h3>
      <div className="text-sm text-[#7B8BA8] mt-3 mb-8 font-medium">Median days at each funnel stage</div>
      <div style={{ height: 360 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
            <CartesianGrid stroke="#2D3E54" strokeDasharray="3 3" />
            <XAxis 
              dataKey="stage" 
              stroke="#4A5D7A" 
              angle={-45}
              textAnchor="end"
              height={100}
              style={{ fontSize: '12px', fontWeight: '600' }}
            />
            <YAxis stroke="#4A5D7A" style={{ fontSize: '12px', fontWeight: '600' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1A2332', border: '1px solid #2D3E54', borderRadius: '8px', padding: '12px' }}
              labelStyle={{ color: '#D0D7E8' }}
              formatter={(value) => `${value} days`}
            />
            <Bar dataKey="days" fill="#19C3C3" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
