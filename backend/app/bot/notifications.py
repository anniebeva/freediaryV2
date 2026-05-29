"""
Telegram Notifications
"""

import logging
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from app.core.config import settings
from app.database import SessionLocal
from app.crud.user import get_user_by_id

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handles sending Telegram notifications"""
    
    def __init__(self):
        self.token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        self.bot = None
        
        if self.token:
            try:
                from telegram import Bot
                self.bot = Bot(token=self.token)
                logger.info("Telegram notifier initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
    
    async def send_notification(self, chat_id: str, message: str) -> bool:
        """Send a notification to a Telegram chat."""
        if not self.bot or not chat_id:
            return False
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            logger.debug(f"Sent Telegram notification to {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    async def send_login_notification(self, user_id: int) -> bool:
        """Send notification about user login"""
        db = SessionLocal()
        try:
            user = get_user_by_id(db, user_id)
            if not user:
                return False
            
            telegram_id = getattr(user, 'telegram_id', None)
            notifications_enabled = getattr(user, 'telegram_notifications_enabled', False)
            username = getattr(user, 'username', 'Unknown')
            
            if not telegram_id or not notifications_enabled:
                return False
            
            message = f"🔐 Вход в систему\nПользователь: {username}"
            return await self.send_notification(telegram_id, message)
        finally:
            db.close()
    
    async def send_training_created_notification(self, user_id: int, training_type: str, date: str) -> bool:
        """Send notification about training creation"""
        db = SessionLocal()
        try:
            user = get_user_by_id(db, user_id)
            if not user:
                return False
            
            telegram_id = getattr(user, 'telegram_id', None)
            notifications_enabled = getattr(user, 'telegram_notifications_enabled', False)
            username = getattr(user, 'username', 'Unknown')
            
            if not telegram_id or not notifications_enabled:
                return False
            
            message = f"✅ Новая тренировка\nТип: {training_type}\nДата: {date}\nПользователь: {username}"
            return await self.send_notification(telegram_id, message)
        finally:
            db.close()
    
    async def send_training_deleted_notification(self, user_id: int, training_type: str, date: str) -> bool:
        """Send notification about training deletion"""
        db = SessionLocal()
        try:
            user = get_user_by_id(db, user_id)
            if not user:
                return False
            
            telegram_id = getattr(user, 'telegram_id', None)
            notifications_enabled = getattr(user, 'telegram_notifications_enabled', False)
            username = getattr(user, 'username', 'Unknown')
            
            if not telegram_id or not notifications_enabled:
                return False
            
            message = f"🗑️ Удалена тренировка\nТип: {training_type}\nДата: {date}\nПользователь: {username}"
            return await self.send_notification(telegram_id, message)
        finally:
            db.close()



# Создаём глобальный экземпляр
_notifier = None


def get_notifier():
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier()
    return _notifier


def notify_login(user_id: int) -> None:
    """Send login notification"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_notifier().send_login_notification(user_id))
        loop.close()
    except Exception as e:
        logger.error(f"Failed to send login notification: {e}")


def notify_training_created(user_id: int, training_type: str, date: str) -> None:
    """Send training created notification"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_notifier().send_training_created_notification(user_id, training_type, date))
        loop.close()
    except Exception as e:
        logger.error(f"Failed to send training created notification: {e}")


def notify_training_deleted(user_id: int, training_type: str, date: str) -> None:
    """Send training deleted notification"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_notifier().send_training_deleted_notification(user_id, training_type, date))
        loop.close()
    except Exception as e:
        logger.error(f"Failed to send training deleted notification: {e}")


def send_test_notification(chat_id: str) -> None:
    """Send test notification"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_notifier().send_notification(chat_id, "🔔 Тестовое уведомление от FreeDiary!"))
        loop.close()
    except Exception as e:
        logger.error(f"Failed to send test notification: {e}")