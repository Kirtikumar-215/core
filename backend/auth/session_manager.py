from fastapi import Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets

from database.session import get_db
from models.user import Session as DBSession, User

SESSION_COOKIE_NAME = "session_id"
SESSION_EXPIRE_HOURS = 24

def create_user_session(db: Session, user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRE_HOURS)
    
    db_session = DBSession(
        id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return session_id

def set_session_cookie(response: Response, session_id: str):
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=False, # Set False for local dev (HTTP), we can make it environmental but for this specific local setup False is better.
        samesite="lax",
        max_age=SESSION_EXPIRE_HOURS * 3600
    )

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Verify session in DB
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    
    # Check expiration
    if db_session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db.delete(db_session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    
    user = db.query(User).filter(User.id == db_session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
        
    return user
