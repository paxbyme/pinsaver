import asyncio
import logging
import os
import time

from dotenv import load_dotenv
from telegram.error import Conflict, NetworkError, TimedOut
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from bot.handlers import cmd_help, cmd_start, handle_message

load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, (NetworkError, TimedOut)):
        logger.warning("Transient network error: %s", err)
        return
    logger.exception("Unhandled exception", exc_info=err)


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    # Python 3.14 no longer creates an implicit event loop;
    # set one explicitly before handing off to PTB's synchronous runner.
    asyncio.set_event_loop(asyncio.new_event_loop())

    # Conflict (another instance polling) terminates run_polling. During
    # Railway deploy transitions the old container can briefly overlap
    # with the new one — retry instead of exiting so Railway doesn't
    # leave the service stopped.
    backoff = 5
    while True:
        logger.info("Bot is running…")
        try:
            app.run_polling(drop_pending_updates=True)
            return
        except Conflict as exc:
            logger.warning("Polling conflict (%s); retrying in %ds", exc, backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)


if __name__ == "__main__":
    main()
