import UploadDropzone from '../../components/upload/UploadDropzone';
import UploadStatus from '../../components/upload/UploadStatus';
import ValidationResults from '../../components/upload/ValidationResults';

export default function UploadPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <header className="space-y-3">
          <p className="text-sm uppercase tracking-[0.32em] text-slate-500">HR recruitment intelligence</p>
          <h1 className="text-4xl font-semibold text-white">Upload Data</h1>
          <p className="max-w-2xl text-slate-400">Upload candidate and hiring data to see insights faster.</p>
        </header>

        <UploadDropzone />
        <UploadStatus />
        <ValidationResults />
      </div>
    </main>
  );
}
