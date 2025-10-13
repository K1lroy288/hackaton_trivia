# controller/room_controller.py
from fastapi import APIRouter, HTTPException
from service.RoomService import RoomService

router = APIRouter()
room_service = RoomService()

@router.get("/api/v1/room")
def controller_get_all_rooms():
    try:
        rooms = room_service.get_all_rooms()
        return [room.to_dict() for room in rooms]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))