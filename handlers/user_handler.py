from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session
from database import get_db
from models.user import User  

GET_NAME, GET_NATIONAL_NUMBER, GET_PHONE = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db: Session = next(get_db())

    user = db.query(User).filter(User.user_id == user_id).first()

    if user:
        await update.message.reply_text(
            f"نام شما {user.name} است. اگر می‌خواهید نام خود را تغییر دهید، نام صحیح خود را وارد کنید."
        )
    else:
        await update.message.reply_text("لطفاً نام و نام خانوادگی خود را وارد کنید.")

    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data["name"] = user_name

    await update.message.reply_text("لطفاً شماره ملی خود را وارد کنید.")
    return GET_NATIONAL_NUMBER

async def get_national_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    national_number = update.message.text
    context.user_data["nationalnumber"] = national_number

    await update.message.reply_text("لطفاً شماره تلفن خود را وارد کنید.")
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone_number = update.message.text
    name = context.user_data["name"]
    national_number = context.user_data["nationalnumber"]

    db: Session = next(get_db())

    user = db.query(User).filter(User.user_id == user_id).first()

    if user:
        user.name = name
        user.national_number = national_number
        user.phone = phone_number
    else:
        user = User(user_id=user_id, name=name, national_number=national_number, phone=phone_number)
        db.add(user)

    db.commit()

    await update.message.reply_text(
        f"اطلاعات شما با موفقیت ثبت شد:\n\n"
        f"🟢 نام و نام خانوادگی: {name}\n"
        f"🟢 شماره ملی: {national_number}\n"
        f"🟢 شماره تلفن: {phone_number}"
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    context.user_data.clear()
    return ConversationHandler.END