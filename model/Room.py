from typing import Set
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Table, Column, ForeignKey, Enum, Boolean
from datetime import datetime
from User import User

class Base(DeclarativeBase):
    pass

room_participants = Table(
    'room_participants',
    Base.metadata,
    Column('room_id', ForeignKey('rooms.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)



class Room(Base):
    __tablename__ = 'rooms'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    roomname: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=True)
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.utcnow, nullable=False
    )
    
    participants: Mapped[Set['User']] = relationship(
        secondary=room_participants,
        back_populates='rooms',
        default_factory=set,
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'roomname': self.roomname,
            'is_running': self.is_running,
            'created_at': self.created_at,
            'participants': [user.to_dict() for user in self.participants],
        }
    
    def __repr__(self) -> str:
        return f'Room(id={self.id!r}, roomname={self.roomname!r}, participants={self.participants!r}, created_at={self.created_at!r}, is_running={self.is_running}, password={self.password})'