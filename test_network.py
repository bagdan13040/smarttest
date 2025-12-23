"""
Тестовый скрипт для диагностики проблем с сетью на Android
Запустите этот файл отдельно для проверки
"""
import sys
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")

# Test 1: Import requests
print("\n=== Test 1: Import requests ===")
try:
    import requests
    print("✓ requests imported successfully")
    print(f"  Version: {requests.__version__}")
except ImportError as e:
    print(f"✗ Failed to import requests: {e}")
    sys.exit(1)

# Test 2: Simple HTTP request
print("\n=== Test 2: Simple HTTP request ===")
try:
    response = requests.get("https://httpbin.org/get", timeout=10)
    print(f"✓ HTTP request successful")
    print(f"  Status code: {response.status_code}")
except Exception as e:
    print(f"✗ HTTP request failed: {e}")

# Test 3: HTTPS with SSL verification
print("\n=== Test 3: HTTPS with SSL verification ===")
try:
    response = requests.get("https://www.google.com", timeout=10, verify=True)
    print(f"✓ HTTPS with SSL verification successful")
    print(f"  Status code: {response.status_code}")
except Exception as e:
    print(f"✗ HTTPS with SSL verification failed: {e}")
    print("  Trying without SSL verification...")
    try:
        response = requests.get("https://www.google.com", timeout=10, verify=False)
        print(f"✓ HTTPS without SSL verification successful")
        print(f"  Status code: {response.status_code}")
    except Exception as e2:
        print(f"✗ HTTPS without SSL verification also failed: {e2}")

# Test 4: OpenRouter API endpoint
print("\n=== Test 4: OpenRouter API endpoint ===")
try:
    response = requests.get("https://openrouter.ai", timeout=10, verify=False)
    print(f"✓ Can reach openrouter.ai")
    print(f"  Status code: {response.status_code}")
except Exception as e:
    print(f"✗ Cannot reach openrouter.ai: {e}")

# Test 5: Check environment variables
print("\n=== Test 5: Check environment variables ===")
import os
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    print(f"✓ OPENROUTER_API_KEY found: {api_key[:10]}...{api_key[-5:]}")
else:
    print("✗ OPENROUTER_API_KEY not found in environment")

# Test 6: Check .env file
print("\n=== Test 6: Check .env file ===")
from pathlib import Path
env_path = Path(__file__).parent / '.env'
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")
if env_path.exists():
    print(f"File size: {env_path.stat().st_size} bytes")
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            if 'OPENROUTER_API_KEY' in content:
                print("✓ .env file contains OPENROUTER_API_KEY")
            else:
                print("✗ .env file does not contain OPENROUTER_API_KEY")
    except Exception as e:
        print(f"✗ Could not read .env file: {e}")

# Test 7: Try dotenv
print("\n=== Test 7: Try loading dotenv ===")
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
    api_key_after = os.getenv("OPENROUTER_API_KEY")
    if api_key_after:
        print(f"✓ dotenv loaded successfully, API key available")
    else:
        print("⚠ dotenv loaded but API key not found")
except ImportError:
    print("✗ python-dotenv not installed")
except Exception as e:
    print(f"✗ Failed to load dotenv: {e}")

print("\n=== Summary ===")
print("If all tests pass, the issue might be with:")
print("1. API key not being saved in app settings")
print("2. App not having internet permissions")
print("3. Firewall/VPN blocking openrouter.ai")
print("\nIf tests fail, check the buildozer.spec requirements.")
