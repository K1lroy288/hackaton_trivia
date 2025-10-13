from repository.RoomRepository import RoomRepository

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
            raise RuntimeError(f'Room {room_id} not found')
        return room
