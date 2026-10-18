import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Copy, ExternalLink, Plus, Search, Trash2, X } from 'lucide-react'
import { useState } from 'react'
import { PageHeader } from '../components/PageHeader'
import { ScoreBadge } from '../components/ScoreBadge'
import { StatusBadge } from '../components/StatusBadge'
import { Badge } from '../components/ui/Badge'
import { Modal } from '../components/ui/Modal'
import { api } from '../lib/api'
import { dateTimeLabel, followupLabel } from '../lib/format'
import { STATUSES } from '../lib/status'
import { inputClass, labelClass } from '../lib/styles'
import type { Application, ApplicationList, Draft } from '../lib/types'

const emptyNew = { company: '', role: '', source: '', url: '', job_text: '', notes: '' }

export function Applications() {
  const queryClient = useQueryClient()
  const [q, setQ] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [showNew, setShowNew] = useState(false)
  const [newForm, setNewForm] = useState(emptyNew)
  const [notesDraft, setNotesDraft] = useState('')
  const [copiedId, setCopiedId] = useState<number | null>(null)

  const applications = useQuery({
    queryKey: ['applications', q],
    queryFn: () =>
      api.get<ApplicationList>(
        `/applications${q.trim() ? `?q=${encodeURIComponent(q.trim())}` : ''}`,
      ),
  })
  const items = applications.data?.items ?? []
  const selected = selectedId === null ? null : (items.find((item) => item.id === selectedId) ?? null)

  const drafts = useQuery({
    queryKey: ['drafts', 'application', selectedId],
    queryFn: () => api.get<Draft[]>(`/ai/drafts?application_id=${selectedId}`),
    enabled: selectedId !== null,
  })

  const refreshLists = () => {
    void queryClient.invalidateQueries({ queryKey: ['applications'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Record<string, unknown> }) =>
      api.patch<Application>(`/applications/${id}`, payload),
    onSuccess: refreshLists,
  })

  const remove = useMutation({
    mutationFn: (id: number) => api.delete<void>(`/applications/${id}`),
    onSuccess: () => {
      setSelectedId(null)
      refreshLists()
    },
  })

  const create = useMutation({
    mutationFn: () => api.post<Application>('/applications', newForm),
    onSuccess: (data) => {
      setShowNew(false)
      setNewForm(emptyNew)
      setSelectedId(data.id)
      refreshLists()
    },
  })

  const generateDraft = useMutation({
    mutationFn: (id: number) =>
      api.post<Draft>('/ai/drafts', { application_id: id, kind: 'carta', language: 'es' }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['drafts'] }),
  })

  const openApp = (item: Application) => {
    setSelectedId(item.id)
    setNotesDraft(item.notes)
  }

  const copy = async (id: number, content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedId(id)
      window.setTimeout(() => setCopiedId(null), 2000)
    } catch {
      /* portapapeles no disponible */
    }
  }

  return (
    <>
      <PageHeader
        title="Postulaciones"
        subtitle={`${items.length} en el tablero`}
        actions={
          <>
            <div className="relative">
              <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-slate-400" />
              <input
                value={q}
                onChange={(event) => setQ(event.target.value)}
                placeholder="Buscar empresa o cargo…"
                className="w-56 rounded-lg border border-slate-300 bg-white py-2 pr-3 pl-8 text-sm placeholder:text-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
              />
            </div>
            <button
              type="button"
              onClick={() => setShowNew(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500"
            >
              <Plus className="size-4" /> Nueva
            </button>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {STATUSES.map((status) => {
          const columnItems = items.filter((item) => item.status === status.value)
          return (
            <section key={status.value} className="rounded-2xl bg-slate-200/70 p-3">
              <header className="mb-3 flex items-center justify-between px-1">
                <h2 className="text-xs font-bold tracking-wide text-slate-500 uppercase">
                  {status.plural}
                </h2>
                <span className="rounded-full bg-white px-2 py-0.5 text-xs font-semibold text-slate-500">
                  {columnItems.length}
                </span>
              </header>
              <div className="space-y-2">
                {columnItems.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => openApp(item)}
                    className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left shadow-sm transition hover:border-indigo-300 hover:shadow"
                  >
                    <p className="text-sm font-semibold text-slate-800">{item.company}</p>
                    <p className="mt-0.5 line-clamp-2 text-xs text-slate-500">{item.role}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-1.5">
                      <ScoreBadge score={item.fit_score} />
                      {item.source ? (
                        <span className="text-[11px] text-slate-400">{item.source}</span>
                      ) : null}
                    </div>
                    {item.next_followup ? (
                      <p className="mt-2 text-[11px] font-medium text-amber-600">
                        {followupLabel(item.next_followup)}
                      </p>
                    ) : null}
                  </button>
                ))}
                {columnItems.length === 0 ? (
                  <p className="px-1 py-4 text-center text-xs text-slate-400">Vacío</p>
                ) : null}
              </div>
            </section>
          )
        })}
      </div>

      {selected ? (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/50" onClick={() => setSelectedId(null)} />
          <aside className="relative flex h-full w-full max-w-xl flex-col overflow-y-auto bg-white shadow-2xl">
            <div className="sticky top-0 z-10 flex items-start justify-between gap-3 border-b border-slate-100 bg-white px-6 py-4">
              <div className="min-w-0">
                <h2 className="truncate text-lg font-bold text-slate-800">{selected.company}</h2>
                <p className="truncate text-sm text-slate-500">{selected.role}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedId(null)}
                className="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                aria-label="Cerrar"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="space-y-5 px-6 py-5">
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge status={selected.status} />
                <ScoreBadge score={selected.fit_score} />
                {selected.source ? <Badge>{selected.source}</Badge> : null}
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <label className={labelClass}>
                  Estado
                  <select
                    value={selected.status}
                    onChange={(event) =>
                      update.mutate({ id: selected.id, payload: { status: event.target.value } })
                    }
                    className={`mt-1 ${inputClass}`}
                  >
                    {STATUSES.map((status) => (
                      <option key={status.value} value={status.value}>
                        {status.singular}
                      </option>
                    ))}
                  </select>
                </label>
                <label className={labelClass}>
                  Próximo seguimiento
                  <input
                    type="date"
                    value={selected.next_followup ?? ''}
                    onChange={(event) =>
                      update.mutate({
                        id: selected.id,
                        payload: { next_followup: event.target.value || null },
                      })
                    }
                    className={`mt-1 ${inputClass}`}
                  />
                </label>
              </div>

              <div className="grid gap-1 text-xs text-slate-400 sm:grid-cols-2">
                {selected.applied_at ? <p>Aplicada: {dateTimeLabel(selected.applied_at)}</p> : null}
                {selected.created_at ? <p>Creada: {dateTimeLabel(selected.created_at)}</p> : null}
                {selected.url ? (
                  <a
                    href={selected.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-medium text-indigo-600 hover:underline"
                  >
                    Ver oferta original <ExternalLink className="size-3" />
                  </a>
                ) : null}
              </div>

              <div>
                <label className={labelClass}>Notas</label>
                <textarea
                  value={notesDraft}
                  onChange={(event) => setNotesDraft(event.target.value)}
                  rows={3}
                  placeholder="Entrevistas, contactos, próximos pasos…"
                  className={`mt-1 ${inputClass}`}
                />
                <button
                  type="button"
                  disabled={notesDraft === selected.notes || update.isPending}
                  onClick={() => update.mutate({ id: selected.id, payload: { notes: notesDraft } })}
                  className="mt-2 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Guardar notas
                </button>
              </div>

              {selected.analysis ? (
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold tracking-wide text-slate-500 uppercase">
                      Análisis IA
                    </h3>
                    <span className="text-lg font-bold text-indigo-600">
                      {selected.analysis.fit_score}
                      <span className="text-xs text-slate-400">/100</span>
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-600">{selected.analysis.summary}</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div>
                      <p className="text-[11px] font-bold text-emerald-600 uppercase">Fortalezas</p>
                      <ul className="mt-1 space-y-0.5">
                        {selected.analysis.strengths.map((item) => (
                          <li key={item} className="text-xs text-slate-600">
                            + {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-[11px] font-bold text-amber-600 uppercase">A reforzar</p>
                      <ul className="mt-1 space-y-0.5">
                        {selected.analysis.gaps.map((item) => (
                          <li key={item} className="text-xs text-slate-600">
                            − {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {selected.analysis.keywords.map((item) => (
                      <Badge key={item}>{item}</Badge>
                    ))}
                  </div>
                </div>
              ) : null}

              {selected.job_text ? (
                <details className="rounded-xl border border-slate-200 p-3">
                  <summary className="cursor-pointer text-xs font-semibold text-slate-500">
                    Ver oferta guardada
                  </summary>
                  <pre className="mt-2 max-h-48 overflow-auto text-xs whitespace-pre-wrap text-slate-600">
                    {selected.job_text}
                  </pre>
                </details>
              ) : null}

              <div>
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold tracking-wide text-slate-500 uppercase">
                    Borradores
                  </h3>
                  <button
                    type="button"
                    disabled={generateDraft.isPending}
                    onClick={() => generateDraft.mutate(selected.id)}
                    className="rounded-lg border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 transition hover:bg-indigo-100 disabled:opacity-50"
                  >
                    {generateDraft.isPending ? 'Generando…' : 'Generar carta (ES)'}
                  </button>
                </div>
                <div className="mt-2 space-y-2">
                  {(drafts.data ?? []).map((item) => (
                    <div key={item.id} className="rounded-xl border border-slate-100 bg-slate-50 p-3">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-1.5">
                          <Badge tone="indigo">{item.kind}</Badge>
                          <Badge>{item.language}</Badge>
                          {item.created_at ? (
                            <span className="text-[11px] text-slate-400">
                              {dateTimeLabel(item.created_at)}
                            </span>
                          ) : null}
                        </div>
                        <button
                          type="button"
                          onClick={() => copy(item.id, item.content)}
                          className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white hover:text-slate-700"
                          title="Copiar"
                        >
                          {copiedId === item.id ? (
                            <Check className="size-3.5 text-emerald-500" />
                          ) : (
                            <Copy className="size-3.5" />
                          )}
                        </button>
                      </div>
                      <pre className="mt-2 max-h-40 overflow-auto text-xs whitespace-pre-wrap text-slate-600">
                        {item.content}
                      </pre>
                    </div>
                  ))}
                  {drafts.data && drafts.data.length === 0 ? (
                    <p className="text-xs text-slate-400">Sin borradores todavía.</p>
                  ) : null}
                </div>
              </div>

              <div className="border-t border-slate-100 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm(`¿Eliminar la postulación de ${selected.company}?`)) {
                      remove.mutate(selected.id)
                    }
                  }}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-600 transition hover:text-rose-700"
                >
                  <Trash2 className="size-3.5" /> Eliminar postulación
                </button>
              </div>
            </div>
          </aside>
        </div>
      ) : null}

      {showNew ? (
        <Modal title="Nueva postulación" onClose={() => setShowNew(false)}>
          <div className="space-y-3">
            <input
              value={newForm.company}
              onChange={(event) => setNewForm({ ...newForm, company: event.target.value })}
              placeholder="Empresa *"
              className={inputClass}
            />
            <input
              value={newForm.role}
              onChange={(event) => setNewForm({ ...newForm, role: event.target.value })}
              placeholder="Cargo *"
              className={inputClass}
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                value={newForm.source}
                onChange={(event) => setNewForm({ ...newForm, source: event.target.value })}
                placeholder="Fuente"
                className={inputClass}
              />
              <input
                value={newForm.url}
                onChange={(event) => setNewForm({ ...newForm, url: event.target.value })}
                placeholder="Enlace"
                className={inputClass}
              />
            </div>
            <textarea
              value={newForm.job_text}
              onChange={(event) => setNewForm({ ...newForm, job_text: event.target.value })}
              rows={5}
              placeholder="Texto de la oferta (opcional, sirve para analizarla y generar borradores)"
              className={inputClass}
            />
            <textarea
              value={newForm.notes}
              onChange={(event) => setNewForm({ ...newForm, notes: event.target.value })}
              rows={2}
              placeholder="Notas"
              className={inputClass}
            />
            <div className="flex justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setShowNew(false)}
                className="rounded-lg px-3.5 py-2 text-sm font-semibold text-slate-500 transition hover:bg-slate-100"
              >
                Cancelar
              </button>
              <button
                type="button"
                disabled={create.isPending || !newForm.company.trim() || !newForm.role.trim()}
                onClick={() => create.mutate()}
                className="rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {create.isPending ? 'Guardando…' : 'Guardar postulación'}
              </button>
            </div>
          </div>
        </Modal>
      ) : null}
    </>
  )
}
