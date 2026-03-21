#!/usr/bin/env python3
"""
Demo script to test the new API integrations.
Run this to verify Adzuna and RapidAPI scrapers are working.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.orchestrator import ScraperOrchestrator
from utils.logger import logger


async def test_new_scrapers():
    """Test the new API scrapers with your API keys."""
    
    print("🚀 Testing new API scrapers...\n")
    
    # Test only the new API scrapers
    test_portals = ["adzuna", "rapidapi"]
    
    try:
        orchestrator = ScraperOrchestrator(
            portals=test_portals,
            max_per_portal=5,  # Small number for testing
            keywords=["fresher", "entry level", "junior"]
        )
        
        jobs = await orchestrator.run()
        
        print(f"\n✅ Successfully scraped {len(jobs)} jobs from new APIs")
        
        # Group by portal
        by_portal = {}
        for job in jobs:
            portal = job.source_portal
            if portal not in by_portal:
                by_portal[portal] = []
            by_portal[portal].append(job)
        
        print("\n📊 Results by portal:")
        for portal, portal_jobs in by_portal.items():
            print(f"\n{portal.upper()}: {len(portal_jobs)} jobs")
            for i, job in enumerate(portal_jobs[:3], 1):  # Show first 3
                print(f"  {i}. {job.title} at {job.company}")
                print(f"     Location: {job.location}")
                if job.salary_raw:
                    print(f"     Salary: {job.salary_raw}")
        
        if len(jobs) == 0:
            print("\n⚠️  No jobs scraped. Check your API keys in .env file:")
            print("   - ADZUNA_APP_ID")
            print("   - ADZUNA_APP_KEY") 
            print("   - RAPIDAPI_KEY")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        logger.exception("Scraping failed")


async def test_apyhub():
    """Test Apyhub API for text summarization."""
    
    print("\n🔧 Testing Apyhub API...")
    
    try:
        from utils.apyhub_client import get_apyhub_client
        
        client = get_apyhub_client()
        
        if not client.api_key:
            print("⚠️  APYHUB_API_KEY not found in .env")
            return
        
        # Test text summarization
        sample_text = """
        We are looking for a talented Software Engineer to join our growing team. 
        The ideal candidate will have experience with Python, JavaScript, and modern web frameworks.
        You will be responsible for developing and maintaining web applications, working with cross-functional teams,
        and contributing to the entire development lifecycle. This is a full-time position based in Bangalore
        with competitive salary and benefits package. Fresh graduates are encouraged to apply.
        """
        
        summary = await client.summarize_text(sample_text, max_sentences=2)
        
        if summary:
            print("✅ Text summarization working:")
            print(f"   Original: {len(sample_text)} chars")
            print(f"   Summary: {len(summary)} chars")
            print(f"   Result: {summary}")
        else:
            print("❌ Text summarization failed")
            
        # Test keyword extraction
        keywords = await client.extract_keywords(sample_text, max_keywords=5)
        
        if keywords:
            print("\n✅ Keyword extraction working:")
            print(f"   Keywords: {', '.join(keywords)}")
        else:
            print("❌ Keyword extraction failed")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Apyhub test failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("JobExtractor - API Integration Test")
    print("=" * 60)
    
    asyncio.run(test_new_scrapers())
    asyncio.run(test_apyhub())
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
