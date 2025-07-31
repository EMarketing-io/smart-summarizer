import re
import json


def extract_json_block(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            print("❌ JSON decoding failed:", e)
            print("OpenAI response:", text)
            raise
    else:
        print("❌ No JSON found in OpenAI response.")
        print("Raw output:", text)
        raise ValueError("Response did not contain valid JSON.")
