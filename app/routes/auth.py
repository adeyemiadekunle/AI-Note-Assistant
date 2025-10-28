from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user_model import TokenResponse, UserCreate, UserLogin, UserPublic
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate) -> TokenResponse:
    try:
        token, user = await auth_service.register_user(payload)
    except auth_service.UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except auth_service.AuthConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return auth_service.token_response(token, user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin) -> TokenResponse:
    try:
        token, user = await auth_service.authenticate_user(payload)
    except auth_service.InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except auth_service.AuthConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return auth_service.token_response(token, user)


@router.get("/me", response_model=UserPublic)
async def read_profile(current_user: UserPublic = Depends(auth_service.get_current_user)) -> UserPublic:
    return current_user
