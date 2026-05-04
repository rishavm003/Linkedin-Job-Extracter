/**
 * Search bar component with debouncing and suggestions
 */

"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Search, X, Loader2 } from "lucide-react"
import Link from "next/link"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { debounce } from "@/lib/utils"
import { useJobSearch } from "@/hooks/useJobs"
import { DomainBadge } from "./DomainBadge"
import { cn } from "@/lib/utils"

interface SearchBarProps {
  placeholder?: string
  onSearch: (query: string) => void
  debounceMs?: number
  showSuggestions?: boolean
  className?: string
}

export function SearchBar({ 
  placeholder = "Search...", 
  onSearch, 
  debounceMs = 400,
  showSuggestions = false,
  className 
}: SearchBarProps) {
  const [query, setQuery] = useState("")
  const [isDebouncing, setIsDebouncing] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Stable debounced search — stored in a ref so it's never recreated on re-render
  const debouncedSearchRef = useRef(
    debounce((searchQuery: string) => {
      setIsDebouncing(false)
      onSearch(searchQuery)
    }, debounceMs)
  )

  // Handle input change
  const handleChange = (value: string) => {
    setQuery(value)
    // We've removed auto-triggering onSearch here to prevent premature navigation
    // Suggestions (if enabled) still reactive based on the 'query' state
  }

  // Handle submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
      setIsOpen(false)
    }
  }

  // Clear search
  const handleClear = () => {
    setQuery("")
    setIsDebouncing(false)
    inputRef.current?.focus()
  }

  // Close suggestions on escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsOpen(false)
      }
    }

    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [])

  // Get suggestions if enabled
  const { data: searchData, isLoading } = useJobSearch(
    { q: query, limit: 5 },
    showSuggestions && query.length >= 2
  )

  if (!showSuggestions) {
    return (
      <form onSubmit={handleSubmit} className={cn("relative flex items-center gap-2", className)}>
        <div className="relative flex-1 group">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            ref={inputRef}
            type="text"
            placeholder={placeholder}
            value={query}
            onChange={(e) => handleChange(e.target.value)}
            className="pl-10 pr-9 h-10 rounded-xl"
          />
          {query && (
            <Button
              type="button"
              variant="ghost"
              size="icon-xs"
              onClick={handleClear}
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0 hover:bg-muted"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
        <Button 
          type="submit" 
          size="sm" 
          className="shrink-0 h-10 px-4 rounded-xl shadow-sm hover:shadow-md transition-all active:scale-95"
        >
          Search
        </Button>
      </form>
    )
  }

  return (
    <div className={cn("relative flex items-center gap-2", className)}>
      <form onSubmit={handleSubmit} className="flex-1 flex items-center gap-2">
        <div className="relative flex-1 group">
          <Popover open={isOpen && query.length >= 2} onOpenChange={setIsOpen}>
            {/* 
              Use render as a div and nativeButton={false} to prevent the browser 
              from treating the Space key as a 'click' activation on a button,
              which causes focus loss and accidental form triggers.
            */}
            <PopoverTrigger 
              className="w-full p-0 border-0 bg-transparent text-left focus:outline-none ring-0"
            >
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                <Input
                  ref={inputRef}
                  type="text"
                  placeholder={placeholder}
                  value={query}
                  onChange={(e) => handleChange(e.target.value)}
                  onFocus={() => setIsOpen(true)}
                  className="pl-10 pr-9 h-10 rounded-xl"
                />
              </div>
            </PopoverTrigger>
            {query && (
              <Button
                type="button"
                variant="ghost"
                size="icon-xs"
                onClick={handleClear}
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0 hover:bg-muted z-10"
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            )}
            <PopoverContent className="w-full p-0" align="start">
              {isLoading ? (
                <div className="p-4 text-center">
                  <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                  <p className="text-sm text-muted-foreground mt-2">Searching...</p>
                </div>
              ) : searchData?.jobs && searchData.jobs.length > 0 ? (
                <div className="max-h-64 overflow-y-auto">
                  {searchData.jobs.map((job) => (
                    <Link
                      key={job.id}
                      href={`/jobs/${job.id}`}
                      className="block p-3 hover:bg-accent transition-colors"
                      onClick={() => setIsOpen(false)}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{job.title}</p>
                          <p className="text-sm text-muted-foreground">{job.company}</p>
                        </div>
                        <DomainBadge domain={job.domain} size="sm" />
                      </div>
                    </Link>
                  ))}
                </div>
              ) : query.length >= 2 ? (
                <div className="p-4 text-center">
                  <p className="text-sm text-muted-foreground">No results found</p>
                </div>
              ) : null}
            </PopoverContent>
          </Popover>
        </div>
        <Button 
          type="submit" 
          size="sm" 
          className="shrink-0 h-10 px-4 rounded-xl shadow-sm hover:shadow-md transition-all active:scale-95"
        >
          Search
        </Button>
      </form>
    </div>
  )
}
