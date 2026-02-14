from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .supabase_client import supabase

security = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        response = supabase.auth.get_user(token.credentials)
        if not response.user:
            raise HTTPException(status_code = 401, details="Invalid User")
        return response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_user_role(allowed_roles: list[str]):
    def role_checker(user = Depends(get_current_user)):
        # Extract the role from user_metadata
        user_role = user.user_metadata.get("role")
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="User has no role assigned"
            )
            
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Role '{user_role}' is not authorized to access this resource"
            )
        
        return user
    return role_checker