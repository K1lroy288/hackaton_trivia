from fastapi import APIRouter, HTTPException, Path
from service.RoomService import RoomService
from pydantic import BaseModel
from typing import Optional
from model.Models import Room, User

router = APIRouter()
room_service = RoomService()

class UserRoomRequest(BaseModel):
    username: str
    userid: int

class RoomCreateRequest(BaseModel):
    name: str
    password: Optional[str]

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

@router.patch("/api/v1/room/{id}")
def controller_change_running(room_id: int):
    try:
        room_service.change_running(room_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/api/v1/room/{room_id}/join")
def controller_add_participant(data: UserRoomRequest, room_data: RoomCreateRequest, room_id: int = Path(..., gt=0)):
    try:
        user = User(
            username=data.username,
            id=data.userid,
        )
        bool_password = room_service.verify_room_password(room_id, room_data.password)
        if bool_password:
            room_service.add_participant(room_id, user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/room", status_code=201)
def controller_create_room(data: RoomCreateRequest):
    try:
        room = Room(name=data.name, password=data.password)
        created_room = room_service.create_room(room)
        return created_room.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/v1/room/{roomname}")
def controller_find_room_by_name(roomname: str = Path(..., regex=r"^[a-zA-Z0-9_-]+$")):
    try:
        room = room_service.find_room_by_name(roomname)
        return room.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/api/v1/room/{room_id}/{user_id}")
def controller_delete_room_by_id(room_id: int, user_id: int):
    try:
        room_service.remove_participant(room_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

