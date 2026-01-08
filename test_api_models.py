#!/usr/bin/env python3
"""
Test-Skript um verschiedene OpenRouter-Modellnamen zu testen
Hilft bei der Diagnose des 404-Fehlers
"""

import requests
import json
import sys

# API-Key aus config.json lesen
with open('config.json', 'r') as f:
    config = json.load(f)
    api_key = config['api_key']

url = "https://openrouter.ai/api/v1/chat/completions"

# Test mit minimaler Anfrage
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/thesis-improver"
}

# Verschiedene Modellnamen testen
test_models = [
    ("Kimi K2 Free (aktuell)", "moonshotai/kimi-k2:free"),
    ("Kimi K2 Bezahlt", "moonshotai/kimi-k2"),
    ("Kimi K2 0905 (neuer)", "moonshotai/kimi-k2-0905"),
    ("Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
    ("GPT-4o", "openai/gpt-4o"),
    ("GPT-4o Mini", "openai/gpt-4o-mini"),
]

print("=" * 70)
print("OpenRouter API Model Test")
print("=" * 70)
print(f"API-Key: {api_key[:20]}...")
print(f"URL: {url}")
print("=" * 70)
print()

results = []

for name, model in test_models:
    print(f"Testing: {name}")
    print(f"  Model: {model}")

    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hallo"}],
        "max_tokens": 10
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            print(f"  ✓ Status: {response.status_code} OK")
            try:
                resp_json = response.json()
                content = resp_json['choices'][0]['message']['content']
                print(f"  ✓ Response: {content[:50]}...")
                results.append((name, model, "OK", ""))
            except:
                print(f"  ⚠ Response parsing failed")
                results.append((name, model, "OK", "Parse error"))
        else:
            print(f"  ✗ Status: {response.status_code}")
            error_text = response.text[:200]
            print(f"  ✗ Error: {error_text}")
            results.append((name, model, f"ERROR {response.status_code}", error_text))

    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout")
        results.append((name, model, "TIMEOUT", ""))
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error: {str(e)[:100]}")
        results.append((name, model, "NETWORK ERROR", str(e)[:100]))

    print()

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

working_models = []
failed_models = []

for name, model, status, error in results:
    if status == "OK":
        working_models.append((name, model))
        print(f"✓ {name:30} | {model}")
    else:
        failed_models.append((name, model, status))
        print(f"✗ {name:30} | {model:40} | {status}")

print()
print("=" * 70)
print("RECOMMENDATION")
print("=" * 70)

if working_models:
    print("\n✓ Diese Modelle funktionieren:")
    for name, model in working_models:
        print(f"  - {name}: {model}")

    print("\n📝 Empfohlene config.json:")
    print("```json")
    print('{')
    print('    "models": {')

    # Empfehle beste Kombination
    if any("Kimi" in name for name, _ in working_models):
        kimi_model = next((model for name, model in working_models if "Kimi" in name), "moonshotai/kimi-k2")
    else:
        kimi_model = "moonshotai/kimi-k2"

    if any("Claude" in name for name, _ in working_models):
        claude_model = next((model for name, model in working_models if "Claude" in name), "anthropic/claude-3.5-sonnet")
    else:
        claude_model = "anthropic/claude-3.5-sonnet"

    if any("GPT" in name for name, _ in working_models):
        gpt_model = next((model for name, model in working_models if "GPT" in name and "Mini" not in name), "openai/gpt-4o")
    else:
        gpt_model = "openai/gpt-4o"

    print(f'        "kimi_k2": "{kimi_model}",')
    print(f'        "claude_opus": "{claude_model}",')
    print(f'        "gpt_52": "{gpt_model}"')
    print('    }')
    print('}')
    print("```")
else:
    print("\n✗ KEIN Modell funktioniert!")
    print("\n🔍 Mögliche Ursachen:")
    print("  1. API-Key ungültig oder abgelaufen")
    print("  2. Kein Guthaben auf OpenRouter")
    print("  3. Netzwerkproblem")
    print("\n💡 Nächste Schritte:")
    print("  1. Prüfe OpenRouter Dashboard: https://openrouter.ai/keys")
    print("  2. Prüfe Guthaben: https://openrouter.ai/credits")
    print("  3. Generiere neuen API-Key falls nötig")

if failed_models:
    print("\n\n⚠️ Diese Modelle haben NICHT funktioniert:")
    for name, model, status in failed_models:
        print(f"  - {name} ({model}): {status}")

print()
print("=" * 70)
