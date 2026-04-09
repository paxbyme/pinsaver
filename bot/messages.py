START = (
    "👋 Hello! Send me any <b>Pinterest</b> video link and I'll download "
    "the highest quality version for you.\n\n"
    "Supported formats:\n"
    "• pinterest.com/pin/…\n"
    "• pin.it/…"
)

HELP = (
    "Just paste a Pinterest video URL and I'll send you the video.\n\n"
    "<b>Example:</b>\n"
    "<code>https://www.pinterest.com/pin/123456789/</code>"
)

DOWNLOADING = "⏳ Downloading, please wait…"

TOO_LARGE = (
    "⚠️ The video is larger than Telegram's 50 MB limit.\n"
    "Here's the direct download link:\n{url}"
)

NO_VIDEO = "ℹ️ This pin doesn't contain a video (it might be an image or GIF)."

INVALID_URL = (
    "❌ That doesn't look like a Pinterest link.\n"
    "Please send a URL like:\n"
    "<code>https://www.pinterest.com/pin/123456789/</code>\n"
    "or a short <code>pin.it/…</code> link."
)

DOWNLOAD_FAILED = (
    "❌ Couldn't download that video. The pin may be private, deleted, "
    "or Pinterest changed something. Please try again later."
)

BLOCKED = (
    "❌ Pinterest blocked the request (403 Forbidden). "
    "This usually resolves on its own — please try again in a few minutes."
)

RATE_LIMITED = (
    "⏳ Pinterest is rate-limiting requests right now. "
    "Please wait a minute and try again."
)

GENERIC_ERROR = "❌ Something went wrong. Please try again."
