import KpiCard from '../../components/dashboard/KpiCard';
import FunnelChart from '../../components/dashboard/FunnelChart';
import BottleneckCard from '../../components/dashboard/BottleneckCard';
import ReasonChart from '../../components/dashboard/ReasonChart';
import FilterBar from '../../components/dashboard/FilterBar';
import DateRangePicker from '../../components/dashboard/DateRangePicker';
import PerformanceChart from '../../components/dashboard/PerformanceChart';
import { dashboardData } from '../../lib/mockData';

export default function DashboardPage() {
  const { kpis, funnel, bottlenecks, reasons, weeklyPerformance } = dashboardData;

  // compute drop-offs between consecutive funnel stages
  const dropOffs = funnel.slice(0, -1).map((step, i) => {
    const next = funnel[i + 1];
    const fromCount = step.count;
    const toCount = next.count;
    const lost = fromCount - toCount;
    const percent = fromCount > 0 ? +( (lost / fromCount) * 100 ).toFixed(1) : 0;
    return {
      from: step.stage,
      to: next.stage,
      fromCount,
      toCount,
      percent
    };
  });

  const biggest = dropOffs.reduce((acc, cur) => (cur.percent > (acc?.percent ?? -1) ? cur : acc), null) || null;
  // pick top reason from reasons mock
  const topReason = reasons && reasons.length ? reasons.reduce((a, b) => (a.value > b.value ? a : b)).reason : 'Unknown';

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-8">
        <header className="space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.32em] text-slate-500">HR recruitment intelligence</p>
              <h1 className="text-4xl font-semibold text-white">Recruitment intelligence dashboard</h1>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <DateRangePicker />
              <FilterBar />
            </div>
          </div>
          <p className="max-w-2xl text-slate-400">
            Monitor applications, funnel progression, hiring velocity, and candidate dropout reasons from a single view.
          </p>
        </header>

        <section className="grid gap-4 xl:grid-cols-4">
          {kpis.map((kpi) => (
            <KpiCard key={kpi.label} {...kpi} />
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[2fr_1fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <div className="mb-6 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-white">Recruitment funnel</h2>
                <p className="text-sm text-slate-400">Track candidate conversion across each pipeline stage.</p>
              </div>
            </div>
            <FunnelChart data={funnel.map((d) => ({ stage: d.stage, count: d.count }))} highlightStage={biggest?.from} />
          </div>

          <div className="space-y-6">
            {biggest ? (
              <BottleneckCard key={`${biggest.from}-${biggest.to}`} from={biggest.from} to={biggest.to} percent={biggest.percent} reason={topReason} />
            ) : (
              <BottleneckCard from="N/A" to="N/A" percent={0} reason="No data" />
            )}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[2fr_1fr]">
          <PerformanceChart data={weeklyPerformance} />
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Candidate feedback trends</h2>
            <div className="mt-6 space-y-4">
              <div className="rounded-3xl bg-slate-950/80 p-4">
                <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Top reason</p>
                <p className="mt-3 text-2xl font-semibold text-white">Salary expectations</p>
                <p className="mt-2 text-sm text-slate-400">More than 28% of declined offers cite salary mismatch.</p>
              </div>
              <div className="rounded-3xl bg-slate-950/80 p-4">
                <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Fastest growing issue</p>
                <p className="mt-3 text-2xl font-semibold text-white">Interview timing</p>
                <p className="mt-2 text-sm text-slate-400">Scheduling friction increased by 14% in the last month.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <h2 className="text-xl font-semibold text-white">Why candidates leave</h2>
            <ReasonChart data={reasons} />
          </div>
        </section>
      </div>
    </main>
  );
}
