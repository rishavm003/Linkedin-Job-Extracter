/**
 * Seniority badge component
 * Shows job seniority level with color coding
 */

import { cn } from "@/lib/utils"

interface SeniorityBadgeProps {
  seniority: string
}

export function SeniorityBadge({ seniority }: SeniorityBadgeProps) {
  const getColorClasses = (level: string) => {
    switch (level.toLowerCase()) {
      case "fresher":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "intern":
        return "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200"
      case "entry level":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "junior":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
      case "mid level":
        return "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200"
      case "senior":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
    }
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium",
        getColorClasses(seniority)
      )}
    >
      {seniority}
    </span>
  )
}
