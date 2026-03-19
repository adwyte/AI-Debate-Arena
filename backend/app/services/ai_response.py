import logging
import os
import asyncio
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..kafka.producer import send_argument

from ..db import models

from dotenv import load_dotenv
load_dotenv()

# ——— Configuration ——————————————————————————————————————————————————————
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME      = "llama-3.3-70b-versatile"
NUM_CANDIDATES  = 2      # generate two candidates

logger = logging.getLogger(__name__)
client = httpx.AsyncClient(timeout=30.0)

async def detect_stance(argument: str, topic: str) -> str:
    prompt = f"""
    Topic: {topic}

    Argument: {argument}

    Is this argument FOR or AGAINST the topic?

    Reply with only one word: FOR or AGAINST.
    """

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    resp = await client.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload
    )

    result = resp.json()["choices"][0]["message"]["content"].strip().upper()

    if "AGAINST" in result:
        return "AGAINST"
    else:
        return "FOR"

async def generate_ai_argument(opponent_text: str, topic: str) -> str:

    word_count = len(opponent_text.split())

    # Detect stance
    stance = await detect_stance(opponent_text, topic)

    opposite = "AGAINST" if stance == "FOR" else "FOR"

    dynamic_prompt = f"""
    You are a master debate participant and judge. The debate topic is: **{topic}**.

    The user has written an argument that is {stance} the topic.

    Your task is to write ONE cohesive, tightly-argued counter-argument that is {opposite} the topic, and **will** earn near-perfect scores on all four rubrics below. Follow these rules exactly:

    1. **Length & Depth**  
       • Match the approximate length of the user argument (around {word_count} words).
       • Use varied sentence structure and precise vocabulary—avoid generic phrases.

    2. **Logical Consistency (0–30)**  
       • Begin with a clear thesis statement that directly addresses the opponent’s claim.  
       • Follow with logical premises, each leading step-by-step to your conclusion.  
       • Avoid logical fallacies: do not overgeneralize, misrepresent, or invoke emotion instead of reason.

    3. **Evidence Support (0–30)**  
       • Include distinct, concrete examples, data points, or reputable sources (e.g. study names, dates, statistics).  
       • For each example, briefly explain its relevance back to your thesis.

    4. **Bias (0–20)**  
       • Maintain a neutral, measured tone—no hyperbolic or manipulative language.  
       • Acknowledge a plausible counter-objection in one sentence, then show why your thesis still holds.

    5. **Ethical Balance (0–20)**  
       • Identify any ethical considerations or unintended consequences of your position.  
       • Offer one or two balanced safeguards or policy recommendations to mitigate those risks.

    **Output**: Only the argument text (no headings, bullet lists, or self-congratulation). Write in polished academic style.  
    """

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": dynamic_prompt},
            {"role": "user", "content": opponent_text}
        ],
        "temperature": 0.7,
        "max_tokens": min(max(120, int(word_count)*2), 400)  # dynamic cap
    }

    resp = await client.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload
    )

    return resp.json()["choices"][0]["message"]["content"].strip()


async def create_ai_response(
    db: AsyncSession,
    debate_id: int,
    human_argument_id: int
) -> Dict[str, Any]:

    # 1) Load human argument
    result = await db.execute(
        select(models.Argument).where(
            models.Argument.id == human_argument_id,
            models.Argument.debate_id == debate_id
        )
    )
    human_arg = result.scalar_one_or_none()
    if not human_arg:
        raise HTTPException(404, "Argument not found")

    # 2) Get topic
    dq = await db.execute(
        select(models.Debate).where(models.Debate.id == debate_id)
    )
    topic = dq.scalar_one().topic

    # 3) Generate ONE AI argument (simplify for now)
    ai_text = await generate_ai_argument(human_arg.text, topic)

    # 4) Save AI argument
    ai_arg = models.Argument(
        speaker="AI",
        text=ai_text,
        debate_id=debate_id
    )
    db.add(ai_arg)
    await db.commit()
    await db.refresh(ai_arg)

    # 5) SEND TO KAFKA
    send_argument({
        "argument_id": ai_arg.id,
        "argument_text": ai_arg.text,
        "topic": topic,
        "source": "ai"
    })

    return ai_arg
