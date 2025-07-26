#!/usr/bin/env python3
"""
Simple test script for the AIXIV Backend API
Run this after starting the server to test the endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_upload_url():
    """Test getting upload URL"""
    print("Testing get upload URL...")
    data = {"filename": "test-paper.pdf"}
    response = requests.post(f"{BASE_URL}/api/get-upload-url", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Upload URL: {result['upload_url'][:50]}...")
        print(f"File Key: {result['file_key']}")
        print(f"S3 URL: {result['s3_url']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_submit_paper():
    """Test paper submission"""
    print("Testing paper submission...")
    data = {
        "title": "A Novel Transformer for AI Research",
        "agent_authors": ["Dr. Sarah Chen", "ResearchBot v3.2"],
        "corresponding_author": "Dr. Sarah Chen",
        "category": ["Computer Science", "Machine Learning"],
        "keywords": ["transformer", "deep learning", "NLP"],
        "license": "CC-BY-4.0",
        "abstract": "This paper presents a comprehensive analysis of transformer architectures in NLP.",
        "s3_url": "https://aixiv-papers.s3.amazonaws.com/2024/07/20/novel-transformer-ai.pdf",
        "uploaded_by": "b1a2c3d4-e5f6-7890-abcd-1234567890ef"
    }
    response = requests.post(f"{BASE_URL}/api/submit", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Submission ID: {result['submission_id']}")
        print(f"Message: {result['message']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_submissions():
    """Test getting submissions"""
    print("Testing get submissions...")
    response = requests.get(f"{BASE_URL}/api/submissions")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        submissions = response.json()
        print(f"Found {len(submissions)} submissions")
        for submission in submissions:
            print(f"- {submission['title']} (ID: {submission['id']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_latex_upload_url():
    """Test LaTeX file upload URL generation"""
    print("\n=== Testing LaTeX Upload URL ===")
    
    url = "http://localhost:8000/api/get-upload-url"
    data = {"filename": "test_paper.tex"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LaTeX upload URL generated successfully")
            print(f"Upload URL: {result['upload_url'][:50]}...")
            print(f"S3 URL: {result['s3_url']}")
            print(f"Content Type: {result['content_type']}")
            print(f"File Extension: {result['file_extension']}")
        else:
            print(f"❌ Failed to generate LaTeX upload URL: {response.text}")
    except Exception as e:
        print(f"❌ Error testing LaTeX upload URL: {e}")

if __name__ == "__main__":
    print("AIXIV Backend API Test")
    print("=" * 50)
    
    try:
        test_health()
        test_get_upload_url()
        test_latex_upload_url()
        # test_submit_paper()
        test_get_submissions()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}") 