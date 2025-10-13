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
        }
    
    def __repr__(self) -> str:
        return f'Room(id={self.id!r}, roomname={self.name!r}, participants={self.participants!r}, created_at={self.created_at!r}, is_running={self.is_running}, password={self.password})'