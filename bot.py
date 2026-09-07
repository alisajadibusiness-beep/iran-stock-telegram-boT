import asyncio
import threading
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN

from database import (
    init_database,
    register_user,
    add_position,
    get_portfolio,
    save_signal
)

from market_data import (
    get_market_data,
    get_market_symbols
)

from analysis import (
    analyze_stock,
    calculate_profit
)

from web import run_web_server


logging.basicConfig(
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
    level=logging.INFO
)

logger = logging.getLogger(
    __name__
)


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            "🔎 تحلیل سهم",
            "🔥 فرصت‌های امروز"
        ],
        [
            "💼 سبد من",
            "💰 محاسبه سود"
        ],
        [
            "📊 وضعیت بازار",
            "📚 راهنما"
        ]
    ],
    resize_keyboard=True
)


def signal_text(result):

    signals = {
        "BUY": "🟢 خرید",
        "WATCH": "🟡 بررسی",
        "HOLD": "🔵 نگهداری",
        "SELL": "🔴 فروش"
    }

    return signals.get(
        result["signal"],
        result["signal"]
    )


def format_price(value):

    return f"{value:,.0f}"


def format_analysis(result):

    price = result["price"]

    target1 = result["target1"]

    target2 = result["target2"]

    target3 = result["target3"]

    stop = result["stop_loss"]

    profit1 = (
        (target1 - price)
        / price
    ) * 100

    profit2 = (
        (target2 - price)
        / price
    ) * 100

    profit3 = (
        (target3 - price)
        / price
    ) * 100

    loss = (
        (stop - price)
        / price
    ) * 100

    reasons = "\n".join(
        f"• {reason}"
        for reason in result["reasons"]
    )

    return f"""
📊 تحلیل سهم

نماد: {result["symbol"]}

💵 قیمت:
{format_price(price)}

━━━━━━━━━━━━━━

📌 وضعیت:
{signal_text(result)}

⭐ امتیاز:
{result["score"]}/100

📈 RSI:
{result["rsi"]}

📊 MACD:
{result["macd"]}

━━━━━━━━━━━━━━

🎯 اهداف احتمالی:

هدف 1:
{format_price(target1)}
(+{profit1:.1f}%)

هدف 2:
{format_price(target2)}
(+{profit2:.1f}%)

هدف 3:
{format_price(target3)}
(+{profit3:.1f}%)

🛑 حد ضرر:
{format_price(stop)}
({loss:.1f}%)

━━━━━━━━━━━━━━

🔍 دلایل:

{reasons}

⚠️ این خروجی تحلیل الگوریتمی است و
تضمین سود یا توصیه قطعی خرید و فروش نیست.
""".strip()


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    register_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    await update.message.reply_text(
        """
🤖 ربات تحلیل بورس

به سیستم تحلیل تکنیکال خوش آمدید.

برای شروع یکی از گزینه‌های زیر را انتخاب کنید.
""",
        reply_markup=MAIN_KEYBOARD
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        """
📚 راهنمای ربات

برای تحلیل سهم:

/analyze فولاد

یا از دکمه 🔎 تحلیل سهم استفاده کنید.

برای اضافه کردن سهم به سبد:

/add فولاد 1000 2500

یعنی:
نماد = فولاد
تعداد = 1000
قیمت خرید = 2500

برای مشاهده سبد:

/portfolio

برای محاسبه سود:

/profit 2500 3000 1000

برای مشاهده فرصت‌ها:

/opportunities
""",
        reply_markup=MAIN_KEYBOARD
    )


async def analyze_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.args:

        await update.message.reply_text(
            "مثال:\n/analyze فولاد"
        )

        return

    symbol = (
        " ".join(
            context.args
        )
        .strip()
    )

    try:

        data = get_market_data(
            symbol
        )

        result = analyze_stock(
            symbol,
            data
        )

        save_signal(
            symbol=result["symbol"],
            signal=result["signal"],
            score=result["score"],
            price=result["price"],
            stop_loss=result["stop_loss"],
            target1=result["target1"],
            target2=result["target2"],
            target3=result["target3"]
        )

        await update.message.reply_text(
            format_analysis(result),
            reply_markup=MAIN_KEYBOARD
        )

    except Exception as error:

        logger.exception(error)

        await update.message.reply_text(
            "❌ خطا در تحلیل سهم."
        )


async def opportunities_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    results = []

    for symbol in get_market_symbols():

        try:

            data = get_market_data(
                symbol
            )

            result = analyze_stock(
                symbol,
                data
            )

            results.append(
                result
            )

        except Exception as error:

            logger.error(
                "Analysis failed %s: %s",
                symbol,
                error
            )

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    text = "🔥 فرصت‌های امروز\n\n"

    for index, result in enumerate(
        results[:5],
        start=1
    ):

        text += (
            f"{index}. "
            f"{result['symbol']}\n"
            f"⭐ {result['score']}/100\n"
            f"{signal_text(result)}\n"
            f"💵 {format_price(result['price'])}\n\n"
        )

    text += (
        "⚠️ این فهرست صرفاً خروجی "
        "مدل تحلیل است."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_KEYBOARD
    )


async def portfolio_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    positions = get_portfolio(
        user_id
    )

    if not positions:

        await update.message.reply_text(
            "💼 سبد شما خالی است."
        )

        return

    text = "💼 سبد من\n\n"

    total_profit = 0

    for position in positions:

        symbol = position["symbol"]

        quantity = position["quantity"]

        buy_price = position["buy_price"]

        try:

            data = get_market_data(
                symbol
            )

            result = analyze_stock(
                symbol,
                data
            )

            current_price = result["price"]

            profit = calculate_profit(
                buy_price,
                current_price,
                quantity
            )

            total_profit += profit[
                "profit"
            ]

            text += (
                f"📌 {symbol}\n"
                f"تعداد: {quantity:,.0f}\n"
                f"خرید: {buy_price:,.0f}\n"
                f"فعلی: {current_price:,.0f}\n"
                f"سود: {profit['profit']:,.0f}\n"
                f"درصد: {profit['percentage']:.2f}%\n"
                f"وضعیت: "
                f"{signal_text(result)}\n\n"
            )

        except Exception:

            text += (
                f"📌 {symbol}\n"
                "خطا در دریافت قیمت\n\n"
            )

    text += (
        f"━━━━━━━━━━━━\n"
        f"سود/زیان کل: "
        f"{total_profit:,.0f}"
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_KEYBOARD
    )


async def add_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if len(context.args) != 3:

        await update.message.reply_text(
            """
فرمت صحیح:

/add SYMBOL QUANTITY BUY_PRICE

مثال:

/add فولاد 1000 2500
"""
        )

        return

    symbol = context.args[0].upper()

    try:

        quantity = float(
            context.args[1]
        )

        buy_price = float(
            context.args[2]
        )

        if quantity <= 0:
            raise ValueError

        if buy_price <= 0:
            raise ValueError

        add_position(
            telegram_id=update.effective_user.id,
            symbol=symbol,
            quantity=quantity,
            buy_price=buy_price
        )

        await update.message.reply_text(
            f"""
✅ سهم به سبد اضافه شد.

نماد: {symbol}
تعداد: {quantity:,.0f}
قیمت خرید: {buy_price:,.0f}
""",
            reply_markup=MAIN_KEYBOARD
        )

    except ValueError:

        await update.message.reply_text(
            "❌ مقدار تعداد یا قیمت صحیح نیست."
        )


async def profit_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if len(context.args) != 3:

        await update.message.reply_text(
            """
فرمت:

/profit BUY_PRICE CURRENT_PRICE QUANTITY

مثال:

/profit 2500 3000 1000
"""
        )

        return

    try:

        buy_price = float(
            context.args[0]
        )

        current_price = float(
            context.args[1]
        )

        quantity = float(
            context.args[2]
        )

        result = calculate_profit(
            buy_price,
            current_price,
            quantity
        )

        emoji = (
            "🟢"
            if result["profit"] >= 0
            else "🔴"
        )

        await update.message.reply_text(
            f"""
💰 محاسبه سود

سرمایه اولیه:
{result["investment"]:,.0f}

ارزش فعلی:
{result["current_value"]:,.0f}

{emoji} سود/زیان:
{result["profit"]:,.0f}

درصد:
{result["percentage"]:.2f}%
""",
            reply_markup=MAIN_KEYBOARD
        )

    except ValueError:

        await update.message.reply_text(
            "❌ مقادیر واردشده صحیح نیستند."
        )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "🔎 تحلیل سهم":

        await update.message.reply_text(
            "نام نماد را بفرستید.\nمثال: فولاد"
        )

        context.user_data[
            "waiting_for_symbol"
        ] = True

        return

    if text == "🔥 فرصت‌های امروز":

        await opportunities_command(
            update,
            context
        )

        return

    if text == "💼 سبد من":

        await portfolio_command(
            update,
            context
        )

        return

    if text == "💰 محاسبه سود":

        await update.message.reply_text(
            "برای محاسبه سریع از دستور زیر استفاده کنید:\n\n"
            "/profit 2500 3000 1000"
        )

        return

    if text == "📊 وضعیت بازار":

        symbols = get_market_symbols()

        await update.message.reply_text(
            "📊 وضعیت بازار\n\n"
            f"تعداد نمادهای نمونه: {len(symbols)}\n\n"
            "موتور تحلیل آماده است."
        )

        return

    if text == "📚 راهنما":

        await help_command(
            update,
            context
        )

        return

    if context.user_data.get(
        "waiting_for_symbol"
    ):

        symbol = text.strip()

        context.user_data[
            "waiting_for_symbol"
        ] = False

        context.args = [symbol]

        await analyze_command(
            update,
            context
        )

        return


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.exception(
        "Unhandled exception:",
        exc_info=context.error
    )


def start_web_server():

    thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    thread.start()


def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

    init_database()

    start_web_server()

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    application.add_handler(
        CommandHandler(
            "analyze",
            analyze_command
        )
    )

    application.add_handler(
        CommandHandler(
            "opportunities",
            opportunities_command
        )
    )

    application.add_handler(
        CommandHandler(
            "portfolio",
            portfolio_command
        )
    )

    application.add_handler(
        CommandHandler(
            "add",
            add_command
        )
    )

    application.add_handler(
        CommandHandler(
            "profit",
            profit_command
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler
        )
    )

    application.add_error_handler(
        error_handler
    )

    logger.info(
        "Stock Telegram Bot started."
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":

    main()
