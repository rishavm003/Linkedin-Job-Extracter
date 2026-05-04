/**
 * Skill pill component
 * Shows individual skill as a clickable pill
 */

import { cn } from "@/lib/utils"
import { X } from "lucide-react"

interface SkillPillProps {
  skill: string
  onClick?: () => void
  active?: boolean
  onRemove?: () => void
}

export function SkillPill({ skill, onClick, active = false, onRemove }: SkillPillProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium transition-colors",
        active
          ? "bg-primary text-primary-foreground"
          : "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        onClick && "cursor-pointer",
        onRemove && "pr-1"
      )}
    >
      {skill}
      {onRemove && (
        <X
          className="h-3 w-3 hover:text-destructive"
          onClick={(e) => {
            e.stopPropagation()
            onRemove()
          }}
        />
      )}
    </button>
  )
}
