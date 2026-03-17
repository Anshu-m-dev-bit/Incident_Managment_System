from openai import OpenAI
import os

# Initialize client safely
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    print("WARNING: OPENAI_API_KEY not set. AI features will be disabled.")
    client = None


def get_ai_analysis(service, error, logs, impact, severity):
    # If API key is missing, return fallback instead of crashing
    if client is None:
        return "AI analysis is currently unavailable because OPENAI_API_KEY is not set."

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        # Prevent full app crash if API fails
        return f"AI analysis failed: {str(e)}"