"""
Simple test to check what's causing the 500 error
"""
import requests
import json

# Test simple API call
try:
    response = requests.post(
        "http://localhost:8000/api/v1/chat/send",
        json={
            "message": "Hello",
            "session_id": None,
            "session_title": "Test"
        },
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test knowledge base stats
try:
    response = requests.get("http://localhost:8000/api/v1/chat/knowledge-stats")
    print(f"\nKnowledge Stats Status: {response.status_code}")
    print(f"Knowledge Stats Response: {response.text}")
except Exception as e:
    print(f"Knowledge Stats Error: {e}")
