from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.debate     import router as debate_router
from backend.app.api.argument   import router as argument_router
from backend.app.api.evaluate   import router as evaluate_router
from backend.app.api.transcribe import router as transcribe_router
from backend.app.api.leaderboard import router as leaderboard_router

app = FastAPI()

app.router.redirect_slashes = False


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(debate_router)
app.include_router(argument_router)
app.include_router(evaluate_router)
app.include_router(transcribe_router)
app.include_router(leaderboard_router)

@app.get("/")
async def root():
    return {"message": "Debate Arena API is running!"}
