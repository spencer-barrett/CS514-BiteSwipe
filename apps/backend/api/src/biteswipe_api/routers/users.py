from fastapi import APIRouter

from biteswipe_api.dependencies import CurrentUser
from biteswipe_api.schemas.user import UserResponse

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/me")
def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)