from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user

router = APIRouter(prefix="/protected", tags=["Protected"])


@router.get("/profile", status_code=status.HTTP_200_OK)
def get_user_profile(current_user=Depends(get_current_user)):
    user_dict = {}
    if hasattr(current_user, "__dict__"):
        user_dict = {
            "id": getattr(current_user, "id", None),
            "email": getattr(current_user, "email", None),
            "created_at": str(getattr(current_user, "created_at", None)),
            "app_metadata": getattr(current_user, "app_metadata", {}),
            "user_metadata": getattr(current_user, "user_metadata", {}),
        }
    elif isinstance(current_user, dict):
        user_dict = current_user
    else:
        user_dict = {"user": str(current_user)}

    return user_dict


@router.get("/dashboard", status_code=status.HTTP_200_OK)
def get_user_dashboard(current_user=Depends(get_current_user)):
    email = (
        current_user.email
        if hasattr(current_user, "email")
        else current_user.get("email", "User")
    )
    return {
        "message": f"Welcome to your private dashboard, {email}!",
        "status": "authenticated",
    }
