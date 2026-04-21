from kafka import KafkaConsumer
import json
import asyncio
import time
from sqlalchemy import select

from app.services.evaluation import evaluate_argument
from app.db.session import async_session_maker
from app.db import models

consumer = KafkaConsumer(
    'debate.input',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='evaluation_group_' + str(int(time.time())),
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Listening for messages...")

import asyncio

async def safe_evaluate(argument_text, topic, retries=3):
    for attempt in range(retries):
        try:
            return await evaluate_argument(argument_text, topic)
        except Exception as e:
            print(f"⚠️ Retry {attempt+1}/{retries} failed:", e)
            await asyncio.sleep(2)

    print("❌ All retries failed")
    return None

async def process_message(data):
    print("Processing:", data)

    if "argument_id" not in data:
        print("⚠️ Old message format, skipping...")
        return

    argument_id = data["argument_id"]
    argument_text = data["argument_text"]
    topic = data["topic"]

    # 🧠 Run AI evaluation
    print("➡️ Calling evaluation...")

    evaluation_result = await safe_evaluate(argument_text, topic)

    if evaluation_result is None:
        print("❌ Skipping message due to failure")
        return

    score_data = evaluation_result["scores"]
    explanation = evaluation_result["explanation"]
    nlp = evaluation_result["nlp_insights"]

    # 🗄️ DB session
    async with async_session_maker() as db:

        result = await db.execute(
            select(models.Score).where(models.Score.argument_id == argument_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("⚠️ Already evaluated, skipping:", argument_id)
            return

        db_score = models.Score(
            argument_id=argument_id,
            logical_consistency=score_data["logical_consistency"],
            evidence_support=score_data["evidence_support"],
            bias=score_data["bias"],
            ethical_balance=score_data["ethical_balance"],
            total_score=score_data["total_score"],
            explanation=explanation,
            stance=evaluation_result.get("stance"),
            nlp_insights=nlp
        )

        db.add(db_score)
        await db.commit()

    print("✅ Stored evaluation for argument:", argument_id)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

for message in consumer:
    try:
        loop.run_until_complete(process_message(message.value))
    except Exception as e:
        print("❌ Error processing message:", e)