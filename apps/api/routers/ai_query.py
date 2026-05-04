from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from functools import lru_cache
from services.ai_service import AIService
import json
import os

router = APIRouter(prefix="/api/ai", tags=["ai"])

@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return AIService()

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question about jobs or career",
        examples=["Which companies are hiring Python freshers in Bangalore?"]
    )
    stream: bool = Field(
        default=True,
        description="Stream tokens as they are generated (recommended)"
    )

class QueryResponse(BaseModel):
    answer: str
    source_jobs: list[str]
    jobs_found: int
    ai_used: bool
    model: str
    fallback: bool

@router.post(
    "/query",
    summary="Query the AI job assistant",
    description="""
    Ask natural language questions about job listings, skills,
    salaries, and career advice for freshers.

    When stream=true (default), returns Server-Sent Events:
    - event: jobs — relevant job listings as JSON
    - event: token — one LLM output token at a time
    - event: done — end of stream with metadata
    - event: error — if something went wrong

    When stream=false, returns a complete JSON response.
    Requires Ollama to be running with llama3.1:8b.
    Falls back gracefully if Ollama is unavailable.
    """,
)
async def query_ai(request: QueryRequest, ai_service: AIService = Depends(get_ai_service)):
    if request.stream:
        return StreamingResponse(
            ai_service.query_stream(request.question),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            }
        )
    else:
        result = ai_service.query(request.question)
        return QueryResponse(**result)

@router.get("/status")
def ai_status(ai_service: AIService = Depends(get_ai_service)):
    status = {
        "ollama_available": ai_service.available,
        "model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        "ollama_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    }
    if not ai_service.available:
        status["setup_instructions"] = "Run bash scripts/setup_ollama.sh to enable AI"
    return status

class SuggestRequest(BaseModel):
    domain: str = None
    seniority: str = None

class SuggestionResponse(BaseModel):
    suggestions: list[str]

@router.post("/suggest", response_model=SuggestionResponse)
def suggest_questions(request: SuggestRequest):
    domain = request.domain
    if domain:
        suggestions = [
            f"Which {domain} companies are hiring freshers right now?",
            f"What skills do I need for a {domain} job?",
            f"What is the average salary for {domain} freshers?",
            f"Is {domain} a good career path for freshers in India?",
            f"Which cities have the most {domain} jobs?",
            f"What certifications help for {domain} roles?"
        ]
    else:
        suggestions = [
            "Which companies are hiring Python freshers in Bangalore?",
            "What skills do I need for a data science role?",
            "Show me remote internships paying above 3 LPA",
            "Which domains have the most fresher openings?",
            "What is a good salary to expect as a fresher in 2024?",
            "Which job portals are best for freshers in India?"
        ]
    return SuggestionResponse(suggestions=suggestions)
