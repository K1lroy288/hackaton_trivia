# repository/PlayerAnswerRepository.py
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.Models import PlayerAnswer, Base
from config.config import Settings

class PlayerAnswerRepository:
    def __init__(self, engine=None):
        if engine is None:
            settings = Settings()
            DATABASE_URL = settings.getDatabaseConnectionURL()
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(bind=self.engine)
        else:
            self.engine = engine

    def save(self, player_answer: PlayerAnswer):
        try:
            with Session(self.engine) as session:
                session.add(player_answer)
                session.commit()
                session.refresh(player_answer)
                return player_answer
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to save player answer: {e}")

    def get_by_room_and_question(self, room_id: int, question_id: int):
        try:
            with Session(self.engine) as session:
                stmt = select(PlayerAnswer).where(
                    PlayerAnswer.room_id == room_id,
                    PlayerAnswer.question_id == question_id
                )
                return list(session.scalars(stmt))
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to fetch answers: {e}")

    def get_by_room_user_question(self, room_id: int, user_id: int, question_id: int):
        try:
            with Session(self.engine) as session:
                stmt = select(PlayerAnswer).where(
                    PlayerAnswer.room_id == room_id,
                    PlayerAnswer.user_id == user_id,
                    PlayerAnswer.question_id == question_id
                )
                return session.scalar(stmt)
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to fetch user answer: {e}")

    def get_all_for_room(self, room_id: int):
        try:
            with Session(self.engine) as session:
                stmt = select(PlayerAnswer).where(PlayerAnswer.room_id == room_id)
                return list(session.scalars(stmt))
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to fetch all answers for room: {e}")
