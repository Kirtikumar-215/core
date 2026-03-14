import os
import httpx
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.user import OTPRequest, User
from fastapi import HTTPException

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")

async def send_otp_via_fast2sms(phone_number: str, otp_code: str):
    """Sends OTP via Fast2SMS API"""
    if FAST2SMS_API_KEY and FAST2SMS_API_KEY != "REPLACE_WITH_FAST2SMS_API_KEY":
        url = "https://www.fast2sms.com/dev/bulkV2"
        querystring = {
            "authorization": FAST2SMS_API_KEY, 
            "route": "otp", 
            "variables_values": otp_code, 
            "numbers": phone_number
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=querystring)
            if response.status_code != 200:
                print(f"Fast2SMS Error: {response.text}")
    else:
        # Development mode fallback (prints to console)
        print(f"DEVELOPMENT MODE: OTP for {phone_number} is {otp_code}")

async def create_and_send_otp(db: Session, phone_number: str):
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this phone number not found")
        
    otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    # Clean up old requests
    db.query(OTPRequest).filter(OTPRequest.phone_number == phone_number).delete()
    
    otp_request = OTPRequest(
        phone_number=phone_number,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp_request)
    db.commit()
    
    await send_otp_via_fast2sms(phone_number, otp_code)
