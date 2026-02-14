from fastapi import APIRouter, Depends, HTTPException, status
from ..utils.supabase_client import supabase
from .. import schemas
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/signup")
def signup(data: schemas.AuthSchema):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "role": "user"  # default to user
                }
            }
        })
        return {"message": "User created", "id": response.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/login")
def login(data: schemas.AuthSchema):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

