#!/usr/bin/env python
"""Test OpenRouter API connectivity"""
import urllib.request
import ssl
import socket

def test_openrouter():
    """Test if OpenRouter is reachable"""
    print("Testing OpenRouter API connectivity...")
    
    # Create SSL context
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        print("1. Testing openrouter.ai homepage...")
        r = urllib.request.urlopen('https://openrouter.ai', timeout=10, context=ctx)
        print(f"   ✓ Homepage reachable (status {r.status})")
    except Exception as e:
        print(f"   ✗ Homepage failed: {e}")
    
    try:
        print("2. Testing API endpoint...")
        headers = {
            'Authorization': 'Bearer test',
            'Content-Type': 'application/json'
        }
        req = urllib.request.Request(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            method='OPTIONS'
        )
        r = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"   ✓ API endpoint reachable (status {r.status})")
    except urllib.error.HTTPError as e:
        print(f"   ✓ API endpoint reachable (HTTP {e.code})")
    except Exception as e:
        print(f"   ✗ API endpoint failed: {e}")
    
    try:
        print("3. Testing DNS resolution...")
        ip = socket.gethostbyname('openrouter.ai')
        print(f"   ✓ DNS resolved to {ip}")
    except Exception as e:
        print(f"   ✗ DNS failed: {e}")

if __name__ == '__main__':
    test_openrouter()
