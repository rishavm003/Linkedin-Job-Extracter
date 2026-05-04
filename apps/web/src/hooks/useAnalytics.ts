/**
 * React Query hooks for analytics API
 * Provides typed hooks for fetching analytics data
 */

import { useQuery } from "@tanstack/react-query"
import { 
  fetchAnalyticsDashboard, 
  fetchTrendingSkills, 
  fetchSalaryRanges 
} from "@/lib/api"

export function useAnalyticsDashboard() {
  return useQuery({
    queryKey: ["analytics", "dashboard"],
    queryFn: fetchAnalyticsDashboard,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  })
}

export function useTrendingSkills() {
  return useQuery({
    queryKey: ["analytics", "trending"],
    queryFn: fetchTrendingSkills,
    staleTime: 5 * 60 * 1000,
  })
}

export function useSalaryRanges() {
  return useQuery({
    queryKey: ["analytics", "salary"],
    queryFn: fetchSalaryRanges,
    staleTime: 5 * 60 * 1000,
  })
}
