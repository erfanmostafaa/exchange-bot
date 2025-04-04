from telegram.ext import Application
from decouple import config
from handlers.setup import setup_all_handlers


# Set up the bot application
app = Application.builder().token(config("TOKEN")).build()

# Register the commands
setup_all_handlers(app)

# Start the bot
app.run_polling()

