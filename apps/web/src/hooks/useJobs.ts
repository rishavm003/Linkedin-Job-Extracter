/**
 * React Query hooks for jobs API
 * Provides typed hooks for fetching job data
 */

import { useQuery, keepPreviousData } from "@tanstack/react-query"
import { 
  fetchJobs, 
  searchJobs, 
  fetchJobDetail, 
  fetchPortals, 
  fetchDomains, 
  fetchSkills 
} from "@/lib/api"
import type { JobFilters, JobSearchResponse } from "@/lib/types"

export function useJobs(filters: JobFilters = {}) {
  return useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => fetchJobs(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
    placeholderData: keepPreviousData, // no flicker on page change
  })
}

export function useJobSearch(
  params: { q: string; domain?: string; is_fresher?: boolean; is_remote?: boolean; limit?: number },
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ["jobs", "search", params],
    queryFn: () => searchJobs(params),
    enabled: enabled && params.q.length >= 2,
    staleTime: 60 * 1000,
  })
}

export function useJobDetail(id: string) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => fetchJobDetail(id),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  })
}

export function usePortals() {
  return useQuery({
    queryKey: ["portals"],
    queryFn: fetchPortals,
    staleTime: 10 * 60 * 1000,
  })
}

export function useDomains() {
  return useQuery({
    queryKey: ["domains"],
    queryFn: fetchDomains,
    staleTime: 10 * 60 * 1000,
  })
}

export function useSkills(limit: number = 50) {
  return useQuery({
    queryKey: ["skills", limit],
    queryFn: () => fetchSkills(limit),
    staleTime: 10 * 60 * 1000,
  })
}
