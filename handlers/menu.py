from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from config import CHANNEL_USERNAME, TRANSFER_TYPES, TRANSFER_REGEX, EXCHANGE_CONDITIONS, ADMIN_USERNAME
import re
from database import get_db
from models.tables import Remittance, User
from datetime import datetime, timedelta


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu with proper keyboard layout"""
    keyboard = [
        ["📝 ثبت درخواست جدید", "📋 نمایش لیست حواله‌ها"],
        ["✏️ تغییر نام", "ℹ️ اطلاعات کاربری"],
        ["📞 پشتیبانی", "شرایط تبادل ارز"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "🏠 منوی اصلی:",
        reply_markup=reply_markup
    )


async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support request with proper markup"""
    await update.message.reply_text(
        text=f"📞 برای ارتباط با پشتیبانی لطفاً به آیدی زیر پیام دهید:\n@{ADMIN_USERNAME}",
        reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
    )
    return ConversationHandler.END


async def exchange_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show exchange conditions with proper HTML formatting"""
    await update.message.reply_text(
        text=EXCHANGE_CONDITIONS,
        reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True),
        parse_mode='HTML'
    )
    return ConversationHandler.END


async def user_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user information"""
    try:
        user = update.effective_user
        db = next(get_db())
        
        # دریافت اطلاعات کاربر از دیتابیس
        user_data = db.query(User).filter(User.user_id == user.id).first()
        
        if not user_data:
            await update.message.reply_text(
                "⚠️ اطلاعات کاربر یافت نشد. لطفاً ابتدا ثبت‌نام کنید.",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
            )
            return ConversationHandler.END
        
        # محاسبه تعداد تراکنش‌های 3 ماه اخیر
        three_months_ago = datetime.now() - timedelta(days=90)
        transaction_count = db.query(Remittance).filter(
            Remittance.user_id == user.id,
            Remittance.created_at >= three_months_ago
        ).count()
        
        # آماده‌سازی پیام اطلاعات کاربر
        message = (
            "ℹ️ اطلاعات کاربری:\n\n"
            f"👤 نام: {user_data.name}\n"
            f"🆔 شماره ملی: {user_data.national_number}\n"
            f"📞 تلفن: {user_data.phone}\n"
            f"🔢 تعداد تراکنش‌ها (3 ماه اخیر): {transaction_count}"
        )
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
        )
        
    except Exception as e:
        print(f"Error in user_info_handler: {e}")
        await update.message.reply_text(
            "⚠️ خطا در دریافت اطلاعات کاربری. لطفاً بعداً تلاش کنید.",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
        )
    
    return ConversationHandler.END
