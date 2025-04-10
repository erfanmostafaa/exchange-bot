from telegram.ext import Application
from decouple import config
from telegram.ext import CommandHandler, MessageHandler, filters
from conversations.register_remittance import RegisterRemittanceConversation 
from conversations.register_user import RegisterUserConversation
from conversations.change_name import ChangeNameConvarsation
from conversations.list_remittance import ListRemittanceConversation
from handlers.menu import show_main_menu, user_info_handler, support_handler, exchange_conditions


# Set up the bot application
app = Application.builder().token(config("TOKEN")).build()

list_remittance = ListRemittanceConversation()
register_remittance = RegisterRemittanceConversation()
register_user = RegisterUserConversation()
change_name = ChangeNameConvarsation()


"""Register all user-related handlers"""
app.add_handler(register_user.get_user_conversation_handler())
app.add_handler(change_name.get_change_name_handler())


"""Register all menu handlers"""
app.add_handler(CommandHandler("menu", show_main_menu))
app.add_handler(list_remittance.list_remittance_handler())
app.add_handler(register_remittance.get_conversation_handler())
app.add_handler(MessageHandler(filters.Regex(r'^(بازگشت|بازگشت به منوی اصلی|انصراف)$'), show_main_menu))
app.add_handler(MessageHandler(filters.Regex(r'^📞 پشتیبانی$'), support_handler))
app.add_handler(MessageHandler(filters.Regex(r'^ℹ️ اطلاعات کاربری$'), user_info_handler))
app.add_handler(MessageHandler(filters.Regex(r'^شرایط تبادل ارز$'), exchange_conditions))

# Start the bot
app.run_polling()

