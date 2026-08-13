export default function UploadStatus() {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
      <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Upload status</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <div className="rounded-3xl bg-slate-950/80 p-4">
          <p className="text-3xl font-semibold text-white">1</p>
          <p className="mt-2 text-sm text-slate-400">Pending files</p>
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-4">
          <p className="text-3xl font-semibold text-white">0</p>
          <p className="mt-2 text-sm text-slate-400">Errors found</p>
        </div>
        <div className="rounded-3xl bg-slate-950/80 p-4">
          <p className="text-3xl font-semibold text-white">Ready</p>
          <p className="mt-2 text-sm text-slate-400">Status</p>
        </div>
      </div>
    </div>
  );
}
