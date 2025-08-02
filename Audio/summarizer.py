import openai
from audio.utils import extract_json_block


# 🧠 Generates a structured summary from meeting transcript using OpenAI GPT
def generate_summary(transcript_text):
    # 📜 System prompt that instructs GPT to act as a business analyst and return a JSON object
    system_prompt = """
You are an expert business analyst. You will be given a raw transcript from a client-agency meeting.

Your task is to extract a comprehensive and structured summary in JSON format using the schema below.

Please follow these guidelines strictly:
- Be concise but informative. Ensure each bullet is standalone and easy to understand.
- Use consistent formatting (no sentence fragments; start with verbs where applicable).
- For To-Do items, include responsible parties and estimated deadlines if mentioned or inferable.
- Include actionable insights and KPIs if discussed.
- Maintain professional tone. Avoid repetition.

Return **only valid JSON** with no extra text, markdown, or explanation.

Schema:
{
  "mom": ["<Key discussion points and agreements>", "..."],
  "todo_list": ["<Actionable task with responsible person and timeframe, if known>", "..."],
  "action_plan": {
    "decision_made": ["<Key decisions taken>", "..."],
    "key_services_to_promote": ["<Service list>", "..."],
    "target_geography": ["<Location list>", "..."],
    "budget_and_timeline": ["<Budget, timeline details>", "..."],
    "lead_management_strategy": ["<Lead handling strategy>", "..."],
    "next_steps_and_ownership": ["<Task and responsible person>", "..."]
  }
}
"""
    # 🤖 Call GPT to summarize the provided transcript text using the system prompt
    chat_response = openai.ChatCompletion.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "system", "content": system_prompt},   # System-level instructions
            {"role": "user", "content": transcript_text},   # Actual input transcript
        ],
        temperature=0.3,     # Low temperature = more consistent and factual output
    )

    return extract_json_block(chat_response.choices[0].message.content)