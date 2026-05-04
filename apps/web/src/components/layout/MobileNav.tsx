/**
 * Mobile navigation component
 * Bottom navigation bar for mobile devices
 */

"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, 
  Briefcase, 
  BarChart2, 
  Bookmark, 
  Bot 
} from "lucide-react"
import { NAV_ITEMS } from "@/lib/constants"
import { cn } from "@/lib/utils"

export default function MobileNav() {
  const pathname = usePathname()

  const iconMap = {
    LayoutDashboard,
    Briefcase,
    BarChart2,
    Bookmark,
    Bot,
  }

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-background border-t">
      <nav className="flex items-center justify-around py-2">
        {NAV_ITEMS.map((item) => {
          const Icon = iconMap[item.icon as keyof typeof iconMap]
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center space-y-1 px-3 py-1 rounded-lg transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="text-xs">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
