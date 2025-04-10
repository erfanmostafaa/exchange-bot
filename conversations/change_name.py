from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from sqlalchemy.orm import Session
from database import get_db
from models.tables import User

# حالت‌های گفتگو
CHANGE_NAME = range(1)

class ChangeNameConvarsation:

    async def change_name_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start name change process"""
        await update.message.reply_text("✏️ لطفاً نام جدید خود را وارد کنید:")
        return CHANGE_NAME

    async def change_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Change user's name"""
        new_name = update.message.text.strip()
        
        if len(new_name) < 3:
            await update.message.reply_text("❌ نام باید حداقل ۳ کاراکتر باشد. لطفاً مجدداً وارد کنید:")
            return CHANGE_NAME

        user_id = update.effective_user.id
        db: Session = next(get_db())
        
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if user:
                user.name = new_name
                db.commit()
                await update.message.reply_text(
                    f"✅ نام شما با موفقیت به {new_name} تغییر یافت.",
                    reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
                )
            else:
                await update.message.reply_text(
                    "❌ کاربر یافت نشد! لطفاً ابتدا ثبت‌نام کنید.",
                    reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
                )
        except():
            await update.message.reply_text(
                "❌ خطا در تغییر نام! لطفاً مجدداً تلاش کنید.",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
            )
        finally:
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current operation"""
        await update.message.reply_text(
            "❌ عملیات لغو شد.",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
        )
        context.user_data.clear()
        return ConversationHandler.END

    def get_change_name_handler(self):
        """Get name change handler"""
        return ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^✏️ تغییر نام$"), self.change_name_start)],
            states={
                CHANGE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.change_name)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
