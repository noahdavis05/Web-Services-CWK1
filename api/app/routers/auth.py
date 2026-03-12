from fastapi import APIRouter, Depends, HTTPException, status
from ..utils.supabase_client import supabase
from .. import schemas
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup", 
    response_model=schemas.SignupResponse,
    responses={
        400: {"description": "Bad Request - Email already registered or password does not meet requirements."},
        422: {"description": "Validation Error - Improperly formatted request body."}
    }
)
def signup(data: schemas.AuthSchema):
    """
    ### Register a new account
    Creates a new user record in the system with a default **'user'** role. 
    
    Once registered, the user can authenticate via the login endpoint to receive a JWT access token.
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
    

@router.post(
    "/login", 
    response_model=schemas.LoginResponse,
    responses={
        401: {"description": "Unauthorized - Invalid email or password credentials."},
        422: {"description": "Validation Error - Improperly formatted request body."}
    }
)
def login(data: schemas.AuthSchema):
    """
    ### Authenticate user
    Verifies user credentials and returns a set of **JWT tokens** for subsequent requests.

    The **access_token** must be provided in the 'Authorization' header as a 'Bearer' token for all protected endpoints. 
    The **refresh_token** is used to obtain a new access token once the current one has expired.
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

