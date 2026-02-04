"""
SmartTest Backend Server - Упрощенная версия
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import httpx
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartTest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Простые модели данных
class QuizRequest(BaseModel):
    topic: str
    level: str
    user_interests: Optional[str] = None

class RoadmapRequest(BaseModel):
    topic: str
    goal: str
    level: str
    user_interests: Optional[str] = None

class OpenQuestionsRequest(BaseModel):
    topic: str
    level: str
    theory_text: str

class EvaluateAnswerRequest(BaseModel):
    question: str
    user_answer: str
    notes: str

class ImageChatRequest(BaseModel):
    image_base64: str
    user_message: str


async def call_openrouter(messages: List[Dict], model: str = "mistralai/mistral-7b-instruct:free") -> str:
    """Простой вызов OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"model": model, "messages": messages}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        raise HTTPException(status_code=500, detail="LLM error")


@app.get("/")
async def root():
    return {
        "service": "SmartTest API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "api_key_set": bool(OPENROUTER_API_KEY)}


@app.post("/api/v1/generate-quiz")
async def generate_quiz(request: QuizRequest):
    interests = f"\nUser interests: {request.user_interests}" if request.user_interests else ""
    
    prompt = f"""Generate a lesson on {request.topic} (Level: {request.level}){interests}

Return JSON with:
- theory: 800-1000 words
- questions: 10 MC questions with options, correct index, explanation
- open_questions: 5 open questions with notes

Format:
{{
  "theory": "...",
  "questions": [{{"question": "...", "options": ["A","B","C","D"], "correct": 0, "explanation": "..."}}],
  "open_questions": [{{"question": "...", "notes": "..."}}]
}}"""
    
    messages = [{"role": "user", "content": prompt}]
    content = await call_openrouter(messages)
    
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    return {"success": True, "data": json.loads(content)}


@app.post("/api/v1/generate-roadmap")
async def generate_roadmap(request: RoadmapRequest):
    interests = f"\nUser interests: {request.user_interests}" if request.user_interests else ""
    
    prompt = f"""Create learning roadmap for {request.topic}. Goal: {request.goal}. Level: {request.level}{interests}

Return JSON with 5-8 modules:
{{
  "roadmap_name": "...",
  "description": "...",
  "modules": [{{"id": 1, "name": "...", "description": "...", "topics": ["..."], "prerequisites": [], "estimated_hours": 5}}]
}}"""
    
    messages = [{"role": "user", "content": prompt}]
    content = await call_openrouter(messages)
    
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    
    return {"success": True, "data": json.loads(content)}


@app.post("/api/v1/generate-questions")
async def generate_open_questions(request: OpenQuestionsRequest):
    prompt = f"""Based on {request.topic} theory (Level: {request.level}), generate 5 open questions.

Theory: {request.theory_text[:2000]}

Return JSON: {{"questions": [{{"question": "...", "notes": "key points"}}]}}"""
    
    messages = [{"role": "user", "content": prompt}]
    content = await call_openrouter(messages)
    
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    
    return {"success": True, "data": json.loads(content)}


@app.post("/api/v1/evaluate-answer")
async def evaluate_answer(request: EvaluateAnswerRequest):
    prompt = f"""Evaluate answer.
Question: {request.question}
Expected: {request.notes}
Student answer: {request.user_answer}

Return JSON: {{"score": 8, "feedback": "...", "strengths": ["..."], "improvements": ["..."]}}"""
    
    messages = [{"role": "user", "content": prompt}]
    content = await call_openrouter(messages)
    
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    
    return {"success": True, "data": json.loads(content)}


@app.post("/api/v1/chat-with-image")
async def chat_with_image(request: ImageChatRequest):
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": request.user_message},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{request.image_base64}"}}
        ]
    }]
    
    content = await call_openrouter(messages, model="google/gemini-2.0-flash-exp:free")
    return {"success": True, "response": content}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
