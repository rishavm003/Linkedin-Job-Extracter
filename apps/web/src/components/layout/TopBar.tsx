/**
 * Top navigation bar component
 * Shows page title, global search, and theme toggle
 */

"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { SearchBar } from "@/components/ui/SearchBar"
import { usePathname, useRouter } from "next/navigation"

export default function TopBar() {
  const { theme, setTheme } = useTheme()
  const pathname = usePathname()
  const router = useRouter()

  // Get page title based on current route
  const getPageTitle = () => {
    if (pathname === "/") return "Dashboard"
    if (pathname === "/jobs") return "Browse Jobs"
    if (pathname === "/analytics") return "Analytics"
    if (pathname === "/saved") return "Saved Jobs"
    if (pathname === "/ai") return "AI Assistant"
    return "Dashboard"
  }

  const handleSearch = (query: string) => {
    if (query.trim()) {
      router.push(`/jobs?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60 shadow-[0_4px_30px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_30px_rgba(0,0,0,0.1)] transition-colors duration-300">
      <div className="w-full px-6 md:px-8 flex h-16 items-center justify-between">
        {/* Page Title */}
        <div className="flex-1">
          <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">{getPageTitle()}</h1>
        </div>

        {/* Global Search */}
        <div className="flex-1 max-w-md mx-4">
          <SearchBar
            placeholder="Search jobs, skills, companies..."
            onSearch={handleSearch}
            debounceMs={400}
            showSuggestions={true}
          />
        </div>

        {/* Theme Toggle */}
        <div className="flex-1 flex justify-end">
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="inline-flex items-center justify-center rounded-full p-2.5 text-sm font-medium transition-all duration-300 hover:bg-accent hover:text-accent-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ring-1 ring-border/50 hover:shadow-md"
            aria-label="Toggle theme"
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </button>
        </div>
      </div>
    </header>
  )
}
