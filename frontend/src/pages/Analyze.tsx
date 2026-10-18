import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Copy, FileText, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { PageHeader } from '../components/PageHeader'
import { Badge } from '../components/ui/Badge'
import { ApiError, api } from '../lib/api'
import { dateTimeLabel } from '../lib/format'
import { inputClass } from '../lib/styles'
import type { AnalyzeResponse, Draft } from '../lib/types'

const KIND_OPTIONS = [
  { value: 'carta', label: 'Carta de presentación' },
  { value: 'mensaje', label: 'Mensaje corto' },
  { value: 'seguimiento', label: 'Seguimiento' },
]

export function Analyze() {
  const queryClient = useQueryClient()
  const [jobText, setJobText] = useState('')
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [source, setSource] = useState('')
  const [url, setUrl] = useState('')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [kind, setKind] = useState('carta')
  const [language, setLanguage] = useState('es')
  const [tone, setTone] = useState('profesional')
  const [extraNotes, setExtraNotes] = useState('')
  const [draft, setDraft] = useState<Draft | null>(null)
  const [copiedId, setCopiedId] = useState<number | null>(null)

  const recentDrafts = useQuery({
    queryKey: ['drafts', 'recent'],
    queryFn: () => api.get<Draft[]>('/ai/drafts?limit=5'),
  })

  const analyze = useMutation({
    mutationFn: (save: boolean) =>
      api.post<AnalyzeResponse>('/ai/analyze', {
        job_text: jobText,
        company,
        role,
        source,
        url,
        save,
      }),
    onSuccess: (data) => {
      setResult(data)
      if (data.application_id) {
        void queryClient.invalidateQueries({ queryKey: ['applications'] })
        void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      }
    },
  })

  const generate = useMutation({
    mutationFn: () =>
      api.post<Draft>('/ai/drafts', {
        application_id: result?.application_id ?? null,
        job_text: jobText,
        kind,
        language,
        tone,
        extra_notes: extraNotes,
      }),
    onSuccess: (data) => {
      setDraft(data)
      void queryClient.invalidateQueries({ queryKey: ['drafts'] })
    },
  })

  const copy = async (id: number, content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedId(id)
      window.setTimeout(() => setCopiedId(null), 2000)
    } catch {
      /* portapapeles no disponible */
    }
  }

  const canAnalyze = jobText.trim().length >= 30
  const canSave = canAnalyze && company.trim().length > 0 && role.trim().length > 0
  const error = analyze.error ?? generate.error
  const errorMessage =
    error instanceof ApiError ? error.message : error ? 'Ocurrió un error inesperado' : null

  return (
    <>
      <PageHeader
        title="Analizar oferta"
        subtitle="Pega una oferta y obtén encaje, fortalezas, brechas y un borrador listo para enviar"
      />

      {errorMessage ? (
        <div className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {errorMessage}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-4 lg:col-span-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-700">Oferta de trabajo</h2>
            <textarea
              value={jobText}
              onChange={(event) => setJobText(event.target.value)}
              rows={10}
              placeholder="Pega aquí el texto completo de la oferta (responsabilidades, requisitos…)"
              className={`mt-3 ${inputClass}`}
            />
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <input
                value={company}
                onChange={(event) => setCompany(event.target.value)}
                placeholder="Empresa"
                className={inputClass}
              />
              <input
                value={role}
                onChange={(event) => setRole(event.target.value)}
                placeholder="Cargo"
                className={inputClass}
              />
              <input
                value={source}
                onChange={(event) => setSource(event.target.value)}
                placeholder="Fuente (LinkedIn, portal…)"
                className={inputClass}
              />
              <input
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="Enlace (opcional)"
                className={inputClass}
              />
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                disabled={!canAnalyze || analyze.isPending}
                onClick={() => analyze.mutate(false)}
                className="inline-flex items-center gap-2 rounded-lg border border-indigo-200 bg-indigo-50 px-3.5 py-2 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Sparkles className="size-4" />
                {analyze.isPending ? 'Analizando…' : 'Analizar'}
              </button>
              <button
                type="button"
                disabled={!canSave || analyze.isPending}
                onClick={() => analyze.mutate(true)}
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <FileText className="size-4" /> Analizar y guardar
              </button>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              «Guardar» añade la oferta al tablero de postulaciones con su análisis.
            </p>
          </div>

          {recentDrafts.data && recentDrafts.data.length > 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-sm font-bold text-slate-700">Borradores recientes</h2>
              <div className="mt-3 space-y-3">
                {recentDrafts.data.map((item) => (
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
                    <p className="mt-2 line-clamp-3 text-xs whitespace-pre-wrap text-slate-500">
                      {item.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        <div className="space-y-4 lg:col-span-3">
          {result === null ? (
            <div className="flex h-full min-h-64 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/60 p-8 text-center">
              <Sparkles className="size-8 text-indigo-300" />
              <p className="mt-3 text-sm font-medium text-slate-500">El análisis aparecerá aquí</p>
              <p className="mt-1 max-w-sm text-xs text-slate-400">
                Encaje con tu perfil, fortalezas, brechas y palabras clave. Después podrás generar
                una carta o mensaje listo para copiar.
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="text-sm font-bold text-slate-700">Resultado del análisis</h2>
                  <div className="text-right">
                    <p className="text-2xl leading-none font-bold text-indigo-600">
                      {result.analysis.fit_score}
                      <span className="text-sm text-slate-400">/100</span>
                    </p>
                    <p className="text-[11px] text-slate-400">encaje</p>
                  </div>
                </div>
                <p className="mt-3 text-sm text-slate-600">{result.analysis.summary}</p>

                {result.application_id ? (
                  <div className="mt-3 flex items-center justify-between rounded-xl bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                    <span>Guardada en tus postulaciones.</span>
                    <Link to="/postulaciones" className="font-semibold underline">
                      Ver en el tablero
                    </Link>
                  </div>
                ) : null}

                <div className="mt-4 grid gap-4 sm:grid-cols-3">
                  <div>
                    <h3 className="text-xs font-bold tracking-wide text-emerald-600 uppercase">
                      Fortalezas
                    </h3>
                    <ul className="mt-2 space-y-1">
                      {result.analysis.strengths.map((item) => (
                        <li key={item} className="text-xs text-slate-600">
                          + {item}
                        </li>
                      ))}
                      {result.analysis.strengths.length === 0 ? (
                        <li className="text-xs text-slate-400">—</li>
                      ) : null}
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-xs font-bold tracking-wide text-amber-600 uppercase">
                      A reforzar
                    </h3>
                    <ul className="mt-2 space-y-1">
                      {result.analysis.gaps.map((item) => (
                        <li key={item} className="text-xs text-slate-600">
                          − {item}
                        </li>
                      ))}
                      {result.analysis.gaps.length === 0 ? (
                        <li className="text-xs text-slate-400">—</li>
                      ) : null}
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-xs font-bold tracking-wide text-slate-500 uppercase">
                      Palabras clave
                    </h3>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {result.analysis.keywords.map((item) => (
                        <Badge key={item}>{item}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-700">Borrador listo para enviar</h2>
                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                  <select
                    value={kind}
                    onChange={(event) => setKind(event.target.value)}
                    className={inputClass}
                  >
                    {KIND_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <select
                    value={language}
                    onChange={(event) => setLanguage(event.target.value)}
                    className={inputClass}
                  >
                    <option value="es">Español</option>
                    <option value="en">Inglés</option>
                  </select>
                  <select
                    value={tone}
                    onChange={(event) => setTone(event.target.value)}
                    className={inputClass}
                  >
                    <option value="profesional">Tono profesional</option>
                    <option value="cercano">Tono cercano</option>
                    <option value="entusiasta">Tono entusiasta</option>
                    <option value="directo">Tono directo</option>
                  </select>
                </div>
                <input
                  value={extraNotes}
                  onChange={(event) => setExtraNotes(event.target.value)}
                  placeholder="Notas para la IA (opcional): disponibilidad, salario, un logro…"
                  className={`mt-2 ${inputClass}`}
                />
                <button
                  type="button"
                  disabled={generate.isPending}
                  onClick={() => generate.mutate()}
                  className="mt-3 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-3.5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Sparkles className="size-4" />
                  {generate.isPending ? 'Generando…' : 'Generar borrador'}
                </button>

                {draft ? (
                  <div className="mt-4">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-semibold text-slate-500">Borrador generado</p>
                      <button
                        type="button"
                        onClick={() => copy(draft.id, draft.content)}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-500 transition hover:bg-slate-50 hover:text-slate-700"
                      >
                        {copiedId === draft.id ? (
                          <>
                            <Check className="size-3.5 text-emerald-500" /> Copiado
                          </>
                        ) : (
                          <>
                            <Copy className="size-3.5" /> Copiar
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="mt-2 max-h-80 overflow-auto rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm whitespace-pre-wrap text-slate-700">
                      {draft.content}
                    </pre>
                  </div>
                ) : null}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
