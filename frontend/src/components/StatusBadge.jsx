export default function StatusBadge({ label, tone = 'slate' }) {
  const tones = {
    slate: 'bg-slate-700/70 text-slate-200',
    cyan: 'bg-cyan-400/15 text-cyan-200',
    emerald: 'bg-emerald-400/15 text-emerald-200',
    amber: 'bg-amber-400/15 text-amber-200',
  };

  return <span className={`rounded-full px-3 py-1 text-xs font-medium ${tones[tone] ?? tones.slate}`}>{label}</span>;
}
