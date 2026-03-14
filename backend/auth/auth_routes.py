from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database.session import get_db
from models.user import User, Session as DBSession, OTPRequest
from schemas.user import (
    UserCreate, UserResponse, LoginRequest, 
    GoogleAuthRequest, SendOTPRequest, VerifyOTPRequest, ResetPasswordRequest
)
from auth.password_service import get_password_hash, verify_password
from auth.session_manager import create_user_session, set_session_cookie, get_current_user, SESSION_COOKIE_NAME
from auth.google_oauth import verify_google_token
from auth.otp_service import create_and_send_otp

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=get_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == login_data.email).first()
    if not db_user or not db_user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not verify_password(login_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    session_id = create_user_session(db, db_user.id)
    set_session_cookie(response, session_id)
    
    return {"success": True, "message": "Login successful", "data": {"id": db_user.id, "email": db_user.email, "role": db_user.role}}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        db.query(DBSession).filter(DBSession.id == session_id).delete()
        db.commit()
    
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"success": True, "message": "Logged out successfully", "data": {}}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/google")
async def google_auth(request_data: GoogleAuthRequest, response: Response, db: Session = Depends(get_db)):
    google_user = await verify_google_token(request_data.token)
    email = google_user.get("email")
    name = google_user.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Google token did not contain email")

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        db_user = User(name=name or "Google User", email=email, role="Warehouse Staff", hashed_password=None)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    session_id = create_user_session(db, db_user.id)
    set_session_cookie(response, session_id)
    
    return {"success": True, "message": "Google authentication successful", "data": {"id": db_user.id, "email": db_user.email}}

@router.post("/send-otp")
async def send_otp(request_data: SendOTPRequest, db: Session = Depends(get_db)):
    await create_and_send_otp(db, request_data.phone_number)
    return {"success": True, "message": "OTP sent successfully", "data": {}}

@router.post("/verify-otp")
def verify_otp(request_data: VerifyOTPRequest, db: Session = Depends(get_db)):
    otp_record = db.query(OTPRequest).filter(
        OTPRequest.phone_number == request_data.phone_number,
        OTPRequest.is_used == False
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="No active OTP found for this number")
    if otp_record.attempts >= 3:
        raise HTTPException(status_code=400, detail="Maximum OTP attempts exceeded. Request a new OTP.")
    if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")
    if otp_record.otp_code != request_data.otp_code:
        otp_record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    return {"success": True, "message": "OTP verified successfully. You can now reset your password.", "data": {}}

@router.post("/reset-password")
def reset_password(request_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    otp_record = db.query(OTPRequest).filter(
        OTPRequest.phone_number == request_data.phone_number,
        OTPRequest.otp_code == request_data.otp_code,
        OTPRequest.is_used == False
    ).first()
    
    if not otp_record or otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    otp_record.is_used = True
    user = db.query(User).filter(User.phone_number == request_data.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = get_password_hash(request_data.new_password)
    db.query(DBSession).filter(DBSession.user_id == user.id).delete() # Force logout
    db.commit()
    
    return {"success": True, "message": "Password reset successfully", "data": {}}
