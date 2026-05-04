"""Integration test without TestClient."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dependencies import get_search_service, get_postgres
from routers.jobs import list_jobs, _to_job_summary

async def test_list_jobs():
    """Test list_jobs endpoint directly."""
    search_service = get_search_service()
    
    # Create a mock request object
    class MockRequest:
        pass
    
    request = MockRequest()
    
    # Call the endpoint directly
    result = await list_jobs(
        request=request,
        search_service=search_service,
        domain=None,
        seniority=None,
        is_remote=None,
        portal=None,
        is_fresher=None,
        skills=None,
        salary_min=None,
        salary_max=None,
        page=1,
        page_size=5,
        sort_by="scraped_at",
        sort_order="desc"
    )
    
    print(f"Result type: {type(result)}")
    print(f"Total jobs: {result.total}")
    print(f"Source: {result.source}")
    
    if result.jobs:
        print(f"First job: {result.jobs[0].title}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_list_jobs())
