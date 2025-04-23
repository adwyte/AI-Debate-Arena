import httpx
from typing import Dict

GROQ_API_KEY = "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"
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"  # or "mixtral-8x7b-32768"

SYSTEM_PROMPT = """
You are an expert debate judge. Given an argument, analyze it on four parameters:
1. Logical Consistency (0-30): Is the reasoning logically sound and well-structured?
2. Evidence Support (0-30): Are real-world data, examples, or sources used effectively?
3. Bias (0-20): Is the argument fair and not manipulative or emotionally skewed?
4. Ethical Balance (0-20): Does it respect moral boundaries and avoid unethical reasoning?

Respond ONLY in the following JSON format:
{
  "logical_consistency": float,
  "evidence_support": float,
  "bias": float,
  "ethical_balance": float,
  "total_score": float
}
"""

async def evaluate_argument(text: str) -> Dict[str, float]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GROQ_BASE_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Evaluate this argument:\n\n{text}"}
                ],
                "temperature": 0.3
            }
        )

        response.raise_for_status()
        content = response.json()
        reply = content['choices'][0]['message']['content']

        try:
            scores = eval(reply) if isinstance(reply, str) else reply
            return scores
        except Exception as e:
            print("Failed to parse LLM response:", reply)
            raise ValueError("Invalid LLM response format") from e
