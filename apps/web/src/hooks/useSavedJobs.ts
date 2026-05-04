/**
 * Hook for managing saved jobs in localStorage
 * Persists saved job IDs across sessions
 */

import { useState, useEffect } from "react"

const SAVED_JOBS_KEY = "jobextractor_saved_jobs"

export function useSavedJobs() {
  const [savedIds, setSavedIds] = useState<string[]>([])

  // Load saved jobs from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(SAVED_JOBS_KEY)
      if (stored) {
        setSavedIds(JSON.parse(stored))
      }
    } catch (error) {
      console.error("Failed to load saved jobs:", error)
    }
  }, [])

  // Save to localStorage whenever savedIds changes
  useEffect(() => {
    try {
      localStorage.setItem(SAVED_JOBS_KEY, JSON.stringify(savedIds))
    } catch (error) {
      console.error("Failed to save jobs:", error)
    }
  }, [savedIds])

  function saveJob(id: string): void {
    setSavedIds(prev => {
      if (!prev.includes(id)) {
        return [...prev, id]
      }
      return prev
    })
  }

  function unsaveJob(id: string): void {
    setSavedIds(prev => prev.filter(jobId => jobId !== id))
  }

  function isSaved(id: string): boolean {
    return savedIds.includes(id)
  }

  function toggleSave(id: string): void {
    if (isSaved(id)) {
      unsaveJob(id)
    } else {
      saveJob(id)
    }
  }

  function clearAll(): void {
    setSavedIds([])
  }

  return { 
    savedIds, 
    saveJob, 
    unsaveJob, 
    isSaved, 
    toggleSave, 
    clearAll 
  }
}
