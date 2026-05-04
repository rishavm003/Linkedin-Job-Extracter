/**
 * Summary card component
 * Shows key metrics in dashboard
 */

import { Card } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface SummaryCardProps {
  title: string
  value: number | string
  icon: LucideIcon
  color?: string
  subtitle?: string
  trend?: number
}

export function SummaryCard({ 
  title, 
  value, 
  icon: Icon, 
  color = "primary", 
  subtitle, 
  trend 
}: SummaryCardProps) {
  const getColorClasses = (color: string) => {
    switch (color) {
      case "primary":
        return "bg-primary/10 text-primary"
      case "success":
        return "bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400"
      case "warning":
        return "bg-amber-100 text-amber-600 dark:bg-amber-900 dark:text-amber-400"
      case "danger":
        return "bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <Card className="group relative overflow-hidden p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:shadow-[0_8px_30px_rgb(255,255,255,0.02)] border-border/50 hover:border-primary/20 bg-background/60 backdrop-blur-sm">
      {/* Glowing background blob */}
      <div className={cn("absolute -top-10 -right-10 w-32 h-32 rounded-full blur-3xl opacity-0 group-hover:opacity-20 transition-opacity duration-500 pointer-events-none", getColorClasses(color))} />
      
      <div className="flex items-center justify-between relative z-10">
        <div className="space-y-2">
          <p className="text-sm font-semibold tracking-wide text-muted-foreground uppercase">{title}</p>
          <p className="text-3xl font-extrabold tracking-tight">{value}</p>
          {subtitle && (
            <p className="text-sm text-muted-foreground font-medium">{subtitle}</p>
          )}
          {trend !== undefined && (
            <p className="text-sm font-medium mt-1 flex items-center gap-1">
              <span className={trend > 0 ? "text-emerald-500" : "text-rose-500"}>
                {trend > 0 ? "+" : ""}{trend}
              </span>
              <span className="text-muted-foreground text-xs">this week</span>
            </p>
          )}
        </div>
        <div className={cn("p-4 rounded-2xl shadow-sm ring-1 ring-inset ring-white/10 dark:ring-white/5 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3", getColorClasses(color))}>
          <Icon className="h-7 w-7" />
        </div>
      </div>
    </Card>
  )
}
