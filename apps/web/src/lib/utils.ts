/**
 * Utility functions for JobExtractor frontend
 */

import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { formatDistanceToNow, parseISO, format } from "date-fns"
import type { Salary, JobFilters } from "./types"

export const MAX_SKILLS_DISPLAY = 5

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatSalary(salary: Salary): string {
  if (!salary.is_disclosed) {
    return "Salary not disclosed"
  }
  
  if (salary.raw && salary.min_value === null) {
    return salary.raw
  }
  
  if (!salary.min_value || !salary.max_value) {
    return salary.raw || "Not disclosed"
  }
  
  const { min_value, max_value, currency } = salary
  
  if (currency === "INR") {
    // Convert to LPA (Lakhs Per Annum)
    const minLPA = Math.round(min_value / 100000)
    const maxLPA = Math.round(max_value / 100000)
    return `₹${minLPA}–${maxLPA} LPA`
  }
  
  if (currency === "USD") {
    // Convert to thousands
    const minK = Math.round(min_value / 1000)
    const maxK = Math.round(max_value / 1000)
    return `$${minK}k–$${maxK}k/yr`
  }
  
  return salary.raw || "Not disclosed"
}

export function formatRelativeDate(dateStr: string | null): string {
  if (!dateStr) return "Recently"
  
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true })
  } catch {
    return "Recently"
  }
}

export function formatAbsoluteDate(dateStr: string | null): string {
  if (!dateStr) return "—"
  
  try {
    return format(parseISO(dateStr), "dd MMM yyyy")
  } catch {
    return "—"
  }
}

export function truncateSkills(skills: string[], max: number = 5): {
  visible: string[]
  overflow: number
} {
  if (skills.length <= max) {
    return { visible: skills, overflow: 0 }
  }
  
  return {
    visible: skills.slice(0, max),
    overflow: skills.length - max
  }
}

import { DOMAIN_COLORS, PORTAL_COLORS } from "./constants"

export function domainColor(domain: string): string {
  return DOMAIN_COLORS[domain] || DOMAIN_COLORS["Other"]
}

export function portalColor(portal: string): string {
  return PORTAL_COLORS[portal] || "#888780"
}

export function buildQueryString(filters: JobFilters): string {
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
  
  return params.toString()
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}

export function getGreeting(): string {
  const hour = new Date().getHours()
  
  if (hour < 12) return "Good morning"
  if (hour < 17) return "Good afternoon"
  return "Good evening"
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text)
  }
  
  // Fallback for older browsers
  const textArea = document.createElement("textarea")
  textArea.value = text
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()
  
  try {
    document.execCommand("copy")
  } catch (err) {
    console.error("Failed to copy text: ", err)
  }
  
  document.body.removeChild(textArea)
  return Promise.resolve()
}
