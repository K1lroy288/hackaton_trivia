from typing import Set
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Table, Column, ForeignKey, Boolean
from datetime import datetime
from enum import Enum as PyEnum

class Base(DeclarativeBase):
    pass

user_role_table = Table(
    'user_role',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role', String(50), primary_key=True),
)

room_participants = Table(
    'room_participants',
    Base.metadata,
    Column('room_id', ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)

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
    
    rooms: Mapped[Set["Room"]] = relationship(
        secondary=room_participants,
        back_populates="participants",
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
        }

class Room(Base):
    __tablename__ = 'rooms'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=True)
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="WAITING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False,
    )
    
    participants: Mapped[Set['User']] = relationship(
        secondary=room_participants,
        back_populates='rooms',
    )
    
    
    def to_dict(self):
        return {
            'id': self.id,
            'roomname': self.name,
            'is_running': self.is_running,
            'created_at': self.created_at.isoformat(),
            'participants': [user.to_dict() for user in self.participants],
            'max_players': self.max_players,
            'status': self.status,
        }
    
    def __repr__(self) -> str:
        return f'Room(id={self.id!r}, roomname={self.name!r}, participants={self.participants!r}, created_at={self.created_at!r}, is_running={self.is_running}, password={self.password}, max_players={self.max_players}, status={self.status})'
    
class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String, nullable=False)
    incorrect_answers: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=True)
    difficulty: Mapped[str] = mapped_column(String, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'correct_answer': self.correct_answer,
            'options': self.options,
            'category': self.category,
            'difficulty': self.difficulty,
        }

class RoomParticipant(Base):
    __tablename__ = 'room_participants'
    
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    room: Mapped["Room"] = relationship(back_populates="participants_assoc")
    user: Mapped["User"] = relationship(back_populates="rooms_assoc")