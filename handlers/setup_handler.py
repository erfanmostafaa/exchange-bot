from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from handlers.user_handler import start, get_name, get_national_number, get_phone, cancel, GET_NAME, GET_NATIONAL_NUMBER, GET_PHONE
from handlers.new_request import NewRequestHandler
from handlers.menu_handler import setup_menu_handlers

def setup_user_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_NATIONAL_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_national_number)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

def setup_new_request_handlers(app):
    app.add_handler(NewRequestHandler.get_conversation_handler())

def setup_all_handlers(app):
    setup_user_handlers(app)
    setup_new_request_handlers(app)
    setup_menu_handlers(app)