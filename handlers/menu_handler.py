from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
import requests
from datetime import datetime
from functools import lru_cache
from config import CHANNEL_USERNAME, TRANSFER_TYPES, TRANSFER_REGEX
from telegram.constants import ParseMode
import re



@lru_cache(maxsize=32 )
def get_cbi_rate(currency):
    try:
        response = requests.get("https://api.cbi.ir/rates", timeout=5)
        data = response.json()
        return  {
            'buy': data[currency.lower()]['buy'],
            'sell': data[currency.lower()]['sell']
        }
    
    except():
        return None
    
@lru_cache(maxsize=32 )
def get_namadar_rate(currency):
    try:
        response = requests.get("https://api.namadar.ir/v1/rates", timeout=5)
        data = response.json()
        return  {
            'buy': data[currency.lower()]['buy'],
            'sell': data[currency.lower()]['sell']
        }
    except():
        return None

@lru_cache(maxsize=32   )
def get_sanarate_rate(currency):
    try:
        response = requests.get("https://sanarate.ir/api/currency", timeout=5)
        data = response.json()
        return {
            'buy': data[currency.lower()]['price'],
            'sell': data[currency.lower()]['price']
        }
    except():
        return None


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 ثبت درخواست جدید", callback_data="new_request")],
        [InlineKeyboardButton("⚙️ تنظیمات کاربری", callback_data="user_settings")],
        [InlineKeyboardButton("💵 نرخ لحظه‌ای ارز", callback_data="exchange_price")],
        [InlineKeyboardButton("📜 شرایط تبادل", callback_data="exchange_condition")],
        [InlineKeyboardButton("نمایش لیست حواله ها" , callback_data="show_remittance_list")]   
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 **منوی اصلی**",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )

async def show_exchange_rates(update:Update , context:ContextTypes.DEFAULT_TYPE):

    try:
        usd_rates = {
            'بانک مرکزی': get_cbi_rate('USD'),
            'نماگر': get_namadar_rate('USD'),
            'سنا': get_sanarate_rate('USD')
        }


        eur_rates = {
            'بانک مرکزی': get_cbi_rate('EUR'),
            'نماگر': get_namadar_rate('EUR'),
            'سنا': get_sanarate_rate('EUR')
        }

        message = "💱 **نرخ لحظه‌ای ارزها**\n\n"

        message += "🇺🇸 **دلار آمریکا:**\n"
        for source , rate in usd_rates.items():
            if rate:
                message += f"▫️ {source} : {rate['buy']:, / {rate['sell']:,}}\n"
        message += "\n"

        message += "🇪🇺 **یورو اروپا:**\n"
        for source, rate in eur_rates.items():
            if rate:
                message += f"▫️ {source}: {rate['buy']:,} / {rate['sell']:,}\n"
        

        message += (
            f"\n🕒 آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}\n"
            "🔢 اعداد به تومان - فرمت: خرید/فروش\n\n"
            "🔄 برای بروزرسانی دوباره کلیک کنید"
        )


        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی" , callback_data="exchange_price")], 
            [InlineKeyboardButton("🔙 بازگشت", callback_data="exchange_price")], 

        ]
        reply_markup =[InlineKeyboardMarkup(keyboard)]

        await update.callback_query.edit_message_text(
            text=message , 
            reply_markup= reply_markup ,
            parse_mode= "MarkdownV2"
        )

    except():
        error_msg = "⚠️ خطا در دریافت نرخ ارز. لطفاً چند دقیقه دیگر تلاش کنید." 

        keyboard = [ 
            [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="exchange_price")],
            [InlineKeyboardButton("🔙 بازگشت" , callback_data= "main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=error_msg , 
        reply_markup= reply_markup
    )
async def show_exchange_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش شرایط تبادل"""
    conditions = (
        "📜 **شرایط تبادل ارز:**\n\n"
        "✅ آیدی: 🆔\n\n"
        "🔹 نرخ تبادل بر اساس توافق طرفین مشخص می‌شود\n"
        "🔹 تنها تراکنش‌های حساب‌های تأییدشده پذیرفته می‌شوند\n"
        "🔹 واریز ریال باید طی چند ساعت کاری انجام شود\n"
        "🔹 ارسال رسید پرداخت ضروری است\n"
        "🔹 تسویه حساب ریالی طی یک روز کاری انجام می‌شود\n"
        "🔹 واریزها از طریق کارت به کارت یا شبا انجام می‌شود\n"
        "🔹 تأیید واریزی یورویی بر عهده خریدار است\n"
        "🔹 مسئولیت نهایی تبادل بر عهده طرفین است\n"
        "🔹 کارمزد انتقال ۰.۵٪ (حداقل ۲.۵ یورو)\n"
        "🔹 ارتباط مستقیم ممنوع - فقط از طریق ربات\n\n"
        "لطفاً قبل از ادامه، این شرایط را مطالعه کنید."
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text=conditions,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )

async def show_user_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش تنظیمات کاربری"""
    keyboard = [
        [InlineKeyboardButton("✏️ تغییر نام", callback_data="change_name")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "⚙️ **تنظیمات کاربری:**",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )




async def handle_transfer_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "request_list":
        keyboard = [
            [InlineKeyboardButton(text, callback_data=f"show_{key}")] 
            for key, text in TRANSFER_TYPES.items()
        ] + [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        
        await query.edit_message_text(
            "📋 نوع درخواست را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # استخراج نوع درخواست
    req_type = query.data.replace("show_", "")
    
    try:
        # دریافت پیام‌ها از کانال
        pattern = re.compile(TRANSFER_REGEX, re.VERBOSE | re.DOTALL)
        requests = []
        
        async for message in context.bot.get_chat_history(
            chat_id=CHANNEL_USERNAME,
            limit=50
        ):
            if message.text and req_type in message.text:
                match = pattern.search(message.text)
                if match:
                    requests.append(match.groupdict())
                    if len(requests) >= 10:
                        break
        
        if not requests:
            await query.edit_message_text(
                f"⚠️ درخواستی برای {TRANSFER_TYPES.get(req_type, '')} یافت نشد.",
                reply_markup=back_button()
            )
            return
        
        # ساخت پیام خروجی
        message = [
            f"📋 {TRANSFER_TYPES.get(req_type, '')}",
            "▫️"*10,
            *[
                f"{i}. 🌍 {req['country']}\n"
                f"   💰 {req['amount']}\n"
                f"   💵 {req['price']}\n"
                f"   🆔 {req['code']}"
                for i, req in enumerate(requests, 1)
            ],
            f"\n🔄 {datetime.now().strftime('%H:%M')}"
        ]
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data=query.data)],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="request_list")]
        ]
        
        await query.edit_message_text(
            text="\n\n".join(message),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    except Exception:
        await query.edit_message_text(
            "⚠️ خطا در دریافت اطلاعات.",
            reply_markup=back_button()
        )

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="request_list")]])

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "exchange_price":
        await show_exchange_rates(update, context)
    elif query.data == "main_menu":
        await show_main_menu(update, context)
    elif query.data == "new_request":
        from handlers.new_request import NewRequestHandler
        await NewRequestHandler.start_new_request(update, context)
    elif query.data == "user_settings":
        await show_user_settings(update, context)
    elif query.data == "exchange_condition":
        await show_exchange_conditions(update, context)
    elif query.data == "show_remittance_list":
        await handle_transfer_requests(update , context)




def setup_menu_handlers(app):
    app.add_handler(CommandHandler("start", show_main_menu))
    
    app.add_handler(CallbackQueryHandler(
        handle_button_click,
        pattern="^(exchange_price|main_menu|new_request|user_settings|exchange_condition|change_name)$"
    ))