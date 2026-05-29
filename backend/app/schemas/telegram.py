"""
Telegram Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional


class TelegramLinkRequest(BaseModel):
    """Request to generate Telegram link"""
    pass


class TelegramLinkResponse(BaseModel):
    """Response with Telegram link and verification code"""
    code: str = Field(..., description="Verification code for Telegram bot")
    link: str = Field(..., description="Direct link to Telegram bot with code")
    bot_name: str = Field(..., description="Telegram bot username")


class TelegramVerifyRequest(BaseModel):
    """Request to verify Telegram code"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class TelegramVerifyResponse(BaseModel):
    """Response after Telegram verification"""
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Verification result message")
    telegram_id: Optional[str] = Field(None, description="Linked Telegram chat ID")


class TelegramUnlinkResponse(BaseModel):
    """Response after unlinking Telegram"""
    success: bool = Field(..., description="Whether unlinking was successful")
    message: str = Field(..., description="Unlinking result message")


class TelegramTestNotificationRequest(BaseModel):
    """Request to send test notification"""
    pass


class TelegramTestNotificationResponse(BaseModel):
    """Response after sending test notification"""
    success: bool = Field(..., description="Whether notification was sent")
    message: str = Field(..., description="Notification result message")


class TelegramSettingsUpdate(BaseModel):
    """Request to update Telegram notification settings"""
    telegram_notifications_enabled: bool = Field(
        ..., description="Whether Telegram notifications are enabled"
    )