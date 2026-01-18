#!/usr/bin/env python
"""Quick test of quiz generation"""
import os
import sys

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

from llm import generate_quiz

def test_generation():
    """Test quiz generation"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)
    
    print(f"Testing quiz generation with API key: {api_key[:10]}...")
    print("This may take 1-2 minutes...\n")
    
    result = generate_quiz("Python", "легкий", api_key=api_key)
    
    if 'error' in result:
        print(f"✗ Generation failed: {result['error']}")
        sys.exit(1)
    
    print(f"✓ Generation successful!")
    print(f"  Theory length: {len(result.get('theory', ''))} chars")
    print(f"  Questions: {len(result.get('questions', []))}")
    
    if result.get('questions'):
        q = result['questions'][0]
        print(f"\n  First question: {q.get('question', '')[:80]}...")
        print(f"  Options: {len(q.get('options', []))} options")

if __name__ == '__main__':
    test_generation()
