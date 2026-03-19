import os
import httpx
import json
import re
import logging
import asyncio
from typing import Any, Dict
from transformers import pipeline, Pipeline
from .ai_response import detect_stance
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME   = "llama-3.3-70b-versatile"   # or "mistral-8x7b-32768"

# ——— System prompt with escaped braces for JSON template ———
SYSTEM_PROMPT = """
You are an expert debate judge. The debate topic is: **{topic}**. Given an argument, analyze it on four parameters:
1. Logical Consistency (0-30): Is the reasoning logically sound, well-structured, and relevant to the debate topic?
2. Evidence Support (0-30): Are real-world data, examples, or sources used effectively?
3. Bias (0-20): Is the argument fair and not manipulative or emotionally skewed?
4. Ethical Balance (0-20): Does it respect moral boundaries and avoid unethical reasoning?

Respond ONLY in the following JSON format:
First output ONLY a JSON object like:
{{
  "logical_consistency": float,
  "evidence_support": float,
  "bias": float,
  "ethical_balance": float,
  "total_score": float
}}
Then, on the next line, write an **Explanation:** section in plain English (e.g. bullet points or short paragraphs) walking through how you chose each score.
""".strip()

# ——— Logger ———
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ——— HTTP client ———
_async_client = httpx.AsyncClient(timeout=30.0)

# ——— Lazy‐loaded NLP pipelines ———
_nlp_lock = asyncio.Lock()
_sentiment_pipe: Pipeline = None
_emotion_pipe:   Pipeline = None
_tone_pipe:      Pipeline = None

async def _load_pipelines():
    global _sentiment_pipe, _emotion_pipe, _tone_pipe
    async with _nlp_lock:
        if _sentiment_pipe is None:
            _sentiment_pipe = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        if _emotion_pipe is None:
            _emotion_pipe = pipeline(
                "text-classification",
                model="bhadresh-savani/distilbert-base-uncased-emotion"
            )
        if _tone_pipe is None:
            _tone_pipe = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )

async def llm_nlp_analysis(text: str):
    prompt = f"""
    Analyze the following argument:

    {text}

    Return JSON:
    {{
        "sentiment": "positive/negative/neutral",
        "tone": ["formal", "informal", "aggressive", "analytical", "persuasive"]
    }}
    """

    try:
        resp = await _async_client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            }
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]

        import json, re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else {}

    except Exception as e:
        logger.error("NLP LLM failed: %s", e)
        return {"sentiment": None, "tone": []}


# async def analyze_nlp_insights(text: str) -> Dict[str, Any]:
#     """
#     Run three pipelines, truncating inputs,
#     and return only labels for sentiment, emotion, tone.
#     """
#     await _load_pipelines()
#     loop = asyncio.get_event_loop()
#     insights: Dict[str, Any] = {}
#
#     # Sentiment
#     try:
#         def do_sentiment():
#             return _sentiment_pipe(text, truncation=True, max_length=512)[0]
#         raw = await loop.run_in_executor(None, do_sentiment)
#         insights["sentiment"] = raw.get("label")
#     except Exception as e:
#         logger.error("Sentiment analysis failed: %s", e)
#         insights["sentiment"] = None
#
#     # Emotion
#     try:
#         def do_emotion():
#             return _emotion_pipe(text, truncation=True, max_length=512, top_k=None)[0]
#         raw = await loop.run_in_executor(None, do_emotion)
#         insights["emotion"] = raw.get("label")
#     except Exception as e:
#         logger.error("Emotion analysis failed: %s", e)
#         insights["emotion"] = None
#
#     # Tone (zero-shot)
#     try:
#         def do_tone():
#             return _tone_pipe(
#                 text,
#                 candidate_labels=["formal","informal","sarcastic","humorous","serious"],
#                 truncation=True,
#                 max_length=512
#             )
#         tone_out = await loop.run_in_executor(None, do_tone)
#         insights["tone"] = tone_out.get("labels", [])[:5]
#     except Exception as e:
#         logger.error("Tone analysis failed: %s", e)
#         insights["tone"] = []
#
#     return insights

async def evaluate_argument(text: str, topic: str) -> Dict[str, Any]:
    """
    1) Calls LLM with topic‐aware prompt
    2) Parses and recomputes scores
    3) Extracts Explanation
    4) Adds NLP insight labels
    """

    # 1) Build the system message with topic
    prompt = SYSTEM_PROMPT.format(topic=topic)

    # 2) LLM request
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Evaluate this argument:\n\n{text}"}
        ],
        "temperature": 0.6
    }
    resp = await _async_client.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]

    # 3) Extract JSON scores
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("Could not parse JSON from LLM response")
    scores = json.loads(match.group())

    # 4) Sanity‐check & total
    for k in ("logical_consistency","evidence_support","bias","ethical_balance"):
        if k not in scores:
            raise KeyError(f"Missing score key: {k}")
    scores["total_score"] = sum(scores[k] for k in (
        "logical_consistency",
        "evidence_support",
        "bias",
        "ethical_balance"
    ))

    # 5) Extract explanation
    explanation = raw.replace(match.group(), "", 1).strip()

    stance = await detect_stance(text, topic)

    result = {"scores": scores, "explanation": explanation, "stance": stance}

    # 6) NLP insights
    try:
        result["nlp_insights"] = await llm_nlp_analysis(text)
    except:
        result["nlp_insights"] = {"sentiment":None,"emotion":None,"tone":[]}

    return result
