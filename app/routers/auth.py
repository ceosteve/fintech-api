from fastapi import APIRouter, status


router = APIRouter(
    tags=["login"]
)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=)
