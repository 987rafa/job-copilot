import { Badge } from './ui/Badge'

export function ScoreBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return <Badge tone="slate">sin análisis</Badge>
  const tone = score >= 80 ? 'emerald' : score >= 60 ? 'amber' : 'rose'
  return <Badge tone={tone}>encaje {score} %</Badge>
}
