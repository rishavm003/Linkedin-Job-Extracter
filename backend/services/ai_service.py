import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'jobextractor'))

import httpx
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from storage.search import JobSearchService
from utils.logger import logger
from config.settings import JOB_DOMAINS

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
CONTEXT_JOB_LIMIT = 20     # max jobs to pass as context


SYSTEM_PROMPT = """You are JobBot, an intelligent job market assistant
for Indian students and freshers looking for their first job or internship.

You have access to real job listings from portals like LinkedIn, Naukri,
Internshala, Remotive, and RemoteOK.

Your personality:
- Friendly, encouraging, and practical
- Speak to freshers who may be anxious about job hunting
- Always give actionable advice alongside job recommendations
- Use simple language, avoid corporate jargon

Your capabilities:
- Find relevant jobs from the database based on the user's question
- Explain what skills are in demand for a given domain
- Advise on salary expectations for freshers in India
- Suggest which portals are best for specific job types
- Help users understand job requirements

Rules:
- Always mention the company name and apply link when recommending jobs
- If salary is disclosed, mention it clearly in Indian format (LPA)
- Never make up job listings — only recommend from the context provided
- If no relevant jobs are found, say so honestly and give general advice
- Keep responses concise — 150 to 300 words maximum
- Use bullet points for job listings
- End with one encouraging sentence for the fresher

Context — current job listings relevant to this question:
{job_context}

Current date context: Jobs were scraped recently from major portals.
"""

USER_PROMPT = """User question: {question}

Based on the job listings above, provide a helpful response.
If the question is about specific jobs, list the most relevant ones.
If it's about skills or career advice, give practical guidance."""


class AIService:

    def __init__(self):
        self._search = JobSearchService()
        self._llm = None
        self.available = False
        self._check_ollama()

    def _check_ollama(self) -> None:
        """
        Check if Ollama is running and llama3.1:8b is available.
        Sets self.available = True only if both conditions are met.
        Never raises — logs warnings instead.
        """
        try:
            resp = httpx.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                timeout=3.0
            )
            models = [m["name"] for m in resp.json().get("models", [])]
            has_model = any(OLLAMA_MODEL.split(":")[0] in m for m in models)
            if has_model:
                self._llm = Ollama(
                    base_url=OLLAMA_BASE_URL,
                    model=OLLAMA_MODEL,
                    temperature=0.3,
                    num_predict=512,
                )
                self.available = True
                logger.info(f"[AI] Ollama ready: {OLLAMA_MODEL}")
            else:
                logger.warning(
                    f"[AI] Ollama running but {OLLAMA_MODEL} not found. "
                    f"Available: {models}. Run: ollama pull {OLLAMA_MODEL}"
                )
        except Exception as e:
            logger.warning(
                f"[AI] Ollama not reachable at {OLLAMA_BASE_URL}: {e}. "
                f"AI features disabled. Run scripts/setup_ollama.sh to enable."
            )

    def _retrieve_context_jobs(self, question: str) -> list[dict]:
        """
        Search the job database for listings relevant to the question.
        Uses JobSearchService which tries ES first, falls back to PG.
        Returns up to CONTEXT_JOB_LIMIT job dicts.
        """
        try:
            result = self._search.search(
                query=question,
                is_fresher=True,
                limit=CONTEXT_JOB_LIMIT,
                offset=0,
            )
            return result.get("hits", [])
        except Exception as e:
            logger.warning(f"[AI] Context retrieval failed: {e}")
            return []

    def _build_job_context(self, jobs: list[dict]) -> str:
        """
        Format a list of job dicts into a concise context string
        that the LLM can read and reason about.
        """
        if not jobs:
            return "No specific job listings found for this query."

        lines = []
        for i, job in enumerate(jobs[:CONTEXT_JOB_LIMIT], 1):
            salary = job.get("salary_raw") or "Not disclosed"
            skills = ", ".join(job.get("skills", [])[:6]) or "Not specified"
            lines.append(
                f"{i}. {job.get('title')} at {job.get('company')}\n"
                f"   Location: {job.get('location')} | "
                f"Remote: {'Yes' if job.get('is_remote') else 'No'}\n"
                f"   Domain: {job.get('domain')} | "
                f"Type: {job.get('job_type')} | "
                f"Seniority: {job.get('seniority')}\n"
                f"   Skills: {skills}\n"
                f"   Salary: {salary}\n"
                f"   Apply: {job.get('apply_url')}\n"
            )
        return "\n".join(lines)

    def _extract_source_job_ids(self, jobs: list[dict]) -> list[str]:
        """Return the IDs of jobs used as context."""
        return [j["id"] for j in jobs if j.get("id")]

    def query(self, question: str) -> dict:
        """
        Non-streaming query. Returns full answer as a string.
        Use this for simple integrations.

        Returns:
        {
          "answer": str,
          "source_jobs": list[str],  — job IDs used as context
          "jobs_found": int,
          "ai_used": bool,           — False if Ollama unavailable
          "model": str,
          "fallback": bool           — True if returned jobs only, no AI
        }
        """
        context_jobs = self._retrieve_context_jobs(question)
        job_context  = self._build_job_context(context_jobs)
        source_ids   = self._extract_source_job_ids(context_jobs)

        if not self.available:
            return {
                "answer": self._fallback_answer(question, context_jobs),
                "source_jobs": source_ids,
                "jobs_found": len(context_jobs),
                "ai_used": False,
                "model": "none",
                "fallback": True,
            }

        try:
            prompt = PromptTemplate(
                input_variables=["job_context", "question"],
                template=SYSTEM_PROMPT + "\n\n" + USER_PROMPT,
            )
            chain = prompt | self._llm | StrOutputParser()
            answer = chain.invoke({
                "job_context": job_context,
                "question": question,
            })
            return {
                "answer": answer.strip(),
                "source_jobs": source_ids,
                "jobs_found": len(context_jobs),
                "ai_used": True,
                "model": OLLAMA_MODEL,
                "fallback": False,
            }
        except Exception as e:
            logger.error(f"[AI] LLM inference failed: {e}")
            return {
                "answer": self._fallback_answer(question, context_jobs),
                "source_jobs": source_ids,
                "jobs_found": len(context_jobs),
                "ai_used": False,
                "model": "none",
                "fallback": True,
            }

    async def query_stream(self, question: str):
        """
        Async generator that yields Server-Sent Events (SSE).
        Yields events in this order:
          1. event: jobs — the context jobs as JSON
          2. event: token — one per LLM output token (streaming)
          3. event: done — signals stream end with metadata
          4. event: error — only if something went wrong

        Each yield is a formatted SSE string:
          "event: {name}\ndata: {json}\n\n"
        """
        import json

        context_jobs = self._retrieve_context_jobs(question)
        source_ids   = self._extract_source_job_ids(context_jobs)

        # Always yield the context jobs first so frontend can
        # show job cards while AI is still generating text
        jobs_payload = {
            "jobs": context_jobs[:6],      # top 6 for display
            "total_found": len(context_jobs),
        }
        yield f"event: jobs\ndata: {json.dumps(jobs_payload)}\n\n"

        if not self.available:
            fallback_text = self._fallback_answer(question, context_jobs)
            yield f"event: token\ndata: {json.dumps({'text': fallback_text})}\n\n"
            yield f"event: done\ndata: {json.dumps({'ai_used': False, 'fallback': True})}\n\n"
            return

        try:
            job_context = self._build_job_context(context_jobs)
            prompt_text = (SYSTEM_PROMPT + "\n\n" + USER_PROMPT).format(
                job_context=job_context,
                question=question,
            )

            # Stream from Ollama directly using httpx for token streaming
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt_text,
                        "stream": True,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 512,
                        },
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

            yield f"event: done\ndata: {json.dumps({'ai_used': True, 'model': OLLAMA_MODEL, 'source_jobs': source_ids})}\n\n"

        except Exception as e:
            logger.error(f"[AI] Streaming failed: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    def _fallback_answer(self, question: str, jobs: list[dict]) -> str:
        """
        Human-readable response when Ollama is not available.
        Summarises the retrieved jobs in plain text.
        """
        if not jobs:
            return (
                "I found no jobs matching your query in the database right now. "
                "Try running the scraper to fetch fresh listings: "
                "`python main.py run`. "
                "Note: AI-powered responses require Ollama to be running. "
                "Run `scripts/setup_ollama.sh` to set it up."
            )

        lines = [
            f"I found {len(jobs)} relevant job(s) for your query "
            f"(AI assistant offline — showing structured results):\n"
        ]
        for job in jobs[:5]:
            salary = job.get("salary_raw") or "Salary not disclosed"
            lines.append(
                f"• {job.get('title')} at {job.get('company')}\n"
                f"  {job.get('location')} · {job.get('domain')}\n"
                f"  {salary}\n"
                f"  Apply: {job.get('apply_url')}\n"
            )
        lines.append(
            "\nTo enable AI-powered responses, run: "
            "`bash scripts/setup_ollama.sh`"
        )
        return "\n".join(lines)
