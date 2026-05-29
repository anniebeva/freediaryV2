"""
Telegram Routes
"""
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.models import User
from app.schemas.telegram import (
    TelegramLinkResponse, TelegramVerifyResponse,
    TelegramUnlinkResponse, TelegramTestNotificationResponse, TelegramSettingsUpdate
)
from app.bot.verification import generate_telegram_code, get_telegram_link
from app.bot.notifications import send_test_notification
from app.crud.user import (
    unlink_user_telegram, update_telegram_notifications
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/me/telegram", tags=["telegram"])


@router.post("/link", response_model=TelegramLinkResponse)
async def generate_telegram_verification_link(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> TelegramLinkResponse:
    try:
        user_id = getattr(current_user, 'id', 0)
        code = generate_telegram_code(user_id)
        bot_name = getattr(settings, "TELEGRAM_BOT_NAME", "FreeDiaryBot")
        link = get_telegram_link(bot_name, code)
        
        return TelegramLinkResponse(code=code, link=link, bot_name=bot_name)
    except Exception as e:
        logger.error(f"Error generating Telegram link: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Telegram verification link")


@router.post("/verify", response_model=TelegramVerifyResponse)
async def verify_telegram_code(
    current_user: Annotated[User, Depends(get_current_user)]
) -> TelegramVerifyResponse:
    telegram_id = getattr(current_user, 'telegram_id', None)
    return TelegramVerifyResponse(
        success=True,
        message="Verification endpoint - called by Telegram bot",
        telegram_id=telegram_id
    )


@router.delete("/unlink", response_model=TelegramUnlinkResponse)
async def unlink_telegram(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> TelegramUnlinkResponse:
    try:
        user_id = getattr(current_user, 'id', 0)
        user = unlink_user_telegram(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return TelegramUnlinkResponse(
            success=True,
            message="Telegram successfully unlinked from your account"
        )
    except Exception as e:
        logger.error(f"Error unlinking Telegram: {e}")
        raise HTTPException(status_code=500, detail="Failed to unlink Telegram")


@router.post("/test", response_model=TelegramTestNotificationResponse)
async def send_test_notification_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    background_tasks: BackgroundTasks
) -> TelegramTestNotificationResponse:
    telegram_id = getattr(current_user, 'telegram_id', None)
    notifications_enabled = getattr(current_user, 'telegram_notifications_enabled', False)
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Telegram is not linked to your account")
    
    if not notifications_enabled:
        raise HTTPException(status_code=400, detail="Telegram notifications are disabled for your account")
    
    try:
        background_tasks.add_task(send_test_notification, telegram_id)
        return TelegramTestNotificationResponse(
            success=True,
            message="Test notification sent to your Telegram"
        )
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")


@router.get("/status")
async def get_telegram_status(
    current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    telegram_id = getattr(current_user, 'telegram_id', None)
    notifications_enabled = getattr(current_user, 'telegram_notifications_enabled', False)
    
    return {
        "telegram_linked": telegram_id is not None,
        "telegram_id": telegram_id,
        "telegram_notifications_enabled": notifications_enabled
    }


@router.put("/settings")
async def update_telegram_settings(
    settings_update: TelegramSettingsUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    telegram_id = getattr(current_user, 'telegram_id', None)
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Telegram is not linked to your account")
    
    try:
        user_id = getattr(current_user, 'id', 0)
        user = update_telegram_notifications(db, user_id, settings_update.telegram_notifications_enabled)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "message": "Telegram notification settings updated",
            "telegram_notifications_enabled": getattr(user, 'telegram_notifications_enabled', False)
        }
    except Exception as e:
        logger.error(f"Error updating Telegram settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update Telegram settings")