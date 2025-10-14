from repository.RoomRepository import RoomRepository
from model.Models import Room
from webSocketManager import manager
from service.QuestionService import QuestionService

class RoomService:
    room_repository: RoomRepository
    def __init__(self):
        self.room_repository = RoomRepository()

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

    def add_participant(self, room_id: int, user_id: int, room_pass: str):
        if self.verify_room_password(room_id, room_pass):
            self.room_repository.addParticipant(room_id, user_id)

    def create_room(self, room: Room):
        new_room = self.room_repository.createRoom(room)
        return new_room

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