# service/GameService.py

from repository.QuestionRepository import QuestionRepository
from repository.RoomRepository import RoomRepository
from model.Models import Room, PlayerAnswer
import json
import asyncio
from datetime import datetime

class GameService:
    def __init__(self):
        self.room_repo = RoomRepository()
        self.question_repo = QuestionRepository()

    async def start_game_if_all_ready(self, room_id: int):
        if self.room_repo.are_all_participants_ready(room_id):
            await self.start_game(room_id)

    async def start_game(self, room_id: int):
        # 1. Получить комнату
        room = self.room_repo.findById(room_id)
        if room.status != "WAITING":
            return
        
        # 2. Выбрать 5 случайных вопросов
        questions = self.question_repo.find_random(limit=5)
        question_ids = [q.id for q in questions]
        
        # 3. Обновить комнату
        room.status = "STARTED"
        room.current_question_index = 0
        room.question_ids = json.dumps(question_ids)
        self.room_repo.update_room(room)  # ← добавь этот метод в RoomRepository
        
        # 4. Отправить первый вопрос
        first_question = questions[0]
        await self.send_question(room_id, first_question, time_limit=15)

    async def send_question(self, room_id: int, question, time_limit: int):
        from controller.game_controller import broadcast
        await broadcast(room_id, {
            "type": "new_question",
            "question": question.to_dict(),
            "time_limit": time_limit
        })
        
        # Запустить таймер
        await asyncio.sleep(time_limit)
        await self.process_question_results(room_id, question.id)

    async def process_question_results(self, room_id: int, question_id: int):
        # 1. Получить все ответы на этот вопрос
        answers = self.get_answers_for_question(room_id, question_id)
        
        # 2. Обновить лидерборд
        leaderboard = self.get_leaderboard(room_id)
        
        # 3. Отправить результаты
        from controller.game_controller import broadcast
        await broadcast(room_id, {
            "type": "question_results",
            "correct_answer": self.question_repo.findById(question_id).correct_answer,
            "leaderboard": leaderboard
        })
        
        # 4. Подготовить следующий вопрос
        room = self.room_repo.findById(room_id)
        question_ids = json.loads(room.question_ids)
        next_index = room.current_question_index + 1
        
        if next_index < len(question_ids):
            await asyncio.sleep(3)  # пауза перед следующим вопросом
            next_question = self.question_repo.findById(question_ids[next_index])
            room.current_question_index = next_index
            self.room_repo.update_room(room)
            await self.send_question(room_id, next_question, 15)
        else:
            # Конец игры
            room.status = "FINISHED"
            self.room_repo.update_room(room)
            await broadcast(room_id, {
                "type": "game_over",
                "leaderboard": leaderboard
            })

    def submit_answer(self, room_id: int, user_id: int, answer: str):
        room = self.room_repo.findById(room_id)
        if room.status != "STARTED":
            raise ValueError("Game not active")
        
        question_ids = json.loads(room.question_ids)
        current_q_id = question_ids[room.current_question_index]
        
        # Проверить, не отвечал ли уже
        existing = self.get_user_answer(room_id, user_id, current_q_id)
        if existing:
            return  # уже ответил
        
        correct = self.question_repo.findById(current_q_id).correct_answer
        is_correct = (answer == correct)
        points = 10 + (5 if is_correct else 0)  # можно усложнить с таймером
        
        pa = PlayerAnswer(
            room_id=room_id,
            user_id=user_id,
            question_id=current_q_id,
            answer=answer,
            is_correct=is_correct,
            points=points
        )
        self.save_player_answer(pa)

    def get_leaderboard(self, room_id: int):
        # SELECT user_id, SUM(points) FROM player_answers WHERE room_id = ? GROUP BY user_id
        answers = self.get_all_answers_for_room(room_id)
        scores = {}
        for a in answers:
            scores[a.user_id] = scores.get(a.user_id, 0) + a.points
        # Получить имена пользователей
        return [{"user_id": uid, "score": score} for uid, score in scores.items()]