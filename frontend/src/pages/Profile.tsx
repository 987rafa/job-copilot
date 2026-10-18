import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Upload } from 'lucide-react'
import { useRef, useState } from 'react'
import { PageHeader } from '../components/PageHeader'
import { ApiError, api } from '../lib/api'
import { dateTimeLabel } from '../lib/format'
import { inputClass, labelClass } from '../lib/styles'
import type { CvUploadResult, Profile as ProfileType } from '../lib/types'

const FIELDS = [
  ['full_name', 'Nombre completo'],
  ['headline', 'Titular (p. ej. Desarrollador Full Stack)'],
  ['email', 'Correo'],
  ['phone', 'Teléfono'],
  ['location', 'Ubicación'],
  ['links', 'Enlaces (GitHub · LinkedIn)'],
] as const

export function Profile() {
  const queryClient = useQueryClient()
  const profile = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get<ProfileType>('/profile'),
  })
  const [edited, setEdited] = useState<Partial<ProfileType> | null>(null)
  const [saved, setSaved] = useState(false)
  const [uploadMsg, setUploadMsg] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const form: ProfileType | null = profile.data ? { ...profile.data, ...edited } : null

  const set = (patch: Partial<ProfileType>) =>
    setEdited((prev) => ({ ...(prev ?? {}), ...patch }))

  const save = useMutation({
    mutationFn: () => {
      if (!form) throw new Error('Perfil sin cargar')
      return api.put<ProfileType>('/profile', {
        full_name: form.full_name,
        headline: form.headline,
        email: form.email,
        phone: form.phone,
        location: form.location,
        links: form.links,
        summary: form.summary,
        skills: form.skills,
        cv_text: form.cv_text,
      })
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data)
      setEdited(null)
      setSaved(true)
      window.setTimeout(() => setSaved(false), 2500)
      void queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })

  const upload = useMutation({
    mutationFn: (file: File) => api.upload<CvUploadResult>('/profile/cv', file),
    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data.profile)
      setEdited(null)
      setUploadMsg(`CV cargado: ${data.filename} (${data.chars.toLocaleString('es-CO')} caracteres)`)
      void queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: (error) => {
      setUploadMsg(error instanceof ApiError ? error.message : 'No se pudo subir el archivo')
    },
  })

  if (!form) {
    return <p className="text-sm text-slate-400">Cargando perfil…</p>
  }

  return (
    <>
      <PageHeader
        title="Mi CV"
        subtitle="Con estos datos la IA analiza ofertas y redacta tus borradores"
        actions={
          <button
            type="button"
            disabled={save.isPending}
            onClick={() => save.mutate()}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saved ? (
              <>
                <Check className="size-4" /> Guardado
              </>
            ) : save.isPending ? (
              'Guardando…'
            ) : (
              'Guardar cambios'
            )}
          </button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-700">Datos básicos</h2>
            <div className="mt-3 space-y-3">
              {FIELDS.map(([key, label]) => (
                <label key={key} className={labelClass}>
                  {label}
                  <input
                    value={form[key]}
                    onChange={(event) => set({ [key]: event.target.value } as Partial<ProfileType>)}
                    className={`mt-1 ${inputClass}`}
                  />
                </label>
              ))}
              <label className={labelClass}>
                Habilidades (separadas por comas)
                <textarea
                  value={form.skills}
                  onChange={(event) => set({ skills: event.target.value })}
                  rows={2}
                  className={`mt-1 ${inputClass}`}
                />
              </label>
              <label className={labelClass}>
                Resumen profesional
                <textarea
                  value={form.summary}
                  onChange={(event) => set({ summary: event.target.value })}
                  rows={4}
                  className={`mt-1 ${inputClass}`}
                />
              </label>
            </div>
          </div>
        </div>

        <div className="lg:col-span-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-sm font-bold text-slate-700">CV en texto</h2>
                <p className="text-xs text-slate-400">
                  Sube un PDF o .txt y la IA lo usa para analizar tu encaje.
                </p>
              </div>
              <div>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.txt,.md"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0]
                    if (file) upload.mutate(file)
                    event.target.value = ''
                  }}
                />
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  disabled={upload.isPending}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50"
                >
                  <Upload className="size-4" /> {upload.isPending ? 'Subiendo…' : 'Subir CV'}
                </button>
              </div>
            </div>
            {uploadMsg ? (
              <p className="mt-2 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">
                {uploadMsg}
              </p>
            ) : null}
            <textarea
              value={form.cv_text}
              onChange={(event) => set({ cv_text: event.target.value })}
              rows={18}
              placeholder="Pega aquí tu CV en texto plano…"
              className={`mt-3 font-mono ${inputClass}`}
            />
            {form.updated_at ? (
              <p className="mt-2 text-[11px] text-slate-400">
                Última actualización: {dateTimeLabel(form.updated_at)}
              </p>
            ) : null}
          </div>
        </div>
      </div>
    </>
  )
}
