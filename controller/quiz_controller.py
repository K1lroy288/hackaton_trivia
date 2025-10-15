from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from repository.QuestionRepository import QuestionRepository

router = APIRouter(prefix="/api/v1/quiz", tags=["quiz"])

@router.get("/{room_id}/questions")
async def get_quiz_questions(room_id: int):
    try:
        quiz_repo = QuestionRepository()
        questions = quiz_repo.getQuestionsByRoomId(room_id)
        
        if not questions:
            raise HTTPException(status_code=404, detail="Вопросы для викторины не найдены")
        
        return JSONResponse(content={
            "room_id": room_id,
            "questions": questions,
            "total_questions": len(questions)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения вопросов: {str(e)}")

@router.post("/{room_id}/answer")
async def submit_answer(room_id: int, request: Request):

    try:
        data = await request.json()
        user_id = data.get("user_id")
        question_id = data.get("question_id")
        answer = data.get("answer")
        
        if not all([user_id, question_id, answer]):
            raise HTTPException(status_code=400, detail="Не все обязательные поля заполнены")
        
        quiz_repo = QuestionRepository()
        result = quiz_repo.submitAnswer(room_id, user_id, question_id, answer)
        
        return JSONResponse(content={
            "correct": result["correct"],
            "correct_answer": result["correct_answer"],
            "points": result["points"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки ответа: {str(e)}")

@router.get("/{room_id}/scoreboard")
async def get_scoreboard(room_id: int):

    try:
        quiz_repo = QuestionRepository()
        scoreboard = quiz_repo.getScoreboard(room_id)
        
        return JSONResponse(content={
            "room_id": room_id,
            "scoreboard": scoreboard
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения результатов: {str(e)}")

@router.post("/{room_id}/start")
async def start_quiz(room_id: int):
    try:
        quiz_repo = QuestionRepository()
        result = quiz_repo.startQuiz(room_id)
        
        return JSONResponse(content={
            "success": True,
            "message": "Викторина начата",
            "quiz_id": result["quiz_id"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка начала викторины: {str(e)}")

@router.post("/{room_id}/finish")
async def finish_quiz(room_id: int):
    try:
        quiz_repo = QuestionRepository()
        result = quiz_repo.finishQuiz(room_id)
        
        return JSONResponse(content={
            "success": True,
            "message": "Викторина завершена",
            "final_scores": result["final_scores"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка завершения викторины: {str(e)}")