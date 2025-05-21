import logging
import os
import asyncio
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db import models
from .evaluation import evaluate_argument

from dotenv import load_dotenv
load_dotenv()

# ——— Configuration ——————————————————————————————————————————————————————
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME      = "llama3-8b-8192"
NUM_CANDIDATES  = 2      # generate two candidates

# ——— Rubric-driven system prompt ——————————————————————————————————————————
SYSTEM_PROMPT_AI = """
You are a master debate participant and judge. The debate topic is: **{topic}**.

Your task is to write ONE cohesive, tightly-argued counter-argument that **will** earn near-perfect scores on all four rubrics below. Follow these rules exactly:

1. **Length & Depth**  
   • Produce at least **150 words** in **two or three well-crafted paragraphs**.  
   • Use varied sentence structure and precise vocabulary—avoid generic phrases.

2. **Logical Consistency (0–30)**  
   • Begin with a clear thesis statement that directly addresses the opponent’s claim.  
   • Follow with 2–4 logical premises, each leading step-by-step to your conclusion.  
   • Avoid logical fallacies: do not overgeneralize, misrepresent, or invoke emotion instead of reason.

3. **Evidence Support (0–30)**  
   • Include **at least three** distinct, concrete examples, data points, or reputable sources (e.g. study names, dates, statistics).  
   • For each example, briefly explain its relevance back to your thesis.

4. **Bias (0–20)**  
   • Maintain a neutral, measured tone—no hyperbolic or manipulative language.  
   • Acknowledge a plausible counter-objection in one sentence, then show why your thesis still holds.

5. **Ethical Balance (0–20)**  
   • Identify any ethical considerations or unintended consequences of your position.  
   • Offer one or two balanced safeguards or policy recommendations to mitigate those risks.

**Output**: Only the argument text (no headings, bullet lists, or self-congratulation). Write in polished academic style.  
""".strip()

logger = logging.getLogger(__name__)
client = httpx.AsyncClient(timeout=30.0)


async def generate_ai_argument(opponent_text: str, topic: str) -> str:
    """
    Generate a single AI argument candidate.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_AI.format(topic=topic)},
            {"role": "user",   "content": opponent_text}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        resp = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.exception("AI generation error")
        raise HTTPException(502, "AI generation error")

    return resp.json()["choices"][0]["message"]["content"].strip()


async def create_ai_response(
    db: AsyncSession,
    debate_id: int,
    human_argument_id: int
) -> Dict[str, Any]:
    # 1) Load the human argument
    result = await db.execute(
        select(models.Argument).where(
            models.Argument.id == human_argument_id,
            models.Argument.debate_id == debate_id
        )
    )
    human_arg = result.scalar_one_or_none()
    if not human_arg:
        raise HTTPException(404, "Argument not found")

    # 2) Load the debate topic
    dq = await db.execute(
        select(models.Debate).where(models.Debate.id == debate_id)
    )
    topic = dq.scalar_one().topic

    # 3) Generate multiple candidates in parallel
    candidate_tasks: List[asyncio.Task] = [
        asyncio.create_task(generate_ai_argument(human_arg.text, topic))
        for _ in range(NUM_CANDIDATES)
    ]
    candidate_texts = await asyncio.gather(*candidate_tasks)

    # 4) Evaluate each candidate in parallel
    eval_tasks = [
        asyncio.create_task(evaluate_argument(text, topic))
        for text in candidate_texts
    ]
    eval_results = await asyncio.gather(*eval_tasks)

    # 5) Pick the candidate with the highest total_score
    best_index = max(
        range(len(eval_results)),
        key=lambda i: eval_results[i]["scores"]["total_score"]
    )
    best_text = candidate_texts[best_index]
    best_eval = eval_results[best_index]

    # 6) Persist the chosen AI argument
    ai_arg = models.Argument(
        speaker="AI",
        text=best_text,
        debate_id=debate_id
    )
    db.add(ai_arg)
    await db.commit()
    await db.refresh(ai_arg)

    # 7) Persist its score
    s = best_eval["scores"]
    ai_score = models.Score(
        argument_id         = ai_arg.id,
        logical_consistency = s["logical_consistency"],
        evidence_support    = s["evidence_support"],
        bias                = s["bias"],
        ethical_balance     = s["ethical_balance"],
        total_score         = s["total_score"],
        explanation         = best_eval["explanation"],
        nlp_insights        = best_eval.get("nlp_insights")
    )
    db.add(ai_score)
    await db.commit()
    await db.refresh(ai_score)

    return {"argument": ai_arg, "score": ai_score}
