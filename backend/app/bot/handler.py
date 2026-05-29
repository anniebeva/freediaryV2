import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.core.config import settings
from app.database import SessionLocal
from .verification import verify_telegram_code

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    """Handler for Telegram bot operations"""
    
    def __init__(self):
        self.token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        self.application: Optional[Application] = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update or not update.message or not update.effective_chat:
            logger.warning("Invalid update object")
            return
        
        message = (
            "👋 Привет! Я бот для уведомлений FreeDiary.\n\n"
            "Для привязки аккаунта:\n"
            "1. Откройте профиль в приложении FreeDiary\n"
            "2. Нажмите 'Привязать Telegram'\n"
            "3. Используйте полученный код: /verify <код>\n\n"
            "Пример: /verify 12345"
        )
        await update.message.reply_text(message)
    
    async def verify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /verify command with code"""
        if not update or not update.message or not update.effective_chat:
            logger.warning("Invalid update object")
            return
        
        try:
            if not context.args:
                await update.message.reply_text("❌ Пожалуйста, укажите код: /verify <код>")
                return
            
            code = context.args[0]
            chat_id = update.effective_chat.id
            
            # Verify the code
            db = SessionLocal()
            try:
                user = verify_telegram_code(db, code, chat_id)
                if user:
                    await update.message.reply_text(
                        "✅ Аккаунт успешно привязан!\n"
                        "Теперь вы будете получать уведомления о тренировках."
                    )
                else:
                    await update.message.reply_text(
                        "❌ Неверный или просроченный код.\n"
                        "Пожалуйста, получите новый код в приложении."
                    )
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error verifying Telegram code: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not update or not update.message:
            return
        
        help_text = (
            "📋 Доступные команды:\n"
            "/start - Начало работы\n"
            "/verify <код> - Привязать аккаунт\n"
            "/help - Показать это сообщение\n\n"
            "Для отключения уведомлений используйте приложение FreeDiary."
        )
        await update.message.reply_text(help_text)
    
    def setup_handlers(self, application: Application):
        """Setup command handlers"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("verify", self.verify))
        application.add_handler(CommandHandler("help", self.help_command))
    
    async def start_bot(self):
        """Start the Telegram bot"""
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN not set, Telegram bot disabled")
            return
        
        try:
            self.application = Application.builder().token(self.token).build()
            self.setup_handlers(self.application)
            
            logger.info("Starting Telegram bot...")
            await self.application.initialize()
            await self.application.start()
            
            # Проверяем, что updater существует
            if self.application.updater:
                await self.application.updater.start_polling()
            else:
                logger.error("Updater not available")
                return
                
            logger.info("Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.application:
            if self.application.updater:
                await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")