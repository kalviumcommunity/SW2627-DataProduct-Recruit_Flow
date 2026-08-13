export default function BottleneckCard({ from, to, percent, reason }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
      <p className="text-sm uppercase tracking-[0.24em] text-slate-500">⚠ Biggest Bottleneck</p>
      <p className="mt-4 text-2xl font-semibold text-white">{from} → {to}</p>
      <p className="mt-2 text-4xl font-bold text-rose-400">{percent}%</p>
      <p className="mt-3 text-sm leading-6 text-slate-400">{percent}% candidates are lost at this stage.</p>
      <div className="mt-4 rounded-2xl bg-slate-950/60 p-3">
        <p className="text-sm text-slate-400">Top reason:</p>
        <p className="mt-1 font-medium text-white">{reason}</p>
      </div>
    </div>
  );
}
