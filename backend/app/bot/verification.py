"""
Telegram Verification Logic
"""

import secrets
import string
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, Dict
from app.models.models import User
from app.crud.user import update_user_telegram_id

logger = logging.getLogger(__name__)


class TelegramVerification:
    """Handles Telegram verification codes"""
    
    def __init__(self):
        self.verification_codes: Dict[str, dict] = {}  # code -> {user_id, expires_at}
        self.code_length = 6
        self.code_expiry_minutes = 10
    
    def generate_verification_code(self, user_id: int) -> str:
        """Generate a unique verification code for a user"""
        # Generate random alphanumeric code
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(self.code_length))
        
        # Store code with expiry
        expires_at = datetime.now() + timedelta(minutes=self.code_expiry_minutes)
        self.verification_codes[code] = {
            'user_id': user_id,
            'expires_at': expires_at
        }
        
        logger.debug(f"Generated verification code {code} for user {user_id}")
        return code
    
    def verify_code(self, code: str, chat_id: int) -> Optional[int]:
        """
        Verify a Telegram verification code.
        Returns user_id if verification successful, None otherwise.
        """
        if code not in self.verification_codes:
            logger.warning(f"Verification code not found: {code}")
            return None
        
        code_data = self.verification_codes[code]
        
        # Check if code has expired
        if datetime.now() > code_data['expires_at']:
            logger.warning(f"Verification code expired: {code}")
            del self.verification_codes[code]
            return None
        
        user_id = code_data['user_id']
        
        # Remove used code
        del self.verification_codes[code]
        
        logger.info(f"Verification successful for user {user_id}, chat_id {chat_id}")
        return user_id
    
    def cleanup_expired_codes(self):
        """Clean up expired verification codes"""
        now = datetime.now()
        expired_codes = [
            code for code, data in self.verification_codes.items()
            if now > data['expires_at']
        ]
        
        for code in expired_codes:
            del self.verification_codes[code]
        
        if expired_codes:
            logger.debug(f"Cleaned up {len(expired_codes)} expired verification codes")


# Global instance
verification = TelegramVerification()


def generate_telegram_code(user_id: int) -> str:
    """Generate a verification code for Telegram linking"""
    return verification.generate_verification_code(user_id)


def verify_telegram_code(db: Session, code: str, chat_id: int) -> Optional[User]:
    """
    Verify Telegram code and link chat_id to user.
    Returns the updated user if successful, None otherwise.
    """
    user_id = verification.verify_code(code, chat_id)
    if not user_id:
        return None
    
    # Update user's telegram_id
    user = update_user_telegram_id(db, user_id, str(chat_id))
    if user:
        logger.info(f"Linked Telegram chat_id {chat_id} to user {user_id}")
    
    return user


def get_telegram_link(bot_name: str, code: str) -> str:
    """Generate Telegram link for verification"""
    return f"https://t.me/{bot_name}?start={code}"