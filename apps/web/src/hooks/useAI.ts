/**
 * React hook for AI chat functionality
 * Manages chat state, streaming responses, and message history
 */

"use client"

import { useState, useEffect, useCallback } from "react"
import { fetchAIStatus, fetchAISuggestions, queryAI } from "@/lib/api"
import type { ChatMessage, AIStatus, JobSummary } from "@/lib/types"

export interface UseAIChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  aiStatus: AIStatus | null
  suggestions: string[]
  sendMessage: (question: string) => Promise<void>
  clearMessages: () => void
  regenerate: () => void
}

export function useAIChat(): UseAIChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [mounted, setMounted] = useState(false)

  // Set mounted flag to prevent hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  // Fetch AI status on mount
  useEffect(() => {
    const loadStatus = async () => {
      try {
        const status = await fetchAIStatus()
        setAiStatus(status)
      } catch (error) {
        console.error("Failed to fetch AI status:", error)
        setAiStatus({
          ollama_available: false,
          model: "llama3.1:8b",
          ollama_url: "http://localhost:11434",
          setup_instructions: "Run bash scripts/setup_ollama.sh to enable AI"
        })
      }
    }
    loadStatus()
  }, [])

  // Fetch suggestions on mount
  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        const response = await fetchAISuggestions()
        setSuggestions(response.suggestions)
      } catch (error) {
        console.error("Failed to fetch suggestions:", error)
        // Fallback suggestions
        setSuggestions([
          "Which companies are hiring Python freshers in Bangalore?",
          "What skills do I need for a data science role?",
          "Show me remote internships paying above 3 LPA",
          "Which domains have the most fresher openings?",
          "What is a good salary to expect as a fresher in 2024?",
          "Which job portals are best for freshers in India?",
        ])
      }
    }
    loadSuggestions()
  }, [])

  const sendMessage = useCallback(async (question: string) => {
    // Add user message - use stable ID to prevent hydration mismatch
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: question,
      isStreaming: false,
      sourceJobs: [],
      jobsTotal: 0,
      aiUsed: false,
      fallback: false,
      timestamp: new Date(),
    }

    // Add assistant placeholder
    const assistantMessage: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: "assistant",
      content: "",
      isStreaming: true,
      sourceJobs: [],
      jobsTotal: 0,
      aiUsed: false,
      fallback: false,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage, assistantMessage])
    setIsLoading(true)

    await queryAI(
      question,
      // onToken - append token to assistant message
      (token) => {
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage.role === "assistant") {
            lastMessage.content += token
          }
          return newMessages
        })
      },
      // onJobs - set source jobs on assistant message
      (jobs, total) => {
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage.role === "assistant") {
            lastMessage.sourceJobs = jobs
            lastMessage.jobsTotal = total
          }
          return newMessages
        })
      },
      // onDone - mark streaming complete
      (meta) => {
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage.role === "assistant") {
            lastMessage.isStreaming = false
            lastMessage.aiUsed = meta.ai_used
            lastMessage.fallback = meta.fallback
          }
          return newMessages
        })
        setIsLoading(false)
      },
      // onError - show error message
      (message) => {
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]
          if (lastMessage.role === "assistant") {
            lastMessage.content = `Error: ${message}`
            lastMessage.isStreaming = false
            lastMessage.fallback = true
          }
          return newMessages
        })
        setIsLoading(false)
      }
    )
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const regenerate = useCallback(() => {
    // Find last user message
    const lastUserMessageIndex = messages
      .map((m, i) => ({ ...m, index: i }))
      .filter(m => m.role === "user")
      .pop()?.index

    if (lastUserMessageIndex === undefined) return

    const lastUserMessage = messages[lastUserMessageIndex]
    
    // Remove the last assistant message if it exists
    const lastMessage = messages[messages.length - 1]
    if (lastMessage.role === "assistant") {
      setMessages(prev => prev.slice(0, -1))
    }

    // Re-send the question
    sendMessage(lastUserMessage.content)
  }, [messages, sendMessage])

  return {
    messages,
    isLoading,
    aiStatus,
    suggestions: mounted ? suggestions : [], // Return empty until mounted to prevent hydration mismatch
    sendMessage,
    clearMessages,
    regenerate,
  }
}
