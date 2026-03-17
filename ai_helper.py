from openai import OpenAI
import os

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_analysis(service, error, logs, impact, severity):
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
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content