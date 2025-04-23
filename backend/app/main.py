from fastapi import FastAPI
from backend.app.api import debate, argument, evaluate

app = FastAPI()

app.include_router(debate.router)
app.include_router(argument.router)
app.include_router(evaluate.router)
