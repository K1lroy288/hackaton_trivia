from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.Room import Room
from model.User import User
from config.config import Settings

class RoomRepository:
    
    settings: Settings
    engine : Engine
    
    def __init__(self):
        self.settings = Settings()
        
        DATABASE_URL = self.settings.getDatabaseConnectionURL()
        
        self.engine = create_engine(DATABASE_URL)
    
    def findAll(self):
        try: 
            with Session(self.engine) as session:
                stmt = session.get(Room)
                return list(session.scalars(stmt))
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of get rooms: {e}')
        
    def findById(self):
        try:
            with Session(self.engine) as session:
                stmt = session.get(Room, id)
                return session.scalar(stmt)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of get room {id}: {e}')
        
    def changeRunning(self, room_id: int):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                room.is_running = not room.is_running
                session.commit()
                session.refresh(room)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of change running of room {room_id}: {e}')
    
    def addParticipant(self, room_id: int, user_id: int):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                room.participants.add(user)
                session.commit()
                session.refresh(room)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of add partisipant {user.id} to room {room_id}: {e}')