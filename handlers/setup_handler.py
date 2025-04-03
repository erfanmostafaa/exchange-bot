from telegram.ext import CommandHandler, MessageHandler, filters
from handlers.user_handler import get_user_conversation_handler, get_change_name_handler
from handlers.menu_handler import (
    show_main_menu,
    handle_back_to_menu,
    user_info_handler,
    get_remittance_handler,
    support_handler,
    exchange_conditions
)
from telegram.ext import Application

def setup_user_handlers(app: Application):
    """Register all user-related handlers"""
    app.add_handler(get_user_conversation_handler())
    app.add_handler(get_change_name_handler())
    app.add_handler(CommandHandler("menu", show_main_menu))
    app.add_handler(CommandHandler("start", show_main_menu))

def setup_new_request_handlers(app: Application):
    """Register new request handlers"""
    from handlers.new_request import NewRequestHandler  # Import مستقیم برای اطمینان
    try:
        # بررسی وجود متد قبل از فراخوانی
        if hasattr(NewRequestHandler, 'get_conversation_handler'):
            app.add_handler(NewRequestHandler.get_conversation_handler())
        else:
            print("Warning: get_conversation_handler() not found in NewRequestHandler!")
    except Exception as e:
        print(f"Error setting up new request handlers: {e}")

def setup_menu_handlers(app: Application):
    """Register all menu handlers"""
    app.add_handler(get_remittance_handler())
    app.add_handler(MessageHandler(filters.Regex(r'^📞 پشتیبانی$'), support_handler))
    app.add_handler(MessageHandler(filters.Regex(r'^ℹ️ اطلاعات کاربری$'), user_info_handler))
    app.add_handler(MessageHandler(filters.Regex(r'^شرایط تبادل ارز$'), exchange_conditions))

def setup_all_handlers(app: Application):
    """Register all application handlers"""
    # General handlers
    app.add_handler(MessageHandler(
        filters.Regex(r'^(بازگشت|بازگشت به منوی اصلی|انصراف)$'),
        handle_back_to_menu
    ))
    
    # Feature handlers
    setup_user_handlers(app)
    setup_new_request_handlers(app)  
    setup_menu_handlers(app)