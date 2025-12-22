from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

@app.route('/generate_quiz', methods=['POST'])
def proxy_generate_quiz():
    data = request.json
    print(f"Received request: {data}")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return jsonify({"error": "API Key not found on server"}), 500

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Forward the request to OpenRouter
    try:
        # We reconstruct the body to ensure it matches what OpenRouter expects
        # The app sends the full body intended for OpenRouter
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        print(f"Error forwarding request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so the phone can connect
    print("Starting server on 0.0.0.0:5000")
    print("Make sure your phone and PC are on the same Wi-Fi.")
    print("Find your PC's IP address (ipconfig) and enter it in the app settings.")
    app.run(host='0.0.0.0', port=5000, debug=True)
