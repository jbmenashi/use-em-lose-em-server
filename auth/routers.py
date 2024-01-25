from auth.schemas import UserCreate, UserRead, UserUpdate
from auth.users import auth_backend, fastapi_users
from fastapi import APIRouter

def get_users_router(app):
    users_router = APIRouter()

    users_router.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
    )
    users_router.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    users_router.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    users_router.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    users_router.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )


    return users_router