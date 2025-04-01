from telegram.ext import CommandHandler, MessageHandler, filters
from handlers.user_handler import get_user_conversation_handler, get_change_name_handler
from handlers.new_request import NewRequestHandler
from handlers.menu_handler import setup_menu_handlers, show_main_menu, handle_back_to_menu

def setup_user_handlers(app):
    """Setup user-related handlers"""
    app.add_handler(get_user_conversation_handler())
    app.add_handler(get_change_name_handler())
    app.add_handler(CommandHandler("menu", show_main_menu))

def setup_new_request_handlers(app):
    """Setup new request handlers"""
    app.add_handler(NewRequestHandler.get_conversation_handler())

def setup_all_handlers(app):
    """Setup all application handlers"""
    # General back to menu handler
    app.add_handler(MessageHandler(
        filters.Regex(r'^(بازگشت|بازگشت به منوی اصلی|انصراف)$'),
        handle_back_to_menu
    ))
    
    setup_user_handlers(app)
    setup_new_request_handlers(app)
    setup_menu_handlers(app)
