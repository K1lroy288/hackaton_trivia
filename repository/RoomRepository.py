from sqlalchemy import create_engine, func
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.Models import User, Room, Base, RoomParticipant
from config.config import Settings
import bcrypt


class RoomRepository:
    settings: Settings
    engine: Engine

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
                stmt = select(Room).where(Room.id == room_id)

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

    def addParticipant(self, room_id: int, user_id: int):
        try:
            print(f"Repository: Adding user {user_id} to room {room_id}")  # Логирование

            with Session(self.engine) as session:
                # Проверяем существование комнаты и пользователя
                room = session.get(Room, room_id)
                if not room:
                    raise ValueError(f"Room {room_id} not found")

                user = session.get(User, user_id)
                if not user:
                    raise ValueError(f"User {user_id} not found")

                # Проверяем, не является ли пользователь уже участником
                existing = session.execute(
                    select(RoomParticipant)
                    .where(RoomParticipant.room_id == room_id)
                    .where(RoomParticipant.user_id == user_id)
                ).scalar_one_or_none()

                if existing:
                    print(f"User {user_id} is already in room {room_id}")  # Логирование
                    return  # Уже участник, ничего не делаем

                # Создаем новую запись участника
                rp = RoomParticipant(room_id=room_id, user_id=user_id)
                session.add(rp)
                session.commit()
                session.refresh(rp)

                print(f"Successfully added user {user_id} to room {room_id}")  # Логирование

        except SQLAlchemyError as e:
            print(f"SQLAlchemy error in addParticipant: {str(e)}")  # Логирование
            raise RuntimeError(f'Error adding participant {user_id} to room {room_id}: {e}')
        except Exception as e:
            print(f"Unexpected error in addParticipant: {str(e)}")  # Логирование
            raise

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
                # Находим запись в RoomParticipant
                participant = session.execute(
                    select(RoomParticipant)
                    .where(RoomParticipant.room_id == room_id)
                    .where(RoomParticipant.user_id == user_id)
                ).scalar_one_or_none()

                if participant:
                    session.delete(participant)
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
                return True
        except SQLAlchemyError as e:
            raise RuntimeError(f'Failed to fetch password of room {room_id}: {e}')

    def are_all_participants_ready(self, room_id: int) -> bool:
        try:
            with Session(self.engine) as session:
                total = session.scalar(
                    select(func.count()).select_from(RoomParticipant)
                    .where(RoomParticipant.room_id == room_id)
                ) or 0
                ready = session.scalar(
                    select(func.count()).select_from(RoomParticipant)
                    .where(RoomParticipant.room_id == room_id)
                    .where(RoomParticipant.is_ready == True)
                ) or 0
                return total >= 2 and total == ready
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error checking readiness in room {room_id}: {e}')

    def deleteRoom(self, room_id):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                session.delete(room)
                session.commit()
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of delete room {room_id}: {e}')

    def update_room(self, room: Room):
        try:
            with Session(self.engine) as session:
                session.merge(room)
                session.commit()
        except SQLAlchemyError as e:
            RuntimeError(f'Error update room: {e}')

    def getParticipants(self, room_id: int):
        try:
            with Session(self.engine) as session:
                room = session.get(Room, room_id)
                if not room:
                    raise ValueError(f"Room {room_id} not found")
                stmt = select(RoomParticipant).where(RoomParticipant.room_id == room_id)
                rp = session.scalars(stmt)
                users = []
                for userrp in rp:
                    user = session.scalar(select(User).where(User.id == userrp.user_id))
                    userresponse = {
                        'id': str(user.id),
                        'username': user.username,
                        'is_ready': userrp.is_ready,
                    }
                    users.append(userresponse)
                return users
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of get participants of room {room_id}: {e}')

    def getRoomByName(self, name: str):
        try:
            with Session(self.engine) as session:
                stmt = select(Room.id).where(Room.name == name)
                return session.scalar(stmt)  # ✅ Возвращает фактический ID
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error fetching room by name {name}: {e}')
        
    def changeReady(self, room_id: int, user_id: int):
        try:
            with Session(self.engine) as session:
                res = select(RoomParticipant).where(RoomParticipant.room_id == room_id and RoomParticipant.user_id == user_id)
                rp = session.scalar(res)
                rp.is_ready = not rp.is_ready
                session.commit()
                session.refresh(rp)
        except SQLAlchemyError as e:
            RuntimeError(f'Error of change read user {user_id} in room {room_id}: {e}')
                                