from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.auth import LoginSchema, RegisterSchema
from app.db.user_queries import get_user_by_email, create_user
from app.core.security import verify_password, hash_password, create_access_token
from app.core.logging import log_security_event

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register(payload: RegisterSchema, request: Request):
    existing = get_user_by_email(payload.email)
    if existing:
        # Generic error — don't confirm whether email exists (A07)
        raise HTTPException(status_code=400, detail="Registration failed")

    hashed = hash_password(payload.password)
    user = create_user(payload.email, hashed, payload.full_name)
    log_security_event("USER_REGISTERED", user_id=str(user["id"]))
    return {"message": "Account created successfully"}


@router.post("/login")
@limiter.limit("5/minute")  # Brute-force protection (A07)
async def login(payload: LoginSchema, request: Request):
    user = get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        log_security_event("FAILED_LOGIN", details={"email": payload.email})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",  # Generic — never reveal which field is wrong
        )
    token = create_access_token(subject=str(user["id"]))
    log_security_event("SUCCESSFUL_LOGIN", user_id=str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}
