# service/GameService.py
from repository.QuestionRepository import QuestionRepository
from repository.RoomRepository import RoomRepository
from repository.PlayerAnswerRepository import PlayerAnswerRepository  # ← новое
from model.Models import Room, PlayerAnswer
import json
import asyncio
from datetime import datetime
from webSocketManager.manager import manager

class GameService:
    def __init__(self):
        self.room_repo = RoomRepository()
        self.question_repo = QuestionRepository()
        self.answer_repo = PlayerAnswerRepository()  # ← новое

    async def start_game_if_all_ready(self, room_id: int):
        # Пока оставим заглушку
        await self.start_game(room_id)

    async def start_game(self, room_id: int):
        room = self.room_repo.findById(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")
        if getattr(room, 'status', 'WAITING') != "WAITING":
            return

        questions = self.question_repo.find_random(limit=5)
        if len(questions) < 5:
            raise ValueError("Not enough questions in DB")

        question_ids = [q.id for q in questions]
        room.status = "STARTED"
        room.current_question_index = 0
        room.question_ids = json.dumps(question_ids)
        self.room_repo.update_room(room)

        first_question = questions[0]
        await self.send_question(room_id, first_question, time_limit=15)

    async def send_question(self, room_id: int, question, time_limit: int):
        await manager.broadcast_to_room(room_id, {
            "type": "new_question",
            "question": question.to_dict(),
            "time_limit": time_limit
        })
        await asyncio.sleep(time_limit)
        await self.process_question_results(room_id, question.id)

    async def process_question_results(self, room_id: int, question_id: int):
        answers = self.get_answers_for_question(room_id, question_id)
        leaderboard = self.get_leaderboard(room_id)
        correct_answer = self.question_repo.findById(question_id).correct_answer

        await manager.broadcast_to_room(room_id, {
            "type": "question_results",
            "correct_answer": correct_answer,
            "leaderboard": leaderboard
        })

        room = self.room_repo.findById(room_id)
        question_ids = json.loads(room.question_ids)
        next_index = room.current_question_index + 1

        if next_index < len(question_ids):
            await asyncio.sleep(3)
            next_question = self.question_repo.findById(question_ids[next_index])
            room.current_question_index = next_index
            self.room_repo.update_room(room)
            await self.send_question(room_id, next_question, 15)
        else:
            room.status = "FINISHED"
            self.room_repo.update_room(room)
            await manager.broadcast_to_room(room_id, {
                "type": "game_over",
                "leaderboard": leaderboard
            })

    def submit_answer(self, room_id: int, user_id: int, answer: str):
        room = self.room_repo.findById(room_id)
        if not room or getattr(room, 'status', '') != "STARTED":
            raise ValueError("Game not active")

        question_ids = json.loads(room.question_ids)
        current_q_id = question_ids[room.current_question_index]

        existing = self.get_user_answer(room_id, user_id, current_q_id)
        if existing:
            return

        correct = self.question_repo.findById(current_q_id).correct_answer
        is_correct = (answer == correct)
        points = 10 if is_correct else 0

        pa = PlayerAnswer(
            room_id=room_id,
            user_id=user_id,
            question_id=current_q_id,
            answer=answer,
            is_correct=is_correct,
            points=points,
            answered_at=datetime.utcnow()
        )
        self.save_player_answer(pa)

    # === НОВЫЕ МЕТОДЫ ===
    def get_answers_for_question(self, room_id: int, question_id: int):
        return self.answer_repo.get_by_room_and_question(room_id, question_id)

    def get_user_answer(self, room_id: int, user_id: int, question_id: int):
        return self.answer_repo.get_by_room_user_question(room_id, user_id, question_id)

    def save_player_answer(self, player_answer: PlayerAnswer):
        self.answer_repo.save(player_answer)

    def get_all_answers_for_room(self, room_id: int):
        return self.answer_repo.get_all_for_room(room_id)

    def get_leaderboard(self, room_id: int):
        answers = self.get_all_answers_for_room(room_id)
        scores = {}
        for a in answers:
            scores[a.user_id] = scores.get(a.user_id, 0) + a.points
        return [{"user_id": uid, "score": score} for uid, score in scores.items()]