from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from database  import get_db
from models.request import Request
from sqlalchemy.orm import Session



async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ثبت درخواست جدید", callback_data="new_request")],
        [InlineKeyboardButton("نمایش لیست حواله‌ها", callback_data="show_requests")],
        [InlineKeyboardButton("تنظیمات کاربری", callback_data="user_settings")],
        [InlineKeyboardButton("نرخ ارز", callback_data="exchange_price")],
        [InlineKeyboardButton("شرایط تبادل ارز", callback_data="exchnage_condition")],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 **منوی اصلی**",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_requests":
        keyboard = [
            [InlineKeyboardButton("فروش پی‌پال", callback_data="sell_paypal")],
            [InlineKeyboardButton("خرید پی‌پال", callback_data="buy_paypal")],
            [InlineKeyboardButton("فروش اسکناس", callback_data="sell_cash")],
            [InlineKeyboardButton("خرید اسکناس", callback_data="buy_cash")],
            [InlineKeyboardButton("فروش حواله بانکی", callback_data="sell_bank_transfer")],
            [InlineKeyboardButton("خرید حواله بانکی", callback_data="buy_bank_transfer")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=reply_markup
        )
    elif query.data.startswith("sell_") or query.data.startswith("buy_"):
        transaction_type = query.data
        requests = get_requests_from_database(transaction_type)  
        message = format_requests_message(requests) 
        await query.edit_message_text(message, parse_mode="MarkdownV2")
    elif query.data == "new_request":
        await query.edit_message_text("شما گزینه 'ثبت درخواست جدید' را انتخاب کردید.")
        from handlers.new_request import NewRequestHandler
        return await NewRequestHandler.start_new_request(update, context)
    elif query.data == "user_settings":
        await query.edit_message_text("شما گزینه 'تنظیمات کاربری' را انتخاب کردید.")

def get_requests_from_database(transaction_type):

    db:Session=next(get_db())

    if transaction_type.startswith("sell_"):
        transaction_type_db = "sell"
    elif transaction_type.startswith("buy_"):
        transaction_type_db = "buy"
    else:
        return []  
    requests = db.query(Request).filter(Request.transaction_type == transaction_type_db).all()
    return requests


def format_requests_message(requests):
    message = "📋 **لیست حواله‌ها**\n\n"
    for req in requests:
        message += (
            f"🔹 شماره: {req.id}\n"
            f"🔹 نوع: {req.transaction_type}\n"
            f"🔹 مقدار: {req.amount}\n"
            f"🔹 قیمت: {req.price}\n"
            f"🔹 روش پرداخت: {req.payment_method}\n"
            f"🔹 کشور: {req.country}\n\n"
        )
    return message

def setup_menu_handlers(app):
    app.add_handler(CommandHandler("start", show_main_menu))
    app.add_handler(CallbackQueryHandler(handle_button_click)) 