from typing import Set
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Text, Table, Column
from datetime import datetime
from enum import Enum as PyEnum
import json

class Base(DeclarativeBase):
    pass

# Ассоциативная таблица для ролей (оставляем, если используешь)
user_role_table = Table(
    'user_role',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role', String(50), primary_key=True),
)

# УДАЛЕНО: room_participants как Table — теперь это модель RoomParticipant

class Role(PyEnum):
    USER = "USER"

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Связь через модель RoomParticipant
    rooms_assoc: Mapped[Set["RoomParticipant"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    @property
    def rooms(self) -> Set["Room"]:
        return {rp.room for rp in self.rooms_assoc}
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
        }

class RoomParticipant(Base):
    __tablename__ = 'room_participants'
    
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    room: Mapped["Room"] = relationship(back_populates="participants_assoc")
    user: Mapped["User"] = relationship(back_populates="rooms_assoc")

class Room(Base):
    __tablename__ = 'rooms'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=True)
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False,
    )
    
    participants_assoc: Mapped[Set["RoomParticipant"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan"
    )
    
    @property
    def participants(self) -> Set[User]:
        return {rp.user for rp in self.participants_assoc}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'is_running': self.is_running,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return (f'Room(id={self.id!r}, roomname={self.name!r}, '
                f'participants={len(self.participants)!r}, created_at={self.created_at!r}, '
                f'is_running={self.is_running}, password={"***" if self.password else None},')

class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    incorrect_answers: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=True)

    def to_dict(self):
        try:
            # Диагностика
            print(f"DEBUG: incorrect_answers = {repr(self.incorrect_answers)}")
            
            # Обрабатываем incorrect_answers
            if isinstance(self.incorrect_answers, list):
                # Если уже список (например, из SQLAlchemy)
                incorrect_list = self.incorrect_answers
            elif isinstance(self.incorrect_answers, str):
                try:
                    # Пробуем распарсить как JSON
                    incorrect_list = json.loads(self.incorrect_answers)
                except json.JSONDecodeError:
                    # Если не JSON, пробуем как Python literal
                    try:
                        incorrect_list = eval(self.incorrect_answers)
                    except:
                        # Если все fails, создаем пустой список
                        incorrect_list = []
            else:
                incorrect_list = []
            
            # Убедимся, что это список
            if not isinstance(incorrect_list, list):
                incorrect_list = []
            
            # Создаем варианты ответов
            options = incorrect_list
            
            import random
            random.shuffle(options)
            
            result = {
                'id': self.id,
                'question': self.question or "",
                'correct_answer': self.correct_answer or "",
                'incorrect_answers': self.incorrect_answers,
                'category': self.category or "",
                'difficulty': self.difficulty or "",
            }
            
            print(f"DEBUG: Result dict = {result}")
            return result
            
        except Exception as e:
            print(f"ERROR in to_dict: {e}")
            # Возвращаем безопасный fallback
            return {
                'id': self.id or 0,
                'question': self.question or "Error loading question",
                'correct_answer': self.correct_answer or "",
                'incorrect_answers': self.incorrect_answers,
                'category': self.category or "",
                'difficulty': self.difficulty or "",
}
        
class PlayerAnswer(Base):
    __tablename__ = 'player_answers'
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    answer: Mapped[str] = mapped_column(String(255))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    points: Mapped[int] = mapped_column(Integer)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)