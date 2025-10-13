from typing import Set
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Table, Column, ForeignKey, Enum
from datetime import datetime
from Room import room_participants
from Room import Room

class Base(DeclarativeBase):
    pass

user_role_table = Table(
    'user_role',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role', String, primary_key=True)
)

class Role(str, Enum):
    User = 'USER'

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default_factory=datetime.utcnow, nullable=False
    )
    
    roles: Mapped[Set[Role]] = relationship(
        secondary=user_role_table,
        collection_class=set,
        default_factory=set,
    )
    
    rooms: Mapped[Set[Room]] = relationship(
        secondary=room_participants,
        back_populates='participants',
        default_factory=set,
    )
    
    def to_dict(self):
        return{
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'User(id={self.id!r}, username={self.username!r}, password={self.password!r}, created_at={self.created_at!r})'