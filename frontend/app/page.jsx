import LinkCard from '../components/ui/LinkCard';

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 px-6 py-16 text-center">
      <div className="max-w-2xl rounded-3xl border border-slate-700 bg-slate-900/80 p-12 shadow-xl shadow-slate-950/40 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.35em] text-slate-400">HR Recruitment Intelligence</p>
        <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl">Recruit Flow</h1>
        <p className="mt-4 text-slate-300">A lightweight hiring dashboard and data upload experience for HR teams.</p>
        <div className="mt-10 grid w-full gap-4 sm:grid-cols-2">
          <LinkCard href="/dashboard" label="Dashboard" />
          <LinkCard href="/upload" label="Upload Data" />
        </div>
      </div>
    </main>
  );
}
