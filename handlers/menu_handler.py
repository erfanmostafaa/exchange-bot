from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from config import CHANNEL_USERNAME, TRANSFER_TYPES, TRANSFER_REGEX
import re

# Conversation states
SELECT_TYPE, SHOW_DETAILS = range(2)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu"""
    keyboard = [
        ["📝 ثبت درخواست جدید", "📋 نمایش لیست حواله‌ها"],
        ["✏️ تغییر نام", "ℹ️ اطلاعات حساب"],
        ["📞 پشتیبانی"]
    ]
    await update.message.reply_text(
        "🏠 منوی اصلی:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to menu command"""
    await show_main_menu(update, context)

async def start_remittance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the remittance process"""
    keyboard = [
        ["خرید پی پال", "خرید حواله بانکی", "خرید اسکناس"],
        ["فروش پی پال", "فروش حواله بانکی", "فروش اسکناس"],
        ["بازگشت به منوی اصلی"]
    ]
    await update.message.reply_text(
        "📋 لطفاً نوع حواله مورد نظر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SELECT_TYPE

async def select_remittance_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the selected remittance type"""
    user_choice = update.message.text
    
    if user_choice == "بازگشت به منوی اصلی":
        return await cancel_remittance(update, context)
    
    transaction_type = "خرید" if user_choice.startswith("خرید") else "فروش"
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
                reply_markup=ReplyKeyboardMarkup([["بازگشت"]], resize_keyboard=True)
            )
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
        keyboard.append(["بروزرسانی", "بازگشت"])
        
        await update.message.reply_text(
            "\n".join(message),
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return SHOW_DETAILS
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(
            "⚠️ خطا در دریافت اطلاعات.",
            reply_markup=ReplyKeyboardMarkup([["بازگشت"]], resize_keyboard=True)
        )
        return SHOW_DETAILS

async def show_remittance_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show details of selected remittance"""
    user_input = update.message.text
    
    if user_input == "بروزرسانی":
        return await select_remittance_type(update, context)
    elif user_input == "بازگشت":
        return await start_remittance(update, context)
    
    if user_input.startswith("نمایش"):
        rem_id = user_input.replace("نمایش", "").strip()
        await display_full_remittance(update, context, rem_id)
    
    keyboard = [
        ["خرید پی پال", "خرید حواله بانکی", "خرید اسکناس"],
        ["فروش پی پال", "فروش حواله بانکی", "فروش اسکناس"],
        ["بازگشت به منوی اصلی"]
    ]
    await update.message.reply_text(
        "لطفاً انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SELECT_TYPE

async def fetch_remittances(bot, transaction_type, transfer_type):
    """Fetch remittances from channel using config settings"""
    remittances = []
    pattern = re.compile(TRANSFER_REGEX, re.VERBOSE)
    
    async for message in bot.get_chat_history(
        chat_id=CHANNEL_USERNAME,
        limit=50
    ):
        if message.text and transaction_type in message.text and TRANSFER_TYPES.get(transfer_type) in message.text:
            match = pattern.search(message.text)
            if match:
                remittance = match.groupdict()
                remittance['id'] = message.message_id
                remittances.append(remittance)
    return remittances

async def display_full_remittance(update: Update, context: ContextTypes.DEFAULT_TYPE, rem_id):
    """Display full remittance details from channel"""
    try:
        message = await context.bot.get_messages(
            chat_id=CHANNEL_USERNAME,
            message_ids=int(rem_id)
        )
        
        await update.message.reply_text(
            f"📋 جزئیات کامل حواله #{rem_id}:\n\n{message.text}",
            reply_markup=ReplyKeyboardRemove()
        )
    except():
        await update.message.reply_text(
            "⚠️ خطا در دریافت جزئیات حواله",
            reply_markup=ReplyKeyboardMarkup([["بازگشت"]], resize_keyboard=True)
        )

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
    """Setup conversation handler for remittances"""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^📋 نمایش لیست حواله‌ها$'), start_remittance)],
        states={
            SELECT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_remittance_type)],
            SHOW_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_remittance_detail)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_remittance),
            MessageHandler(filters.Regex(r'^(بازگشت|بازگشت به منوی اصلی)$'), cancel_remittance)],
    )

def setup_menu_handlers(app):
    """Setup menu handlers"""
    app.add_handler(get_remittance_handler())