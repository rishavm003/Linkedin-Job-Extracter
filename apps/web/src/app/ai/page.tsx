/**
 * AI Assistant page - Full implementation
 * Provides intelligent job market assistance with streaming responses
 */

"use client"

import { useState, useRef, useEffect } from "react"
import { 
  Bot, 
  Send, 
  Sparkles, 
  Loader2, 
  X, 
  RotateCcw,
  ExternalLink,
  AlertCircle,
  CheckCircle2
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { useAIChat } from "@/hooks/useAI"
import { formatSalary } from "@/lib/utils"
import { DomainBadge } from "@/components/ui/DomainBadge"
import { cn } from "@/lib/utils"

export default function AIPage() {
  const {
    messages,
    isLoading,
    aiStatus,
    suggestions,
    sendMessage,
    clearMessages,
    regenerate,
  } = useAIChat()

  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Handle send message
  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    const question = input.trim()
    setInput("")
    await sendMessage(question)
  }

  // Handle Enter key (send on Enter, newline on Shift+Enter)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion)
  }

  // Get last user message for "See all" link
  const lastUserMessage = messages
    .filter(m => m.role === "user")
    .pop()?.content

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Status bar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {aiStatus?.ollama_available ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <span className="text-sm text-muted-foreground">
                AI Assistant ready · {aiStatus.model}
              </span>
            </>
          ) : (
            <>
              <AlertCircle className="h-4 w-4 text-amber-500" />
              <span className="text-sm text-muted-foreground">
                AI offline — showing job results only
              </span>
              <a 
                href="#" 
                className="text-xs text-primary hover:underline ml-2"
                onClick={(e) => {
                  e.preventDefault()
                  alert("To enable AI:\n\n1. Install Ollama from ollama.com\n2. Run: ollama pull llama3.1:8b\n3. Run: ollama serve\n\nOr run: bash scripts/setup_ollama.sh")
                }}
              >
                Setup guide
              </a>
            </>
          )}
        </div>
        
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearMessages}
          >
            <X className="h-4 w-4 mr-1" />
            Clear conversation
          </Button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 ? (
          /* Empty state with suggestions */
          <div className="flex flex-col items-center justify-center h-full py-12">
            {/* Robot icon */}
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary/10 mb-6">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                className="h-10 w-10 text-primary"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <rect x="4" y="8" width="16" height="12" rx="2" />
                <circle cx="9" cy="13" r="1.5" fill="currentColor" />
                <circle cx="15" cy="13" r="1.5" fill="currentColor" />
                <path d="M9 17h6" strokeLinecap="round" />
                <path d="M12 8V6" strokeLinecap="round" />
                <circle cx="12" cy="4" r="2" />
              </svg>
            </div>

            <h1 className="text-3xl font-bold mb-2">Hi! I'm JobBot 👋</h1>
            <p className="text-muted-foreground text-center max-w-md mb-8">
              Ask me anything about jobs, skills, or your career as a fresher
            </p>

            {/* Suggestions grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-xl w-full">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-left p-4 rounded-lg border hover:border-primary/50 hover:bg-accent transition-colors"
                >
                  <p className="text-sm">{suggestion}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Chat messages */
          messages.map((message, index) => (
            <div
              key={message.id}
              className={cn(
                "flex",
                message.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-[85%] md:max-w-[75%]",
                  message.role === "user" ? "max-w-[75%]" : "max-w-[85%]"
                )}
              >
                {message.role === "user" ? (
                  /* User message bubble */
                  <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-3">
                    <p className="text-sm">{message.content}</p>
                  </div>
                ) : (
                  /* Assistant message bubble */
                  <div className="space-y-3">
                    <Card className="rounded-2xl rounded-tl-sm p-4">
                      {/* Bot avatar and name */}
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary" />
                        </div>
                        <span className="text-sm font-medium">JobBot</span>
                      </div>

                      {/* Message content with streaming cursor */}
                      <div className="prose prose-sm max-w-none">
                        <p className="text-sm whitespace-pre-wrap">
                          {message.content}
                          {message.isStreaming && (
                            <span className="animate-pulse">|</span>
                          )}
                        </p>
                      </div>

                      {/* Thinking loader */}
                      {isLoading && message.isStreaming && !message.content && (
                        <div className="flex items-center gap-1 mt-2">
                          <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }} />
                          <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }} />
                          <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }} />
                          <span className="text-xs text-muted-foreground ml-2">Thinking...</span>
                        </div>
                      )}

                      {/* Job cards */}
                      {!message.isStreaming && message.sourceJobs.length > 0 && (
                        <div className="mt-4 pt-4 border-t">
                          <p className="text-xs text-muted-foreground mb-2">
                            Relevant jobs found:
                          </p>
                          <div className="flex gap-3 overflow-x-auto pb-2">
                            {message.sourceJobs.map((job) => (
                              <CompactJobCard key={job.id} job={job} />
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Footer */}
                      {!message.isStreaming && (
                        <div className="mt-3 pt-3 border-t flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                          {message.aiUsed ? (
                            <>
                              <Sparkles className="h-3 w-3" />
                              <span>Powered by llama3.1:8b</span>
                            </>
                          ) : message.fallback ? (
                            <Badge variant="outline" className="text-amber-500 border-amber-500">
                              <AlertCircle className="h-3 w-3 mr-1" />
                              AI offline — showing database results
                            </Badge>
                          ) : null}
                          
                          {message.jobsTotal > message.sourceJobs.length && (
                            <>
                              <span className="mx-1">·</span>
                              <span>Showing {message.sourceJobs.length} of {message.jobsTotal} matching jobs</span>
                              {lastUserMessage && (
                                <>
                                  <span className="mx-1">·</span>
                                  <a
                                    href={`/jobs?q=${encodeURIComponent(lastUserMessage)}`}
                                    className="text-primary hover:underline"
                                  >
                                    See all →
                                  </a>
                                </>
                              )}
                            </>
                          )}
                        </div>
                      )}
                    </Card>

                    {/* Regenerate button */}
                    {!message.isStreaming && index === messages.length - 1 && !isLoading && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={regenerate}
                        className="mt-1"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Regenerate response
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t pt-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about jobs, skills, salaries..."
              className="min-h-[60px] max-h-[120px] resize-none pr-16"
              disabled={isLoading}
            />
            <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
              {input.length} / 500
            </div>
          </div>
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="h-[60px] px-4"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}

import { JobSummary } from "@/lib/types"

/**
 * Compact job card for AI chat
 */
function CompactJobCard({ job }: { job: JobSummary }) {
  return (
    <Card className="flex-none w-[200px] p-3 hover:shadow-md transition-shadow">
      <div className="space-y-2">
        <h4 className="font-semibold text-sm line-clamp-2">{job.title}</h4>
        <p className="text-xs text-muted-foreground">
          {job.company} · {job.location}
        </p>
        <DomainBadge domain={job.domain} size="sm" />
        <p className="text-xs font-medium">
          {formatSalary(job.salary)}
        </p>
        <a
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center text-xs text-primary hover:underline"
        >
          Apply
          <ExternalLink className="h-3 w-3 ml-1" />
        </a>
      </div>
    </Card>
  )
}
