import requests
import os

def get_ai_analysis(service, error, logs, impact, severity):
    api_key = os.getenv("OPENROUTER_API_KEY")

    print("DEBUG: OPENROUTER_API_KEY =", "FOUND" if api_key else "MISSING")

    if not api_key:
        return "AI analysis unavailable: API key not set."

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        prompt = f"""
You are an SRE assistant.

Analyze the following production incident:

Service: {service}
Error: {error}
Logs: {logs}
Impact: {impact}
Severity: {severity}

Provide:
1. Summary
2. Root Causes
3. Troubleshooting Steps
4. Fixes
5. Preventive Measures
"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        response = requests.post(url, headers=headers, json=data)

        # 🔴 Important: handle bad responses safely
        if response.status_code != 200:
            print("ERROR STATUS:", response.status_code)
            print("ERROR RESPONSE:", response.text)
            return f"AI analysis failed (status {response.status_code})"

        res_json = response.json()

        # 🔴 Safe parsing (prevents crashes)
        if "choices" not in res_json:
            return "AI response format error."

        return res_json["choices"][0]["message"]["content"]

    except Exception as e:
        print("EXCEPTION:", str(e))
        return f"AI analysis failed: {str(e)}"