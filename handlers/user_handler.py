from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

# حالت‌های گفتگو
GET_NAME, GET_NATIONAL_NUMBER, GET_PHONE, CHANGE_NAME = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation for new users"""
    user_id = update.effective_user.id
    db: Session = next(get_db())

    user = db.query(User).filter(User.user_id == user_id).first()

    if user:
        await update.message.reply_text(
            "شما قبلاً ثبت‌نام کرده‌اید!",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👋 به ربات تبادل ارز خوش آمدید!\nلطفاً نام و نام خانوادگی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's name"""
    user_name = update.message.text.strip()
    
    if len(user_name) < 3:
        await update.message.reply_text("❌ نام باید حداقل ۳ کاراکتر باشد. لطفاً مجدداً وارد کنید:")
        return GET_NAME

    context.user_data["name"] = user_name
    await update.message.reply_text(
        "لطفاً شماره ملی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_NATIONAL_NUMBER

async def get_national_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's national number"""
    national_number = update.message.text.strip()
    
    if not national_number.isdigit() or len(national_number) != 10:
        await update.message.reply_text(
            "❌ شماره ملی نامعتبر است. لطفاً یک شماره ملی 10 رقمی وارد کنید:",
            reply_markup=ReplyKeyboardRemove()
        )
        return GET_NATIONAL_NUMBER
    
    context.user_data["national_number"] = national_number
    await update.message.reply_text(
        "لطفاً شماره تلفن خود را دقیقاً همانطور که در تلگرام ثبت کرده‌اید وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's phone number (exactly as in Telegram)"""
    phone_number = update.message.text.strip()
    
    # حداقل اعتبارسنجی
    if not phone_number or len(phone_number) < 5:
        await update.message.reply_text(
            "❌ شماره تلفن نامعتبر است. لطفاً شماره تلفن خود را دقیقاً همانطور که در تلگرام ثبت کرده‌اید وارد کنید:",
            reply_markup=ReplyKeyboardRemove()
        )
        return GET_PHONE

    user_id = update.effective_user.id
    name = context.user_data["name"]
    national_number = context.user_data["national_number"]

    db: Session = next(get_db())

    try:
        # بررسی تکراری نبودن شماره
        if db.query(User).filter(User.phone == phone_number).first():
            await update.message.reply_text(
                "❌ این شماره تلفن قبلاً ثبت شده است.",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
            )
            return ConversationHandler.END

        user = User(
            user_id=user_id,
            name=name,
            national_number=national_number,
            phone=phone_number
        )
        db.add(user)
        db.commit()
        
        await update.message.reply_text(
            f"✅ ثبت‌نام با موفقیت انجام شد!\n\n"
            f"👤 نام: {name}\n"
            f"🆔 شماره ملی: {national_number}\n"
            f"📱 تلفن: {phone_number}",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
        )
        
    except Exception as e:
        db.rollback()
        await update.message.reply_text(
            "❌ خطا در ثبت اطلاعات! لطفاً مجدداً تلاش کنید.",
            reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
        )
    finally:
        context.user_data.clear()
        return ConversationHandler.END

async def change_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start name change process"""
    await update.message.reply_text(
        "✏️ لطفاً نام جدید خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    return CHANGE_NAME

async def change_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    await update.message.reply_text(
        "❌ عملیات لغو شد.",
        reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

def get_user_conversation_handler():
    """Get user registration conversation handler"""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_NATIONAL_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_national_number)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

def get_change_name_handler():
    """Get name change handler"""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✏️ تغییر نام$"), change_name_start)],
        states={
            CHANGE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )