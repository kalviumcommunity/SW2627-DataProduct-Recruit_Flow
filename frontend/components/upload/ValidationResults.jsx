export default function ValidationResults() {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
      <h2 className="text-lg font-semibold text-white">Validation preview</h2>
      <p className="mt-3 text-slate-400">No upload results yet. Drop a file to see validation details.</p>
      <div className="mt-6 grid gap-4 text-sm text-slate-300 sm:grid-cols-2">
        <div className="rounded-3xl bg-slate-950/80 p-4">
          <p className="font-medium text-white">Required fields</p>
          <p className="mt-2 text-slate-400">Name, Email, Role, Experience, Status</p>
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-4">
          <p className="font-medium text-white">Sample row</p>
          <p className="mt-2 text-slate-400">John Doe, john@example.com, Analyst, 3, Interviewing</p>
        </div>
      </div>
    </div>
  );
}
