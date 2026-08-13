import Link from 'next/link';

export default function LinkCard({ href, label }) {
  return (
    <Link
      href={href}
      className="block rounded-3xl border border-slate-700 bg-slate-900/90 px-6 py-8 text-left transition hover:border-slate-500 hover:bg-slate-800"
    >
      <p className="text-2xl font-semibold text-white">{label}</p>
      <p className="mt-2 text-sm text-slate-400">View the {label.toLowerCase()} page.</p>
    </Link>
  );
}
