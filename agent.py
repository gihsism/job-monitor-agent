#!/usr/bin/env python3
"""
Job Monitor Agent for Alena Nikolskaia

Runs as a Telegram bot. Periodically searches for jobs, sends them with
Yes/No buttons. Only tailors CV when user taps "Yes".

Usage:
    python agent.py          # Start the bot (runs continuously)
    python agent.py --once   # Search once, send results, then wait for button clicks
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

from config import MIN_RELEVANCE_SCORE
from job_search import search_jobs
from cv_tailor import tailor_cv
from cv_generator import generate_cv_docx
from telegram_notify import (
    send_job_for_review,
    send_tailored_cv,
    send_status,
    save_pending_job,
    get_pending_job,
    remove_pending_job,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"[ERROR] Missing environment variable: {key}")
        print(f"        Copy .env.example to .env and fill in your keys.")
        sys.exit(1)
    return val


EXA_KEY = get_env("EXA_API_KEY")
ANTHROPIC_KEY = get_env("ANTHROPIC_API_KEY")
TG_TOKEN = get_env("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = get_env("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_HOURS", "12"))


async def do_search(bot: Bot):
    """Run a job search and send results with Yes/No buttons."""
    logger.info("Starting job search...")
    await send_status(bot, TG_CHAT_ID, "🔍 <b>Searching for new positions...</b>")

    jobs = search_jobs(EXA_KEY)
    # Filter to best matches only
    jobs = [j for j in jobs if j["score"] >= MIN_RELEVANCE_SCORE]

    if not jobs:
        await send_status(bot, TG_CHAT_ID, "😴 No new matching positions found this time.")
        logger.info("No new jobs found.")
        return

    await send_status(
        bot, TG_CHAT_ID,
        f"📋 Found <b>{len(jobs)}</b> new position(s). Sending for your review..."
    )

    for job in jobs:
        save_pending_job(job)
        await send_job_for_review(bot, TG_CHAT_ID, job)
        await asyncio.sleep(1)  # avoid rate limits

    logger.info(f"Sent {len(jobs)} jobs for review.")


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Yes/No button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    action, job_id = data.split(":", 1)

    job = get_pending_job(job_id)
    if not job:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "no":
        remove_pending_job(job_id)
        await query.edit_message_text(
            text=f"⏭ <b>Skipped:</b> {job['title']}",
            parse_mode="HTML",
        )
        logger.info(f"Skipped: {job['title']}")
        return

    # User said YES — tailor CV
    await query.edit_message_reply_markup(reply_markup=None)
    await send_status(
        context.bot, TG_CHAT_ID,
        f"⏳ Tailoring CV for: <b>{job['title']}</b>\nThis takes ~30 seconds..."
    )

    tailored = tailor_cv(ANTHROPIC_KEY, job)

    cv_path = None
    if tailored:
        try:
            cv_path = generate_cv_docx(tailored, job["title"], job["url"])
            logger.info(f"CV generated: {cv_path}")
        except Exception as e:
            logger.error(f"CV generation failed: {e}")

        await send_tailored_cv(context.bot, TG_CHAT_ID, job, tailored, cv_path)
    else:
        await send_status(
            context.bot, TG_CHAT_ID,
            f"⚠️ CV tailoring failed for: {job['title']}. Please try again later."
        )

    remove_pending_job(job_id)


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command — trigger a manual search."""
    await do_search(context.bot)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 <b>Job Monitor Bot</b>\n\n"
        "I search for AI Product Manager positions in the Zurich area "
        "and send them to you for review.\n\n"
        "<b>Commands:</b>\n"
        "/search - Search for new positions now\n"
        "/status - Show bot status\n\n"
        f"Auto-search runs every {CHECK_INTERVAL} hours.",
        parse_mode="HTML",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    from telegram_notify import PENDING_JOBS_FILE
    import json

    pending = {}
    if PENDING_JOBS_FILE.exists():
        pending = json.loads(PENDING_JOBS_FILE.read_text())

    await update.message.reply_text(
        f"📊 <b>Bot Status</b>\n\n"
        f"Pending reviews: {len(pending)}\n"
        f"Auto-search interval: every {CHECK_INTERVAL}h\n"
        f"Time now: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        parse_mode="HTML",
    )


async def scheduled_search(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job search callback."""
    await do_search(context.bot)


def main():
    parser = argparse.ArgumentParser(description="Job Monitor Agent")
    parser.add_argument("--once", action="store_true", help="Search once then listen for buttons")
    args = parser.parse_args()

    app = Application.builder().token(TG_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(handle_button))

    # Schedule periodic searches
    if not args.once:
        app.job_queue.run_repeating(
            scheduled_search,
            interval=CHECK_INTERVAL * 3600,
            first=10,  # first search 10 seconds after start
        )
    else:
        # Just run once after 5 seconds
        app.job_queue.run_once(scheduled_search, when=5)

    print(f"🤖 Bot started! Search interval: {CHECK_INTERVAL}h")
    print(f"   Send /search in Telegram to trigger a manual search.")
    print(f"   Press Ctrl+C to stop.")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
