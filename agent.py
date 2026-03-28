#!/usr/bin/env python3
"""
Job Monitor Agent for Alena Nikolskaia

Runs as a Telegram bot. Periodically searches for jobs, sends them with
Yes/No buttons. Only tailors CV + cover letter when user taps "Yes".

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

from config import MIN_RELEVANCE_SCORE, MIN_MATCH_SCORE
from job_search import search_jobs
from job_screener import screen_job
from cv_tailor import tailor_cv
from cv_generator import generate_cv_docx
from cover_letter import generate_cover_letter, generate_cover_letter_docx
from job_history import record_decision, get_history, get_stats, export_csv
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
    # Basic keyword filter
    jobs = [j for j in jobs if j["score"] >= MIN_RELEVANCE_SCORE]

    if not jobs:
        await send_status(bot, TG_CHAT_ID, "😴 No new matching positions found this time.")
        logger.info("No new jobs found.")
        return

    await send_status(
        bot, TG_CHAT_ID,
        f"🔍 Found <b>{len(jobs)}</b> job postings. Screening with AI (≥{MIN_MATCH_SCORE}% match)..."
    )

    # AI screening — score each job against profile
    matched_jobs = []
    for job in jobs:
        result = screen_job(ANTHROPIC_KEY, job)
        job["match_score"] = result["score"]
        job["match_reason"] = result["reason"]
        logger.info(f"Screened: {result['score']}% — {job['title'][:60]}")

        if result["score"] >= MIN_MATCH_SCORE:
            matched_jobs.append(job)

    if not matched_jobs:
        await send_status(
            bot, TG_CHAT_ID,
            f"😴 Screened {len(jobs)} positions but none matched ≥{MIN_MATCH_SCORE}%. "
            f"Best was {max(j['match_score'] for j in jobs)}%."
        )
        logger.info("No jobs passed AI screening.")
        return

    matched_jobs.sort(key=lambda j: -j["match_score"])

    await send_status(
        bot, TG_CHAT_ID,
        f"📋 <b>{len(matched_jobs)}</b> position(s) matched ≥{MIN_MATCH_SCORE}%. Sending for review..."
    )

    for job in matched_jobs:
        save_pending_job(job)
        await send_job_for_review(bot, TG_CHAT_ID, job)
        await asyncio.sleep(1)  # avoid rate limits

    logger.info(f"Sent {len(matched_jobs)} jobs for review (from {len(jobs)} screened).")


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
        record_decision(job, "skipped")
        remove_pending_job(job_id)
        await query.edit_message_text(
            text=f"⏭ <b>Skipped:</b> {job['title']}",
            parse_mode="HTML",
        )
        logger.info(f"Skipped: {job['title']}")
        return

    # User said YES — tailor CV + generate cover letter
    await query.edit_message_reply_markup(reply_markup=None)
    await send_status(
        context.bot, TG_CHAT_ID,
        f"⏳ Tailoring CV & cover letter for: <b>{job['title']}</b>\nThis takes ~60 seconds..."
    )

    tailored = tailor_cv(ANTHROPIC_KEY, job)

    cv_path = None
    cl_path = None
    match_score = None

    if tailored:
        match_score = tailored.get("match_score")

        try:
            cv_path = generate_cv_docx(tailored, job["title"], job["url"])
            logger.info(f"CV generated: {cv_path}")
        except Exception as e:
            logger.error(f"CV generation failed: {e}")

        # Generate cover letter
        try:
            cl_data = generate_cover_letter(ANTHROPIC_KEY, job)
            if cl_data:
                cl_path = generate_cover_letter_docx(cl_data, job["title"])
                logger.info(f"Cover letter generated: {cl_path}")
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")

        await send_tailored_cv(context.bot, TG_CHAT_ID, job, tailored, cv_path, cl_path)
    else:
        await send_status(
            context.bot, TG_CHAT_ID,
            f"⚠️ CV tailoring failed for: {job['title']}. Please try again later."
        )

    record_decision(job, "approved", match_score)
    remove_pending_job(job_id)


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command — trigger a manual search."""
    await do_search(context.bot)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 <b>Job Monitor Bot</b>\n\n"
        "I search for positions across two tracks:\n"
        "🎯 <b>Track 1:</b> AI Product Manager roles (finance/accounting/audit + AI)\n"
        "🏢 <b>Track 2:</b> Accounting/finance roles at big AI/tech companies\n\n"
        "<b>Commands:</b>\n"
        "/search - Search for new positions now\n"
        "/status - Show bot status\n"
        "/history - Recent job decisions\n"
        "/export - Export job history as CSV\n\n"
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

    stats = get_stats()

    await update.message.reply_text(
        f"📊 <b>Bot Status</b>\n\n"
        f"Pending reviews: {len(pending)}\n"
        f"Auto-search interval: every {CHECK_INTERVAL}h\n"
        f"Time now: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"<b>History:</b>\n"
        f"Total jobs reviewed: {stats['total']}\n"
        f"Approved: {stats['approved']} | Skipped: {stats['skipped']}\n"
        f"Approval rate: {stats['approval_rate']}",
        parse_mode="HTML",
    )


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command — show recent job decisions."""
    history = get_history(limit=15)

    if not history:
        await update.message.reply_text("No job history yet. Use /search to find positions.")
        return

    lines = ["📜 <b>Recent Job Decisions</b>\n"]
    for entry in reversed(history):
        icon = "✅" if entry["decision"] == "approved" else "⏭"
        score_str = f" (match: {entry['match_score']}%)" if entry.get("match_score") else ""
        date = entry["decided_at"][:10]
        lines.append(f"{icon} <b>{entry['title'][:60]}</b>{score_str}\n   {date}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export command — export job history as CSV."""
    path = export_csv()
    if not path:
        await update.message.reply_text("No job history to export yet.")
        return

    from pathlib import Path
    with open(path, "rb") as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            caption="📊 Job application history",
            filename="job_applications.csv",
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
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("export", cmd_export))
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
