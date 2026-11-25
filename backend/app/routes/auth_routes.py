from fastapi import APIRouter, HTTPException, status

from app.schemas import UserSignup, UserLogin, UserResponse, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token

router = APIRouter()

users = {}
next_user_id = 1


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(user: UserSignup):
    global next_user_id

    if user.email in users:
        raise HTTPException(
            status_code=400,
            detail="Email is already registered"
        )

    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
        "hashed_password": hash_password(user.password)
    }

    users[user.email] = new_user
    next_user_id += 1

    return {
        "id": new_user["id"],
        "name": new_user["name"],
        "email": new_user["email"]
    }


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    existing_user = users.get(user.email)

    if not existing_user or not verify_password(
        user.password,
        existing_user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token({
        "sub": str(existing_user["id"]),
        "email": existing_user["email"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }