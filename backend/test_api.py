"""Simple test script to verify API endpoints."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import httpx
import asyncio

async def test_api():
    """Test API endpoints."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("Testing /api/health...")
            response = await client.get(f"{base_url}/api/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test jobs list
            print("\nTesting /api/jobs...")
            response = await client.get(f"{base_url}/api/jobs?page_size=5")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Found {data['total']} jobs")
                if data['jobs']:
                    print(f"First job: {data['jobs'][0]['title']}")
            
            # Test analytics
            print("\nTesting /api/analytics/dashboard...")
            response = await client.get(f"{base_url}/api/analytics/dashboard")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Total jobs: {data['summary']['total_jobs']}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
