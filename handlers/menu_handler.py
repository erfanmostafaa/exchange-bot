from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import ContextTypes, CallbackQueryHandler , CommandHandler

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ثبت درخواست جدید", callback_data="new_request")],
        [InlineKeyboardButton("نمایش لیست حواله‌ها", callback_data="show_requests")],
        [InlineKeyboardButton("تنظیمات کاربری", callback_data="user_settings")],
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

    if query.data == "new_request":
        await query.edit_message_text("شما گزینه 'ثبت درخواست جدید' را انتخاب کردید.")
        from handlers.new_request import NewRequestHandler
        return await NewRequestHandler.start_new_request(update, context)
    elif query.data == "show_requests":
        await query.edit_message_text("شما گزینه 'نمایش لیست حواله‌ها' را انتخاب کردید.")
    elif query.data == "user_settings":
        await query.edit_message_text("شما گزینه 'تنظیمات کاربری' را انتخاب کردید.")

def setup_menu_handlers(app):
    app.add_handler(CommandHandler("start", show_main_menu))
    app.add_handler(CallbackQueryHandler(handle_button_click))