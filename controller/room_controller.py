from fastapi import APIRouter, HTTPException, Path
from service.RoomService import RoomService
from pydantic import BaseModel
from typing import Optional
from model.Models import Room, User
from fastapi import WebSocket, WebSocketDisconnect
from webSocketManager.manager import manager
from service.GameService import GameService
from fastapi import BackgroundTasks

router = APIRouter()
room_service = RoomService()
game_service = GameService()


class JoinRequest(BaseModel):
    userid: int
    room_password: str


class RoomCreateRequest(BaseModel):
    name: str
    user_id: int
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
def controller_add_participant(data: JoinRequest, room_id: int = Path(..., gt=0)):
    try:
        return room_service.verify_room_password(room_id, data.userid, data.room_password)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/v1/room", status_code=201)
def controller_create_room(data: RoomCreateRequest):
    try:
        print(f"API: Creating room '{data.name}' for user {data.user_id}")

        # ВАЖНО: Проверим существование пользователя перед созданием комнаты
        user = room_service.user_repository.findById(data.user_id)
        if not user:
            raise ValueError(f"User with ID {data.user_id} does not exist")

        # Создаем комнату
        room = Room(name=data.name, password=data.password)
        created_room = room_service.create_room(room)

        # Добавляем создателя в комнату
        room_service.add_participant(created_room.id, data.user_id, data.password, True)

        print(f"API: Room '{data.name}' created successfully with ID {created_room.id}")
        return created_room.to_dict()

    except ValueError as e:
        print(f"API: ValueError - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        print(f"API: RuntimeError - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"API: Unexpected error - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
def controller_delete_user_by_id(room_id: int, user_id: int):
    try:
        room_service.remove_participant(room_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/api/v1/room/{room_id}")
def controller_delete_room_by_id(room_id: int):
    try:
        room_service.delete_room(room_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.websocket("/ws/room/{room_id}")
async def web_soсket_room(websocket: WebSocket, room_id: int):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast_to_room(room_id, {
                "type": "answer",
                "user_id": data.get("user_id"),
                "answer": data.get("answer")
            })
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)


@router.post("/api/v1/room/{room_id}/start")
async def start_game(room_id: int):
    import asyncio
    asyncio.create_task(game_service.start_game(room_id))
    return {"status": "game started"}


@router.get("/api/v1/room/{room_id}/participants")
def controller_get_count_participants(room_id: int):
    try:
        users = room_service.getCountParticipants(room_id)
        return users
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
