from fastapi import APIRouter, Depends, HTTPException, status
from ..utils.supabase_client import supabase
from .. import schemas
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/signup", response_model=schemas.SignupResponse)
def signup(data: schemas.AuthSchema):
    """
    ### Register a new account
    Creates a new user record in Supabase with a default 'user' role.

    **Args:**
    - **data**: Schema containing the user's email and password.

    **Returns:**
    - A success message and the unique Supabase user ID.

    **Errors:**
    - **400**: If the email is already registered or the password does not meet requirements.
    """
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
    

@router.post("/login", response_model=schemas.LoginResponse)
def login(data: schemas.AuthSchema):
    """
    ### Authenticate user
    Verifies credentials and returns a set of JWT tokens for subsequent requests.

    **Args:**
    - **data**: Schema containing the user's email and password.

    **Returns:**
    - **access_token**: The Bearer token used for authorization headers.
    - **refresh_token**: Used to obtain a new access token when it expires.
    - **token_type**: Always returns 'bearer'.

    **Errors:**
    - **401**: If the email or password credentials are incorrect.
    """
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

