from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from service.AuthenticationService import AuthenticationService
from model.Models import User

router = APIRouter()
auth_service = AuthenticationService()

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/api/v1/trivia/register", status_code=201)
def controller_register(data: RegisterRequest):
    try:
        user = User()
        user.username = data.username
        user.password = data.password
        registered_user = auth_service.register(user)
        return registered_user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/trivia/login")
def controller_login(data: LoginRequest):
    try:
        user = User()
        user.username = data.username
        user.password = data.password
        logged_user = auth_service.login(user)
        return logged_user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
