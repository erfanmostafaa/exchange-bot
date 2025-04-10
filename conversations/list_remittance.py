from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove 
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CommandHandler
)
from handlers.menu import show_main_menu
from database import get_db
from models.tables import Remittance


class ListRemittanceConversation:
    SHOW_DETAILS = range(1)

    async def select_remittance_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the remittance process with clear options"""
        context.user_data.clear()
        
        keyboard = [
            ["خرید پی پال", "خرید حواله بانکی", "خرید اسکناس"],
            ["فروش پی پال", "فروش حواله بانکی", "فروش اسکناس"],
            ["بازگشت به منوی اصلی"]
        ]
        await update.message.reply_text(
            "📋 لطفاً نوع حواله مورد نظر را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True) )
        return self.SHOW_DETAILS
    
    
    async def show_remittance_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process the selected remittance type with better error handling"""
        user_choice = update.message.text
        
        if user_choice == "بازگشت به منوی اصلی":
            return await self.cancel_remittance(update, context)
        
        if not any(x in user_choice for x in ["خرید", "فروش"]):
            await update.message.reply_text(
                "⚠️ گزینه نامعتبر. لطفاً از دکمه‌های کیبورد استفاده کنید.",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True))
            return self.SHOW_DETAILS
        
        print(user_choice)
        transaction_type = "خرید" if "خرید" in user_choice else "فروش"
        transfer_type = " ".join(user_choice.split()[1:])
        
        db = next(get_db())
        last_five_remittance = (db.query(Remittance).order_by(Remittance.created_at.desc()).limit(5).all())

        for remittance in last_five_remittance:
            await update.message.reply_text(
                f"📌 شماره درخواست: {remittance.remittance_id}\n"
                f"💰 ارز: {remittance.currency}\n"
                f"🌍 کشور: {remittance.country}\n"
                f"💲 قیمت واحد: {remittance.price}\n"
                f"🔢 مقدار: {remittance.amount}\n"
                f"🔄 نوع تراکنش: {remittance.transaction_type}\n"
                f"💳 روش پرداخت: {remittance.payment_method}\n"
                f"🏢 نوع: {remittance.entity_type}\n\n",
                reply_markup=ReplyKeyboardMarkup([["بازگشت به منوی اصلی"]], resize_keyboard=True)
            )


        return ConversationHandler.END
            

    async def cancel_remittance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel operation and return to main menu"""
        await update.message.reply_text(
            "بازگشت به منوی اصلی...",
            reply_markup=ReplyKeyboardRemove()
        )
        await show_main_menu(update, context)
        context.user_data.clear()
        return ConversationHandler.END


    def list_remittance_handler(self):
        
        return ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(r'^📋 نمایش لیست حواله‌ها$'), self.select_remittance_type)],
            states={
                self.SHOW_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.show_remittance_list)],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel_remittance),
                MessageHandler(filters.Regex(r'^(بازگشت|بازگشت به منوی اصلی|انصراف)$'), self.cancel_remittance)],
            map_to_parent={
                ConversationHandler.END: ConversationHandler.END
            }
        )
