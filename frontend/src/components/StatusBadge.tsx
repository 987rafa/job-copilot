import { statusMeta } from '../lib/status'
import { Badge } from './ui/Badge'

export function StatusBadge({ status }: { status: string }) {
  const meta = statusMeta(status)
  return <Badge tone={meta.tone}>{meta.singular}</Badge>
}
