export function parseDateTime(iso: string): Date {
  const hasZone = /(Z|[+-]\d{2}:?\d{2})$/.test(iso)
  return new Date(hasZone ? iso : `${iso}Z`)
}

export function dateTimeLabel(iso: string): string {
  return parseDateTime(iso).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' })
}

/** Fecha local (YYYY-MM-DD) sin desfases de zona horaria. */
function localDate(value: string): Date {
  const [y, m, d] = value.slice(0, 10).split('-').map(Number)
  return new Date(y ?? 1970, (m ?? 1) - 1, d ?? 1)
}

export function dateLabel(value: string): string {
  return localDate(value).toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })
}

export function followupLabel(value: string): string {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = localDate(value)
  const days = Math.round((target.getTime() - today.getTime()) / 86_400_000)
  if (days < 0) return `Vencido · ${dateLabel(value)}`
  if (days === 0) return 'Hoy'
  if (days === 1) return 'Mañana'
  return `En ${days} días · ${dateLabel(value)}`
}
