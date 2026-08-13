export default function DateRangePicker() {
  return (
    <div className="inline-flex items-center gap-3 rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-sm text-slate-300">
      <span className="text-slate-400">Date range</span>
      <select className="rounded-2xl border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-slate-500">
        <option>Last 7 days</option>
        <option>Last 30 days</option>
        <option>Last 90 days</option>
      </select>
    </div>
  );
}
