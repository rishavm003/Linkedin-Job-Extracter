/**
 * Sidebar navigation component
 * Shows navigation items and API status
 */

"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { 
  LayoutDashboard, 
  Briefcase, 
  BarChart2, 
  Bookmark, 
  Bot 
} from "lucide-react"
import { NAV_ITEMS } from "@/lib/constants"
import { fetchHealth, fetchAIStatus } from "@/lib/api"
import { cn } from "@/lib/utils"

export default function Sidebar() {
  const pathname = usePathname()
  const [apiStatus, setApiStatus] = useState<"loading" | "online" | "offline">("loading")
  const [lastCheck, setLastCheck] = useState<Date>(new Date())

  const [mounted, setMounted] = useState(false)

  const { data: aiStatusData } = useQuery({
    queryKey: ["ai-status"],
    queryFn: fetchAIStatus,
    staleTime: 30 * 1000,     // refresh every 30s
    retry: false,             // don't spam if backend is down
  })

  // Check API health status
  useEffect(() => {
    setMounted(true)
    const checkHealth = async () => {
      try {
        await fetchHealth()
        setApiStatus("online")
      } catch {
        setApiStatus("offline")
      }
      setLastCheck(new Date())
    }

    // Initial check
    checkHealth()

    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000)

    return () => clearInterval(interval)
  }, [])

  const iconMap = {
    LayoutDashboard,
    Briefcase,
    BarChart2,
    Bookmark,
    Bot,
  }

  return (
    <div className="hidden md:flex md:w-60 md:flex-col md:fixed md:inset-y-0 bg-background border-r">
      {/* Logo */}
      <div className="flex flex-col items-center px-6 py-6 border-b border-border/40">
        <div className="flex items-center space-x-3 w-full">
          <div className="p-2 bg-gradient-to-br from-primary to-indigo-500 rounded-xl shadow-sm ring-1 ring-primary/20">
            <Briefcase className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="flex flex-col items-start justify-center text-left">
            <h1 className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-foreground to-foreground/70">
              JobExtractor
            </h1>
            <p className="text-[10px] font-bold tracking-widest uppercase text-muted-foreground -mt-0.5">Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {NAV_ITEMS.map((item) => {
          const Icon = iconMap[item.icon as keyof typeof iconMap]
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-gradient-to-r from-primary/15 to-primary/5 text-primary shadow-sm ring-1 ring-primary/20"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
              )}
            >
              <div className="relative">
                <Icon className={cn("h-5 w-5 transition-transform duration-200", !isActive && "group-hover:scale-110 group-hover:text-primary")} />
                {item.href === "/ai" && aiStatusData && (
                  <span 
                    className={cn(
                      "absolute -top-1 -right-1 flex h-2.5 w-2.5 rounded-full ring-2 ring-background",
                      aiStatusData.ollama_available ? "bg-green-500" : "bg-amber-500"
                    )}
                  />
                )}
              </div>
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* API Status */}
      <div className="px-4 py-4 border-t">
        <div className="flex items-center space-x-2">
          <div
            className={cn(
              "w-2 h-2 rounded-full",
              apiStatus === "online" 
                ? "bg-green-500" 
                : apiStatus === "offline" 
                ? "bg-red-500" 
                : "bg-yellow-500 animate-pulse"
            )}
          />
          <span className="text-xs text-muted-foreground">
            {apiStatus === "online" 
              ? "API Connected" 
              : apiStatus === "offline" 
              ? "API Offline" 
              : "Checking..."
            }
          </span>
        </div>
        <span className="text-xs text-muted-foreground mt-1 block">
          {mounted ? `Last check: ${lastCheck.toLocaleTimeString()}` : " "}
        </span>
      </div>
    </div>
  )
}
