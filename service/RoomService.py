from repository.RoomRepository import RoomRepository

class RoomService:
    room_repository: RoomRepository
    def __init__(self):
        self.room_repository = RoomRepository()

    def get_all_rooms(self):
        rooms = self.room_repository.findAll()
        return rooms