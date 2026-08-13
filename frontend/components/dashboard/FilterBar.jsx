export default function FilterBar() {
  return (
    <div className="inline-flex items-center gap-3 rounded-3xl border border-slate-800 bg-slate-900/90 px-4 py-3 text-sm text-slate-300">
      <span className="font-medium text-slate-100">Filters</span>
      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">Region</span>
      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">Job Level</span>
    </div>
  );
}
