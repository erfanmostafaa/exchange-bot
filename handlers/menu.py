from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove 
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from config import CHANNEL_USERNAME, TRANSFER_TYPES, TRANSFER_REGEX, EXCHANGE_CONDITIONS, ADMIN_USERNAME
import re
from database import get_db
from models.user import Request, User
from datetime import datetime, timedelta


# Conversation states
SELECT_TYPE, SHOW_DETAILS = range(2)

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

async def handle_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to menu command"""
    await show_main_menu(update, context)
    return ConversationHandler.END

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
        transaction_count = db.query(Request).filter(
            Request.user_id == user.id,
            Request.created_at >= three_months_ago
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

async def start_remittance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the remittance process with clear options"""
    context.user_data.clear()
    
    keyboard = [
        ["خرید پی پال", "خرید حواله بانکی", "خرید اسکناس"],
        ["فروش پی پال", "فروش حواله بانکی", "فروش اسکناس"],
        ["بازگشت به منوی اصلی"]
    ]
    await update.message.reply_text(
        "📋 لطفاً نوع حواله مورد نظر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True) )
    return SELECT_TYPE

async def select_remittance_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the selected remittance type with better error handling"""
    user_choice = update.message.text
    
    if user_choice == "بازگشت به منوی اصلی":
        return await cancel_remittance(update, context)
    
    if not any(x in user_choice for x in ["خرید", "فروش"]):
        await update.message.reply_text(
            "⚠️ گزینه نامعتبر. لطفاً از دکمه‌های کیبورد استفاده کنید.",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True))
        return SELECT_TYPE
    
    transaction_type = "خرید" if "خرید" in user_choice else "فروش"
    transfer_type = user_choice.split()[-1]
    
    context.user_data['remittance_data'] = {
        'transaction_type': transaction_type,
        'transfer_type': transfer_type
    }
    
    try:
        remittances = await fetch_remittances(context.bot, transaction_type, transfer_type)
        
        if not remittances:
            await update.message.reply_text(
                f"⚠️ هیچ حواله‌ای برای {user_choice} یافت نشد.",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True))
            return SHOW_DETAILS
        
        message = [f"📋 حواله‌های {user_choice}:"]
        for idx, rem in enumerate(remittances[:5], 1):
            message.append(
                f"{idx}. 🔹 کد: {rem['id']}\n"
                f"   💰 مبلغ: {rem['amount']}\n"
                f"   💵 نرخ: {rem['price']}\n"
                f"   🌍 کشور: {rem['country']}"
            )
        
        keyboard = [[f"نمایش {rem['id']}"] for rem in remittances[:3]]
        keyboard.append(["بروزرسانی", "بازگشت به منوی اصلی"])
        
        await update.message.reply_text(
            "\n".join(message),
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return SHOW_DETAILS
        
    except Exception:
        await update.message.reply_text(
            "⚠️ خطا در دریافت اطلاعات.",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True))
        return SHOW_DETAILS

async def show_remittance_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show details of selected remittance with better navigation"""
    user_input = update.message.text
    
    if user_input == "بروزرسانی":
        return await select_remittance_type(update, context)
    elif user_input == "بازگشت به منوی اصلی":
        return await cancel_remittance(update, context)
    
    if user_input.startswith("نمایش"):
        rem_id = user_input.replace("نمایش", "").strip()
        await display_full_remittance(update, context, rem_id)
    
    return await cancel_remittance(update, context)

async def fetch_remittances(bot, transaction_type, transfer_type):
    """Fetch remittances from channel with improved matching"""
    remittances = []
    pattern = re.compile(TRANSFER_REGEX, re.VERBOSE)
    
    try:
        async for message in bot.get_chat_history(
            chat_id=CHANNEL_USERNAME,
            limit=50
        ):
            if message.text:
                text = message.text.lower()
                if (transaction_type.lower() in text and 
                    TRANSFER_TYPES.get(transfer_type, "").lower() in text):
                    match = pattern.search(message.text)
                    if match:
                        remittance = match.groupdict()
                        remittance['id'] = message.message_id
                        remittances.append(remittance)
    except Exception:
        return []
    
    return remittances

async def display_full_remittance(update: Update, context: ContextTypes.DEFAULT_TYPE, rem_id):
    """Display full remittance details with error handling"""
    try:
        message = await context.bot.get_messages(
            chat_id=CHANNEL_USERNAME,
            message_ids=int(rem_id)
        )
        
        await update.message.reply_text(
            f"📋 جزئیات کامل حواله #{rem_id}:\n\n{message.text}",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception:
        await update.message.reply_text(
            "⚠️ خطا در دریافت جزئیات حواله",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True) )

async def cancel_remittance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel operation and return to main menu"""
    await update.message.reply_text(
        "بازگشت به منوی اصلی...",
        reply_markup=ReplyKeyboardRemove()
    )
    await show_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

def get_remittance_handler():
    """Setup conversation handler for remittances with improved fallbacks"""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^📋 نمایش لیست حواله‌ها$'), start_remittance)],
        states={
            SELECT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_remittance_type)],
            SHOW_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_remittance_detail)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_remittance),
            MessageHandler(filters.Regex(r'^(بازگشت|بازگشت به منوی اصلی|انصراف)$'), cancel_remittance)],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END
        }
    )