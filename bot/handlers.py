import logging
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot import messages
from downloader.pinterest import download_best, get_direct_url
from utils.helpers import extract_pinterest_url, is_within_telegram_limit

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(messages.START, parse_mode=ParseMode.HTML)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(messages.HELP, parse_mode=ParseMode.HTML)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""

    url = extract_pinterest_url(text)
    if not url:
        await update.message.reply_text(messages.INVALID_URL, parse_mode=ParseMode.HTML)
        return

    status_msg = await update.message.reply_text(messages.DOWNLOADING)

    result = download_best(url)

    # ── success: file downloaded ──────────────────────────────────────────
    if result.success and result.filepath:
        try:
            if is_within_telegram_limit(result.filepath):
                await _send_video(update, result.filepath, result.title)
            else:
                # File too large — fall back to direct URL
                direct = result.direct_url or get_direct_url(url).direct_url
                if direct:
                    await update.message.reply_text(
                        messages.TOO_LARGE.format(url=direct),
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    await update.message.reply_text(messages.DOWNLOAD_FAILED)
        except Exception:
            logger.exception("Error sending video for %s", url)
            await update.message.reply_text(messages.GENERIC_ERROR)
        finally:
            _cleanup(result.filepath)

    # ── no video on this pin ──────────────────────────────────────────────
    elif result.error == "no_video":
        await update.message.reply_text(messages.NO_VIDEO)

    # ── pinterest blocked the bot ─────────────────────────────────────────
    elif result.error == "blocked":
        logger.warning("Pinterest 403 for %s", url)
        await update.message.reply_text(messages.BLOCKED)

    elif result.error == "rate_limited":
        logger.warning("Pinterest rate limit for %s", url)
        await update.message.reply_text(messages.RATE_LIMITED)

    # ── extraction failed ─────────────────────────────────────────────────
    else:
        logger.warning("Download failed for %s: %s", url, result.error)
        await update.message.reply_text(messages.DOWNLOAD_FAILED)

    # Always delete the "downloading…" status message
    try:
        await status_msg.delete()
    except Exception:
        pass


# ── helpers ───────────────────────────────────────────────────────────────────

async def _send_video(update: Update, filepath: str, title: str | None) -> None:
    caption = f"🎬 {title}" if title else None
    with open(filepath, "rb") as f:
        await update.message.reply_video(
            video=f,
            caption=caption,
            supports_streaming=True,
        )


def _cleanup(filepath: str) -> None:
    try:
        os.remove(filepath)
        # Also remove the temp dir if empty
        parent = os.path.dirname(filepath)
        if os.path.isdir(parent) and not os.listdir(parent):
            os.rmdir(parent)
    except OSError:
        pass
