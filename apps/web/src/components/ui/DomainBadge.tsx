/**
 * Domain badge component
 * Shows job domain with color coding
 */

import { cn, domainColor } from "@/lib/utils"

interface DomainBadgeProps {
  domain: string
  size?: "sm" | "md"
}

export function DomainBadge({ domain, size = "md" }: DomainBadgeProps) {
  const color = domainColor(domain)
  const truncatedDomain = domain.length > 20 ? `${domain.slice(0, 20)}...` : domain

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium",
        size === "sm" ? "px-1.5 py-0.5 text-xs" : "px-2 py-1 text-sm",
      )}
      style={{
        backgroundColor: `${color}15`,
        color: color,
      }}
    >
      {truncatedDomain}
    </span>
  )
}
