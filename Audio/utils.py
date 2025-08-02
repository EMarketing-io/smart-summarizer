import re
import json


# 🔍 Extracts the first JSON block from a text response (commonly from GPT/OpenAI)
def extract_json_block(text):
    
    # 🧠 Use regex to locate a block that starts and ends with curly braces
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:

        # ✅ Attempt to parse the matched block as JSON
        try:
            return json.loads(match.group())
        
        except json.JSONDecodeError as e:
           
            # ❌ If decoding fails, print debug info and re-raise the error
            print("❌ JSON decoding failed:", e)
            print("OpenAI response:", text)
            raise
    
    # ❌ No valid JSON block found in the response
    else:
        print("❌ No JSON found in OpenAI response.")
        print("Raw output:", text)
        raise ValueError("Response did not contain valid JSON.")

