import type { BadgeTone } from '../components/ui/Badge'

export interface StatusMeta {
  value: string
  plural: string
  singular: string
  tone: BadgeTone
}

export const STATUSES: StatusMeta[] = [
  { value: 'guardada', plural: 'Guardadas', singular: 'Guardada', tone: 'slate' },
  { value: 'aplicada', plural: 'Aplicadas', singular: 'Aplicada', tone: 'indigo' },
  { value: 'entrevista', plural: 'Entrevistas', singular: 'Entrevista', tone: 'violet' },
  { value: 'oferta', plural: 'Ofertas', singular: 'Oferta', tone: 'emerald' },
  { value: 'rechazada', plural: 'Rechazadas', singular: 'Rechazada', tone: 'rose' },
]

export function statusMeta(value: string): StatusMeta {
  return STATUSES.find((status) => status.value === value) ?? STATUSES[0]
}
