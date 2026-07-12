export default function SectionCard({ title, children, footer }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-4">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>
      <div className="mt-4 text-sm leading-6 text-slate-300">{children}</div>
      {footer ? <div className="mt-5 border-t border-white/10 pt-4">{footer}</div> : null}
    </section>
  );
}
