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

@router.get('/api/v1/room/{room_id}')
def controller_get_room_by_id(room_id: int):
    try:
        room = room_service.get_room_by_id(room_id)
        return room.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
