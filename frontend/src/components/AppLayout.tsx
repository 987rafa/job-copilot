import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Briefcase, LayoutDashboard, Menu, RefreshCw, Sparkles, UserRound, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { api } from '../lib/api'
import type { Health } from '../lib/types'
import { Badge } from './ui/Badge'

const navItems = [
  { to: '/', label: 'Panel', icon: LayoutDashboard, end: true },
  { to: '/analizar', label: 'Analizar oferta', icon: Sparkles, end: false },
  { to: '/postulaciones', label: 'Postulaciones', icon: Briefcase, end: false },
  { to: '/perfil', label: 'Mi CV', icon: UserRound, end: false },
]

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [resetting, setResetting] = useState(false)
  const queryClient = useQueryClient()

  const health = useQuery({
    queryKey: ['health'],
    queryFn: () => api.get<Health>('/health'),
  })
  const llm = health.data?.llm ?? 'heuristic'
  const llmLabel = llm === 'heuristic' ? 'Motor local' : `IA · ${llm}`

  const resetDemo = async () => {
    if (!window.confirm('¿Restaurar los datos de ejemplo? Se reemplazan postulaciones y borradores.')) {
      return
    }
    setResetting(true)
    try {
      await api.post('/demo/reset')
      await queryClient.invalidateQueries()
    } finally {
      setResetting(false)
    }
  }

  const sidebar = (
    <div className="flex h-full flex-col bg-slate-900 text-slate-300">
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600">
          <Sparkles className="size-4.5 text-white" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-bold tracking-wide text-white">Job Copilot</p>
          <p className="text-[11px] text-slate-500">Copiloto de postulaciones</p>
        </div>
        <button
          type="button"
          className="ml-auto rounded-lg p-1 text-slate-500 hover:text-white lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Cerrar menú"
        >
          <X className="size-4" />
        </button>
      </div>

      <nav className="mt-2 flex-1 space-y-1 px-3">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive
                  ? 'bg-indigo-600/90 text-white shadow-sm'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <Icon className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="space-y-3 border-t border-slate-800 p-4">
        <div className="flex items-center justify-between">
          <Badge tone={llm === 'heuristic' ? 'amber' : 'emerald'}>{llmLabel}</Badge>
          <button
            type="button"
            onClick={resetDemo}
            disabled={resetting}
            className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium text-slate-400 transition hover:bg-slate-800 hover:text-white disabled:opacity-50"
            title="Restaurar datos demo"
          >
            <RefreshCw className={`size-3.5 ${resetting ? 'animate-spin' : ''}`} />
            Datos demo
          </button>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-600">
          {llm === 'heuristic'
            ? 'Sin clave de IA: análisis heurístico local. Configura OPENAI_API_KEY o GEMINI_API_KEY en el backend.'
            : 'Análisis y redacción con IA activados.'}
        </p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-100">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 lg:block">{sidebar}</aside>

      {sidebarOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-slate-900/60" onClick={() => setSidebarOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-64">{sidebar}</aside>
        </div>
      ) : null}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur lg:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
            aria-label="Abrir menú"
          >
            <Menu className="size-5" />
          </button>
          <span className="text-sm font-bold text-slate-800">Job Copilot</span>
        </header>

        <main className="mx-auto max-w-7xl p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
