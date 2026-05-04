/**
 * Portal badge component
 * Shows job portal with colored border
 */

import { cn } from "@/lib/utils"
import { portalColor } from "@/lib/utils"

interface PortalBadgeProps {
  portal: string
  displayName: string
}

export function PortalBadge({ portal, displayName }: PortalBadgeProps) {
  const color = portalColor(portal)

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border-l-2 bg-background",
      )}
      style={{
        borderLeftColor: color,
      }}
    >
      {displayName}
    </span>
  )
}
