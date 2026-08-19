"""
MyCards AI proxy — a tiny FastAPI server that holds the Anthropic API key
and answers questions about the user's card transactions using Claude.

The Android app sends { question, transactions }; we build a prompt,
call Claude, and return { answer }. The key never ships to the phone.
"""
import os

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()  # read ANTHROPIC_API_KEY from .env

# The SDK reads ANTHROPIC_API_KEY from the environment automatically.
client = anthropic.Anthropic()

app = FastAPI(title="MyCards AI proxy")

# CORS is harmless for a native app; handy if you ever test from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = (
    "You are a helpful personal-finance assistant inside a mobile app called MyCards. "
    "Answer the user's question about their card transactions concisely and accurately. "
    "Use ONLY the transaction data provided in the message. If the answer isn't in the "
    "data, say so plainly. All amounts are in US dollars. Keep answers short and friendly."
)


class Transaction(BaseModel):
    merchant: str
    category: str
    amount: float
    date: str


class ChatRequest(BaseModel):
    question: str
    transactions: list[Transaction]


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Format the transactions as readable lines for the model.
    lines = "\n".join(
        f"- {t.date} | {t.merchant} | {t.category} | ${t.amount:.2f}"
        for t in req.transactions
    )
    user_content = (
        f"Here are my transactions:\n{lines}\n\n"
        f"Question: {req.question}"
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    answer = "".join(block.text for block in message.content if block.type == "text")
    return ChatResponse(answer=answer)
