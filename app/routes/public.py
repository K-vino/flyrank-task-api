from fastapi import APIRouter, status

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/info", status_code=status.HTTP_200_OK)
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}
