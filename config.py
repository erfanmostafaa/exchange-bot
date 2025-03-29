# config.py
CHANNEL_USERNAME = "@YourExchangeChannel"  # آیدی کانال تلگرام

TRANSFER_TYPES = {
    'sell_paypal': 'فروش پی‌پال',
    'buy_paypal': 'خرید پی‌پال',
    'sell_cash': 'فروش اسکناس',
    'buy_cash': 'خرید اسکناس',
    'sell_transfer': 'فروش حواله بانکی',
    'buy_transfer': 'خرید حواله بانکی'
}

TRANSFER_REGEX = r"""
    از\s+(?P<country>[^\n]+)\s*   # کشور مبدا
    .*?مبلغ:\s*(?P<amount>[^\n]+)\s*  # مقدار ارز
    .*?نرخ:\s*(?P<price>[^\n]+)\s*    # قیمت
    .*?کد:\s*(?P<code>[^\n]+)\s*      # کد پیگیری
    .*?نوع:\s*(?P<type>[^\n]+)        # نوع درخواست
"""