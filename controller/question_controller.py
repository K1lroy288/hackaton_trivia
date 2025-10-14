from model.Models import Question
from fastapi import APIRouter, HTTPException, Path
from service.QuestionService import QuestionService
from pydantic import BaseModel
from typing import Optional
from model.Models import Question

router = APIRouter()
quest_service = QuestionService()

@router.get("/api/v1/trivia/question", status_code=200)
def get_random_question():
    try:
        question = quest_service.find_random()
        return question.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

