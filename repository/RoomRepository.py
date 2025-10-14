from sqlalchemy import create_engine
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.Models import User, Room, Base
from config.config import Settings
import bcrypt

class RoomRepository:
    
    settings: Settings
    engine : Engine
    
    def __init__(self):
        self.settings = Settings()
        
        DATABASE_URL = self.settings.getDatabaseConnectionURL()
        
        self.engine = create_engine(DATABASE_URL)
        
        Base.metadata.create_all(bind=self.engine)
    
    """ 
        эта функция для нахождения всех комнат, она ничего не принимает
        она вызывается по GET endpoint и возвращает массив комнат с их участниками
        /api/v1/room [GET]
        body: пустое
    """
    def findAll(self):
        try: 
            with Session(self.engine) as session:
                stmt = select(Room)
                return list(session.scalars(stmt))
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error fetching rooms: {e}')
    
    """ 
        эта функция для нахождения комнаты по ее id
        принимает только id комнаты
        возвращает саму комнату с участниками ее
        /api/v1/room/{room_id} [GET]
        body: пустое
    """
    def findById(self, room_id: int):
        try:
            with Session(self.engine) as session:
                stmt = session.get(Room, room_id)
                return session.scalar(stmt)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error fetching room {id}: {e}')
    
    """ 
        эта функция меняет статус запуска комнаты
        принимает только id комнаты
        ничего не возвращает
        PATCH запрос
        /api/v1/room/{id} [PATCH]
        body: пустое
    """
    def changeRunning(self, room_id: int):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                room.is_running = not room.is_running
                session.commit()
                session.refresh(room)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of change running of room {room_id}: {e}')
    
    """ 
        эта функция по добавлению участника в комнату
        принимает id комнаты и пользователя
        ничего не возвращает
        /api/v1/room/{room_id}/join [PATCH]
        body: username, user.id
    """
    def addParticipant(self, room_id: int, user: User):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                user = session.get(User, user.id)
                if not room or not user:
                    raise ValueError(f'Room {room_id} or User {user.id} not found')
                room.participants.add(user)
                session.commit()
                session.refresh(room)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of add partisipant {user.id} to room {room_id}: {e}')
    
    """ 
        эта функция создает комнату
        принимает структуру комнаты
        возвращает структуру комнаты
        /api/v1/room [POST]
        body: room.name, room.password(может быть а может и не быть, сделать проверку)
    """
    def createRoom(self, room: Room):
        try:
            with Session(self.engine) as session:
                result = session.execute(select(Room).where(Room.name == room.name))
                db_room = result.scalar_one_or_none()                
                if db_room:
                    raise ValueError('Room with such name is already exist')
                session.add(room)
                session.commit()
                session.refresh(room)
                return room
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of create room: {e}')
    
    """ 
        эта функция ищет комнату по ее имени
        принимает имя комнаты
        возвращает структуру комнаты
        /api/v1/room/{roomname} [GET]
        body: пустое
    """
    def findByRoomname(self, roomname: str):
        try:
            with Session(self.engine) as session:
                stmt = select(Room).where(Room.name == roomname)
                return session.scalar(stmt)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error fetching room by name "{roomname}": {e}')
    
    """ 
        эта функция удаляет пользователя из комнаты
        принимает id комнаты и пользователя
        ничего не возвращает
        /api/v1/room/{room_id}/{user_id} [DELETE]
        body: пустое
    """
    def removeParticipant(self, room_id: int, user_id: int):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                user = session.get(Room, user_id)
                if room and user and user in room.participants:
                    room.participants.remove(user)
                    session.commit()
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error removing participant {user_id} from room {room_id}: {e}')
    
    """ 
        эта функция принимает имя комнаты и пароль
        возвращает пароль если он есть иначе None
        это не апи функция, ты вызываешь ее при добавлении пользователя в комнату
        проверяешь пароль
    """
    def verify_room_password(self, room_id: int, room_password: str):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                if not room.password:
                    return False
                if not bcrypt.checkpw(room_password.encode('utf-8'), room.password.encode('utf-8')):
                    raise ValueError("Wrong password")
        except SQLAlchemyError as e:
            raise RuntimeError(f'Failed to fetch password of room {room_id}: {e}')