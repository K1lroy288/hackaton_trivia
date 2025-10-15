from repository.RoomRepository import RoomRepository
from repository.UserRepository import UserRepository
from model.Models import Room
from webSocketManager import manager
from service.QuestionService import QuestionService
import bcrypt


class RoomService:
    room_repository: RoomRepository

    def __init__(self):
        self.room_repository = RoomRepository()
        self.user_repository = UserRepository()

    def get_all_rooms(self):
        rooms = self.room_repository.findAll()
        return rooms

    def get_room_by_id(self, room_id: int):
        room = self.room_repository.findById(room_id)
        if room is None:
            raise ValueError(f'Room {room_id} not found')
        return room

    def change_running(self, room_id: int):
        self.room_repository.changeRunning(room_id)

    def add_participant(self, room_id: int, user_id: int, room_pass: str = None, creator: bool = False):
        try:
            print(f"Adding participant: room_id={room_id}, user_id={user_id}, creator={creator}")  # Логирование

            # Получаем комнату по ID
            room = self.room_repository.findById(room_id)
            if not room:
                raise ValueError(f"Room with ID {room_id} not found")

            # Проверяем пароль если требуется (для не-создателей)
            if not creator and room.password:
                print(f"Room requires password verification")  # Логирование
                if not self.verify_room_password(room_id, room_pass):
                    raise ValueError("Invalid room password")

            # Добавляем участника
            self.room_repository.addParticipant(room_id, user_id)
            print(f"Participant {user_id} added to room {room_id}")  # Логирование

        except Exception as e:
            print(f"Error in add_participant: {str(e)}")  # Логирование
            raise

    def create_room(self, room: Room):
        try:
            print(f"Creating room: {room.name}")  # Логирование
            if room.password != None:
                password_bytes = room.password.encode('utf-8')
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password_bytes, salt)
                room.password = hashed_password.decode('utf-8')
            new_room = self.room_repository.createRoom(room)
            print(f"Room created with ID: {new_room.id}")  # Логирование
            return new_room
        except Exception as e:
            print(f"Error in create_room: {str(e)}")  # Логирование
            raise

    def find_room_by_name(self, room_name: str):
        room = self.room_repository.findByRoomname(room_name)
        if room is None:
            raise ValueError(f'Room {room_name} not found')
        return room

    def remove_participant(self, room_id: int, user_id: int):
        self.room_repository.removeParticipant(room_id, user_id)

    def verify_room_password(self, room_id: int, room_password: str):
        bool_password = self.room_repository.verify_room_password(room_id, room_password)
        if bool_password:
            return bool_password
        else:
            return bool_password

    def delete_room(self, room_id: int):
        self.room_repository.deleteRoom(room_id)

    def getCountParticipants(self, room_id: int):
        users = self.room_repository.getParticipants(room_id)
        return users
    
    def changeready(self, room_id: int, user_id: int):
        self.room_repository.changeReady(room_id, user_id)
