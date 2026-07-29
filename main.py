import logging
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("samuraifx")

SYSTEM_PROMPT = """
You are SamuraiFX AI, a Telegram trading education assistant focused only on GBPJPY.

Rules:
1. Only discuss GBPJPY, GBP fundamentals, JPY fundamentals, trading psychology, risk management, and technical analysis.
2. Never claim to have live prices, live charts, or live news unless the user provides them.
3. Clearly label analysis as educational, not financial advice.
4. Never guarantee profit or certainty.
5. Use clean Telegram-friendly formatting with emojis and no asterisks.
6. Keep responses direct and organized.
7. For trade ideas, use this format:
📊 Pair: GBPJPY
🧭 Bias:
🎯 Entry area:
🛑 Invalidation:
💰 Target 1:
💰 Target 2:
🧠 Reason:
⚠️ Risk:
8. When data is missing, ask the user for the current price, chart screenshot, timeframe, or levels.
"""

HELP_TEXT = """
🥷 SamuraiFX AI Commands

/start — Open the bot
/help — Show all commands
/bias — Daily GBPJPY bias
/weeklybias — Weekly GBPJPY bias
/session — Current session outlook
/asian — Asian session outlook
/london — London session outlook
/newyork — New York session outlook
/tradeidea — Build a GBPJPY trade idea
/autotradeidea — Autonomous-style GBPJPY setup framework
/chart — Analyze a chart screenshot
/levels — Key support and resistance
/zones — Supply and demand zones
/liquidity — Liquidity targets
/trend — Current trend framework
/structure — Market structure
/fvg — Fair value gaps
/orderblocks — Order blocks
/fibonacci — Fibonacci zones
/ema — EMA alignment
/patterns — Chart and candle patterns
/adr — Average daily range
/volatility — Volatility outlook
/correlation — GBPUSD and USDJPY relationship
/news — GBP and JPY news impact
/boe — Bank of England impact
/boj — Bank of Japan impact
/calendar — Important economic events
/newsimpact — Explain news impact
/risk — Risk calculator help
/lotsize — Lot-size calculator help
/rr — Risk-to-reward calculator
/pips — GBPJPY pip calculator
/learn — Trading education
/psychology — Trading mindset support
/status — Check bot status
/cancel — Cancel current action

💬 You can also type any GBPJPY question directly.
"""

async def send_ai(update: Update, prompt: str) -> None:
    if not update.effective_message:
        return

    if client is None:
        await update.effective_message.reply_text(
            "⚠️ OPENAI_API_KEY is missing in Railway Variables."
        )
        return

    await update.effective_chat.send_action(ChatAction.TYPING)

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )
        text = (response.output_text or "").strip()
        if not text:
            text = "⚠️ I could not generate a response. Try again."
        await update.effective_message.reply_text(text[:4096])
    except Exception as exc:
        logger.exception("OpenAI request failed")
        await update.effective_message.reply_text(
            f"⚠️ AI request failed: {type(exc).__name__}. Check OPENAI_API_KEY and OPENAI_MODEL."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🥷 Welcome to SamuraiFX AI\n\n"
        "📊 This bot focuses only on GBPJPY.\n"
        "🧠 Ask for bias, sessions, structure, trade ideas, risk, news impact, or chart analysis.\n\n"
        "Use /help to view every command."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_status = "Connected" if client else "Missing OPENAI_API_KEY"
    await update.message.reply_text(
        "✅ SamuraiFX AI is running\n"
        f"🤖 AI: {ai_status}\n"
        f"📊 Market focus: GBPJPY\n"
        f"🧠 Model: {OPENAI_MODEL}"
    )

async def bias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_ai(update, "Give a practical daily GBPJPY bias framework. Since you do not have live price data, ask for current price or a chart and explain exactly what confirms bullish, bearish, or neutral bias.")

async def weeklybias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_ai(update, "Give a GBPJPY weekly bias framework using weekly open, previous week high and low, daily structure, liquidity, and major GBP/JPY fundamentals. State that live chart data is needed for a final bias.")

async def session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now_et = datetime.now(ZoneInfo("America/New_York"))
    await send_ai(update, f"The current Eastern Time is {now_et:%A %I:%M %p}. Explain which forex session is active and give a GBPJPY session outlook framework without pretending to know live price.")

async def asian(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_ai(update, "Give a GBPJPY Asian session plan covering consolidation, Asian high and low, JPY volatility, liquidity sweeps, and what to watch before London.")

async def london(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_ai(update, "Give a GBPJPY London session plan covering Asian range breaks, London liquidity, GBP volatility, continuation versus reversal, and confirmation.")

async def newyork(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_ai(update, "Give a GBPJPY New York session plan covering London high and low, overlap volatility, USD-driven cross effects, profit taking, and reversal risk.")

async def tradeidea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = " ".join(context.args).strip()
    prompt = (
        "Build a GBPJPY trade idea using the required structured format. "
        "Do not invent live price data. Ask for current price, timeframe, or chart if missing."
    )
    if args:
        prompt += f"\nUser details: {args}"
    await send_ai(update, prompt)

async def autotradeidea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_ai(update, "Create an autonomous-style GBPJPY setup checklist with directional conditions, entry trigger, invalidation, targets, confidence factors, and no-trade conditions. Do not claim live market access.")

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📸 Send a clear GBPJPY chart screenshot.\n\n"
        "Include:\n"
        "⏱ Timeframe\n"
        "💵 Current price\n"
        "📍 Any marked zones\n\n"
        "After sending it, type what you want analyzed."
    )

COMMAND_PROMPTS = {
    "levels": "Explain how to identify current GBPJPY support, resistance, psychological levels, previous highs/lows, and session highs/lows. Ask for current price or chart.",
    "zones": "Explain how to identify GBPJPY supply and demand zones and how to validate them with displacement, liquidity, and reaction strength.",
    "liquidity": "Explain likely GBPJPY liquidity locations such as equal highs/lows, Asian range, previous day high/low, and obvious swing points.",
    "trend": "Explain how to determine GBPJPY trend across weekly, daily, 4H, 1H, and entry timeframe without inventing current direction.",
    "structure": "Explain GBPJPY market structure, BOS, CHOCH, higher highs/lows, lower highs/lows, and confirmation.",
    "fvg": "Explain GBPJPY fair value gaps, how to validate them, and how to use them with structure and liquidity.",
    "orderblocks": "Explain GBPJPY order blocks, valid versus weak order blocks, mitigation, and invalidation.",
    "fibonacci": "Explain GBPJPY Fibonacci retracement zones including 71.8, 78.6, and 88 percent and how to combine them with structure.",
    "ema": "Explain GBPJPY EMA alignment and how 8 EMA or 10 EMA can be used as confirmation rather than a standalone signal.",
    "patterns": "List useful GBPJPY chart and candlestick patterns and explain confirmation and invalidation.",
    "adr": "Explain GBPJPY average daily range, how to calculate it, and how to avoid chasing once most of the range is complete.",
    "volatility": "Explain GBPJPY volatility by Asian, London, and New York sessions and major risk factors.",
    "correlation": "Explain how GBPJPY relates to GBPUSD and USDJPY, including when the relationship can break down.",
    "news": "Explain the major types of GBP and JPY news that move GBPJPY. State that live news requires a current calendar or headline from the user.",
    "boe": "Explain how Bank of England rates, inflation language, voting splits, and guidance can affect GBPJPY.",
    "boj": "Explain how Bank of Japan policy, intervention risk, yields, and yen strength can affect GBPJPY.",
    "calendar": "List the key recurring GBP and JPY economic events a GBPJPY trader should monitor.",
    "newsimpact": "Ask the user to paste a headline or economic result, then explain how to evaluate its potential impact on GBPJPY.",
    "risk": "Explain a simple GBPJPY risk-management process using account balance, risk percentage, stop-loss pips, and lot size.",
    "lotsize": "Explain the inputs needed to calculate GBPJPY lot size and ask for account balance, risk percentage, stop-loss pips, and account currency.",
    "rr": "Explain risk-to-reward for GBPJPY and ask for entry, stop loss, and target.",
    "pips": "Explain that for most GBPJPY quotes, 0.01 equals one pip, then ask for entry and exit prices to calculate the move.",
    "learn": "Give a short GBPJPY lesson covering top-down analysis, session liquidity, entry confirmation, stop placement, and journaling.",
    "psychology": "Give direct trading psychology support for patience, revenge trading, fear of entry, overtrading, and following a GBPJPY plan.",
}

async def generic_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.split()[0].lstrip("/").split("@")[0].lower()
    prompt = COMMAND_PROMPTS.get(command, "Answer the user's GBPJPY trading question.")
    args = " ".join(context.args).strip()
    if args:
        prompt += f"\nUser details: {args}"
    await send_ai(update, prompt)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("✅ Cancelled.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    await send_ai(update, f"User question: {text}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Telegram update failed", exc_info=context.error)

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("bias", bias))
    app.add_handler(CommandHandler("weeklybias", weeklybias))
    app.add_handler(CommandHandler("session", session))
    app.add_handler(CommandHandler("asian", asian))
    app.add_handler(CommandHandler("london", london))
    app.add_handler(CommandHandler("newyork", newyork))
    app.add_handler(CommandHandler("tradeidea", tradeidea))
    app.add_handler(CommandHandler("autotradeidea", autotradeidea))
    app.add_handler(CommandHandler("chart", chart))
    app.add_handler(CommandHandler("cancel", cancel))

    for command in COMMAND_PROMPTS:
        app.add_handler(CommandHandler(command, generic_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)

    logger.info("SamuraiFX AI is starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
