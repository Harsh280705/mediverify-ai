export default function PageShell({ eyebrow, title, description, children }) {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-soft backdrop-blur">
        {eyebrow ? <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">{eyebrow}</p> : null}
        <div className="mt-2 space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">{title}</h1>
          {description ? <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">{description}</p> : null}
        </div>
        <div className="mt-8">{children}</div>
      </div>
    </div>
  );
}
