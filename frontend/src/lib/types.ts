export interface Analysis {
  fit_score: number
  summary: string
  strengths: string[]
  gaps: string[]
  keywords: string[]
}

export interface Application {
  id: number
  company: string
  role: string
  source: string
  url: string
  job_text: string
  status: string
  fit_score: number | null
  analysis: Analysis | null
  notes: string
  next_followup: string | null
  applied_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface ApplicationList {
  items: Application[]
  total: number
}

export interface Profile {
  id: number
  full_name: string
  headline: string
  email: string
  phone: string
  location: string
  links: string
  summary: string
  skills: string
  cv_text: string
  updated_at: string | null
}

export interface Draft {
  id: number
  application_id: number | null
  kind: string
  language: string
  tone: string
  content: string
  created_at: string | null
}

export interface DashboardData {
  total: number
  active: number
  by_status: Record<string, number>
  avg_fit: number | null
  applied_this_week: number
  upcoming_followups: Application[]
  recent: Application[]
  llm: string
}

export interface AnalyzeResponse {
  analysis: Analysis
  application_id: number | null
}

export interface CvUploadResult {
  filename: string
  chars: number
  profile: Profile
}

export interface Health {
  status: string
  app: string
  version: string
  llm: string
}
