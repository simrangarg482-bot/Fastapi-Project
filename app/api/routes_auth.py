from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import create_token
from app.core.users import authenticate_user

router = APIRouter()


class AuthInput(BaseModel):
    username: str
    password: str


@router.post('/login')
def login(auth: AuthInput):
    user = authenticate_user(auth.username, auth.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_token({'sub': user['username']})
    return {'access_token': token, 'token_type': 'bearer'}