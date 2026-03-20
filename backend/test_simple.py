"""Simple test without TestClient."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dependencies import get_search_service, get_postgres
from schemas.job_schema import JobListResponse

async def test_search():
    """Test search service directly."""
    search_service = get_search_service()
    pg = get_postgres()
    
    # Test search
    result = search_service.search(
        query="",
        limit=5,
        offset=0
    )
    
    print(f"Search result: {result}")
    print(f"Total jobs: {result['total']}")
    print(f"Source: {result['source']}")
    
    if result['hits']:
        print(f"First job: {result['hits'][0]['title']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_search())
