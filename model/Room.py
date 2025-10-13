from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from typing import Optional
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Room(Base):
    def __init__(self):
        pass