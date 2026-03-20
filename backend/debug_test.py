"""Debug test script."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("Testing /api/jobs...")
response = client.get('/api/jobs')
print(f'Status: {response.status_code}')
print(f'Content: {response.content.decode()}')

print("\nTesting /api/health...")
response = client.get('/api/health')
print(f'Status: {response.status_code}')
print(f'Content: {response.content.decode()}')
