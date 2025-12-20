import requests
import json

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
}

data = {
    "model": "nex-agi/deepseek-v3.1-nex-n1:free",
    "messages": [
        {"role": "system", "content": "You are a JSON-only API. Reply only with JSON."},
        {"role": "user", "content": "ping"}
    ],
    "max_tokens": 10
}

try:
    r = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    print('Status:', r.status_code)
    print('Headers:\n', '\n'.join(f'{k}: {v}' for k, v in r.headers.items()))
    txt = r.text
    if len(txt) > 1000:
        txt = txt[:1000] + '\n...[truncated]'
    print('Body:\n', txt)
except Exception as e:
    print('Request exception:', repr(e))
