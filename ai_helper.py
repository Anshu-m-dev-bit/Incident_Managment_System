from openai import OpenAI
import os

def get_ai_analysis(service, error, logs, impact, severity):
    api_key = os.getenv("ZAI_API_KEY")  # changed env variable

    print("DEBUG: ZAI_API_KEY =", "FOUND" if api_key else "MISSING")

    if not api_key:
        return "AI analysis is currently unavailable because ZAI_API_KEY is not set."

    try:
        # 🔥 Change: base_url added for Z.ai
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.z.ai/v1"   # <-- important
        )

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

        response = client.chat.completions.create(
            model="glm-4.5-air",   # 🔥 changed model
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis failed: {str(e)}"