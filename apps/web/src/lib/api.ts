/**
 * API client functions for JobExtractor backend
 * All functions are typed and throw on non-2xx responses
 */

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

import type {
  JobListResponse, JobSearchResponse, JobDetail, PortalInfo, DomainInfo,
  SkillInfo, AnalyticsDashboard, TrendingSkill, SalaryRange,
  JobFilters, HealthResponse,
  AIStatus, AIQueryResponse, AISuggestion, JobSummary
} from './types'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export async function fetchJobs(filters: JobFilters = {}): Promise<JobListResponse> {
  const params = new URLSearchParams()
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      if (key === "skills" && Array.isArray(value)) {
        params.append(key, value.join(","))
      } else if (typeof value === "boolean") {
        params.append(key, value.toString())
      } else {
        params.append(key, String(value))
      }
    }
  })
  
  const queryString = params.toString()
  const response = await fetch(`${BASE}/api/jobs?${queryString}`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<JobListResponse>(response)
}

export async function searchJobs(params: {
  q: string
  domain?: string
  is_fresher?: boolean
  is_remote?: boolean
  limit?: number
}): Promise<JobSearchResponse> {
  const searchParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, String(value))
    }
  })
  
  const response = await fetch(`${BASE}/api/jobs/search?${searchParams.toString()}`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<JobSearchResponse>(response)
}

export async function fetchJobDetail(id: string): Promise<JobDetail> {
  const response = await fetch(`${BASE}/api/jobs/${id}`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<JobDetail>(response)
}

export async function fetchPortals(): Promise<PortalInfo[]> {
  const response = await fetch(`${BASE}/api/jobs/portals`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<PortalInfo[]>(response)
}

export async function fetchDomains(): Promise<DomainInfo[]> {
  const response = await fetch(`${BASE}/api/jobs/domains`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<DomainInfo[]>(response)
}

export async function fetchSkills(limit: number = 50): Promise<SkillInfo[]> {
  const response = await fetch(`${BASE}/api/jobs/skills?limit=${limit}`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<SkillInfo[]>(response)
}

export async function fetchAnalyticsDashboard(): Promise<AnalyticsDashboard> {
  const response = await fetch(`${BASE}/api/analytics/dashboard`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<AnalyticsDashboard>(response)
}

export async function fetchTrendingSkills(): Promise<TrendingSkill[]> {
  const response = await fetch(`${BASE}/api/analytics/trending-skills`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<TrendingSkill[]>(response)
}

export async function fetchSalaryRanges(): Promise<SalaryRange[]> {
  const response = await fetch(`${BASE}/api/analytics/salary-ranges`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<SalaryRange[]>(response)
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${BASE}/api/health`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<HealthResponse>(response)
}

// AI Assistant API functions

export async function fetchAIStatus(): Promise<AIStatus> {
  const response = await fetch(`${BASE}/api/ai/status`, {
    headers: { "Content-Type": "application/json" }
  })
  
  return handleResponse<AIStatus>(response)
}

export async function fetchAISuggestions(params?: {
  domain?: string
  seniority?: string
}): Promise<AISuggestion> {
  const response = await fetch(`${BASE}/api/ai/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params || {})
  })
  
  return handleResponse<AISuggestion>(response)
}

export async function queryAI(
  question: string,
  onToken: (token: string) => void,
  onJobs: (jobs: JobSummary[], total: number) => void,
  onDone: (meta: { ai_used: boolean, fallback: boolean }) => void,
  onError: (message: string) => void,
): Promise<void> {
  try {
    const response = await fetch(`${BASE}/api/ai/query`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
      },
      body: JSON.stringify({ question, stream: true })
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error("No response body")
    }

    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      
      // Process complete SSE events
      const events = buffer.split("\n\n")
      buffer = events.pop() || "" // Keep incomplete event in buffer

      for (const event of events) {
        const lines = event.split("\n")
        let eventName = ""
        let eventData = ""

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventName = line.slice(7)
          } else if (line.startsWith("data: ")) {
            eventData = line.slice(6)
          }
        }

        if (eventName && eventData) {
          try {
            const data = JSON.parse(eventData)
            
            switch (eventName) {
              case "jobs":
                onJobs(data.jobs || [], data.total_found || 0)
                break
              case "token":
                onToken(data.text || "")
                break
              case "done":
                onDone({ ai_used: data.ai_used, fallback: data.fallback })
                break
              case "error":
                onError(data.message || "Unknown error")
                break
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", e)
          }
        }
      }
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Network error"
    onError(message)
  }
}
