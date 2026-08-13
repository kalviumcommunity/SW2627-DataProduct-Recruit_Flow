export default function UploadDropzone() {
  return (
    <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-900/70 p-10 text-center text-slate-300">
      <p className="text-xl font-semibold text-white">Drag and drop files here</p>
      <p className="mt-3 text-sm text-slate-400">Upload CSVs or Excel files to refresh the hiring dataset.</p>
      <button className="mt-6 rounded-2xl bg-slate-700 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:bg-slate-600">
        Select file
      </button>
    </div>
  );
}
