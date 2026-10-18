import { useQuery } from '@tanstack/react-query'
import { Briefcase, CalendarClock, Send, Sparkles, Target } from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { PageHeader } from '../components/PageHeader'
import { ScoreBadge } from '../components/ScoreBadge'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { followupLabel } from '../lib/format'
import { STATUSES } from '../lib/status'
import type { DashboardData } from '../lib/types'

const STATUS_COLORS: Record<string, string> = {
  guardada: '#94a3b8',
  aplicada: '#6366f1',
  entrevista: '#8b5cf6',
  oferta: '#10b981',
  rechazada: '#fb7185',
}

export function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get<DashboardData>('/dashboard'),
  })

  if (isLoading || !data) {
    return <p className="text-sm text-slate-400">Cargando panel…</p>
  }

  const cards = [
    {
      label: 'Postulaciones',
      value: String(data.total),
      hint: `${data.active} activas`,
      icon: Briefcase,
      tone: 'bg-indigo-50 text-indigo-600',
    },
    {
      label: 'Aplicadas (7 días)',
      value: String(data.applied_this_week),
      hint: 'esta semana',
      icon: Send,
      tone: 'bg-violet-50 text-violet-600',
    },
    {
      label: 'Encaje medio',
      value: data.avg_fit === null ? '—' : `${Math.round(data.avg_fit)} %`,
      hint: 'de las ofertas analizadas',
      icon: Target,
      tone: 'bg-emerald-50 text-emerald-600',
    },
    {
      label: 'Seguimientos',
      value: String(data.upcoming_followups.length),
      hint: 'próximos 7 días',
      icon: CalendarClock,
      tone: 'bg-amber-50 text-amber-600',
    },
  ]

  const chartData = STATUSES.map((status) => ({
    name: status.plural,
    total: data.by_status[status.value] ?? 0,
    color: STATUS_COLORS[status.value] ?? '#94a3b8',
  }))

  return (
    <>
      <PageHeader
        title="Panel"
        subtitle="Tu búsqueda de empleo de un vistazo"
        actions={
          <Link
            to="/analizar"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500"
          >
            <Sparkles className="size-4" /> Analizar oferta
          </Link>
        }
      />

      {data.llm === 'heuristic' ? (
        <div className="mb-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          <span className="font-semibold">Motor local activo.</span> La app funciona sin claves de
          IA (análisis heurístico). Con{' '}
          <code className="rounded bg-amber-100 px-1">OPENAI_API_KEY</code> o{' '}
          <code className="rounded bg-amber-100 px-1">GEMINI_API_KEY</code> en el backend, el
          análisis y los borradores se generan con IA real.
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ label, value, hint, icon: Icon, tone }) => (
          <div key={label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <span className={`flex size-8 items-center justify-center rounded-lg ${tone}`}>
                <Icon className="size-4" />
              </span>
            </div>
            <p className="mt-2 text-3xl font-bold tracking-tight text-slate-800">{value}</p>
            <p className="mt-1 text-xs text-slate-400">{hint}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-5">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm xl:col-span-3">
          <h2 className="text-sm font-bold text-slate-700">Postulaciones por estado</h2>
          <div className="mt-4 h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: -18 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip cursor={{ fill: '#f1f5f9' }} />
                <Bar dataKey="total" name="Postulaciones" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6 xl:col-span-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-700">Próximos seguimientos</h2>
            <div className="mt-3 space-y-3">
              {data.upcoming_followups.length === 0 ? (
                <p className="text-xs text-slate-400">Sin seguimientos próximos.</p>
              ) : (
                data.upcoming_followups.map((item) => (
                  <div key={item.id} className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-700">{item.company}</p>
                      <p className="truncate text-xs text-slate-400">{item.role}</p>
                    </div>
                    <div className="shrink-0 text-right">
                      <p className="text-xs font-semibold text-amber-600">
                        {item.next_followup ? followupLabel(item.next_followup) : ''}
                      </p>
                      <StatusBadge status={item.status} />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-700">Recientes</h2>
            <div className="mt-3 space-y-3">
              {data.recent.length === 0 ? (
                <p className="text-xs text-slate-400">Nada por aquí todavía.</p>
              ) : (
                data.recent.map((item) => (
                  <div key={item.id} className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-700">{item.company}</p>
                      <p className="truncate text-xs text-slate-400">{item.role}</p>
                    </div>
                    <ScoreBadge score={item.fit_score} />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
