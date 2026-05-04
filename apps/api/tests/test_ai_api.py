import pytest
from fastapi.testclient import TestClient
from main import app
from services.ai_service import AIService
from routers.ai_query import get_ai_service

client = TestClient(app)

# Helper to mock AIService
class MockAIService:
    def __init__(self, available=True):
        self.available = available
        
    def query(self, question):
        return {
            "answer": "Mock fallback answer." if not self.available else "Mock AI answer.",
            "source_jobs": [],
            "jobs_found": 0,
            "ai_used": self.available,
            "model": "llama3.1:8b" if self.available else "none",
            "fallback": not self.available,
        }
        
    async def query_stream(self, question):
        yield 'event: token\ndata: {"text": "mock"}\\n\\n'

def override_ai_service_available():
    return MockAIService(available=True)

def override_ai_service_offline():
    return MockAIService(available=False)


class TestAIStatusEndpoint:
    def test_status_always_200(self):
        app.dependency_overrides[get_ai_service] = override_ai_service_available
        response = client.get("/api/ai/status")
        assert response.status_code == 200

    def test_status_has_required_fields(self):
        app.dependency_overrides[get_ai_service] = override_ai_service_available
        response = client.get("/api/ai/status")
        data = response.json()
        assert "ollama_available" in data
        assert isinstance(data["ollama_available"], bool)
        assert "model" in data

    def test_status_offline_has_instructions(self):
        app.dependency_overrides[get_ai_service] = override_ai_service_offline
        response = client.get("/api/ai/status")
        data = response.json()
        assert data["ollama_available"] is False
        assert "setup_instructions" in data

class TestAISuggestEndpoint:
    def test_default_suggestions(self):
        response = client.post("/api/ai/suggest", json={})
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) == 6

    def test_domain_suggestions(self):
        response = client.post("/api/ai/suggest", json={"domain": "Data Science & ML"})
        data = response.json()
        assert "suggestions" in data
        assert any("data science" in s.lower() for s in data["suggestions"])

    def test_suggestions_are_strings(self):
        response = client.post("/api/ai/suggest", json={})
        data = response.json()
        assert all(isinstance(s, str) and len(s) > 0 for s in data["suggestions"])

class TestAIQueryEndpoint:
    def test_query_non_stream_returns_json(self):
        app.dependency_overrides[get_ai_service] = override_ai_service_available
        response = client.post("/api/ai/query", json={"question": "python jobs", "stream": False})
        data = response.json()
        assert "answer" in data
        assert "source_jobs" in data
        assert "jobs_found" in data
        assert "ai_used" in data
        assert "fallback" in data

    def test_query_fallback_when_ollama_down(self):
        app.dependency_overrides[get_ai_service] = override_ai_service_offline
        response = client.post("/api/ai/query", json={"question": "python jobs", "stream": False})
        data = response.json()
        assert data["fallback"] is True
        assert data["ai_used"] is False
        assert len(data["answer"]) > 0

    def test_query_stream_returns_sse(self):
        app.dependency_overrides[get_ai_service] = override_ai_service_available
        response = client.post("/api/ai/query", json={"question": "python jobs", "stream": True})
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_query_too_short_returns_422(self):
        response = client.post("/api/ai/query", json={"question": "hi"})
        assert response.status_code == 422

    def test_query_too_long_returns_422(self):
        response = client.post("/api/ai/query", json={"question": "x" * 501})
        assert response.status_code == 422
