from fastapi import APIRouter, Depends
from google.cloud.firestore import SERVER_TIMESTAMP

from biteswipe_api.auth import get_current_user
from biteswipe_api.firebase import get_db
from biteswipe_api.schemas.User import UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(get_current_user), db=Depends(get_db)):
    ref = db.collection("users").document(user["uid"])
    snap = ref.get()
    if not snap.exists:  # first login creates the profile
        ref.set({
            "email": user.get("email"),
            "displayName": user.get("name"),
            "createdAt": SERVER_TIMESTAMP,
        })
        snap = ref.get()
    data = snap.to_dict()
    return UserResponse(uid=user["uid"], email=data.get("email"), displayName=data.get("displayName"))