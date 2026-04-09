# PinSaver — Telegram Bot: Pinterest Video Downloader

## Goal
A Telegram bot that accepts Pinterest URLs and replies with the highest-quality video available.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | async support, rich ecosystem |
| Bot framework | `python-telegram-bot` v21 (async) | well-maintained, full Bot API coverage |
| Video extraction | `yt-dlp` | natively supports Pinterest, auto-selects best format |
| Config | `python-dotenv` + `.env` | keeps secrets out of code |
| Temp files | `tempfile` (stdlib) | auto-cleanup |

---

## Project Structure

```
pinsaver/
├── .env                  # BOT_TOKEN (gitignored)
├── .env.example          # template for contributors
├── requirements.txt
├── PLAN.md               # this file
├── main.py               # entry point — starts polling
├── bot/
│   ├── __init__.py
│   ├── handlers.py       # /start, /help, message handler
│   └── messages.py       # all user-facing text strings
├── downloader/
│   ├── __init__.py
│   └── pinterest.py      # yt-dlp wrapper, highest-quality extraction
└── utils/
    ├── __init__.py
    └── helpers.py        # URL validation, file size guard
```

---

## Bot Flow

```
User sends message
        │
        ▼
  Is it a Pinterest URL?
   ├── No  → "Please send a valid Pinterest link"
   └── Yes │
           ▼
     Reply "⏳ Downloading…"
           │
           ▼
     yt-dlp extracts best quality video → temp file
           │
     ┌─────┴──────┐
  ≤ 50 MB        > 50 MB
     │               │
  Send video     "File too large, here's
  as document       the direct URL: …"
     │
  Delete temp file
```

---

## Supported Pinterest URL Formats

- `https://www.pinterest.com/pin/123456789/`
- `https://pin.it/XXXXXXX`  (short link — yt-dlp resolves automatically)
- `https://www.pinterest.co.uk/pin/…`
- `https://www.pinterest.com.au/pin/…`
- Any `pinterest.*/pin/` variant

---

## yt-dlp Format Strategy

```python
ydl_opts = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "merge_output_format": "mp4",
    "outtmpl": "<tempdir>/%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
}
```

This picks the highest-resolution MP4 + best audio, falling back gracefully.

---

## Error Cases & Responses

| Situation | Bot reply |
|---|---|
| Not a Pinterest URL | Ask user to send a valid link |
| Pin has no video (image) | "This pin doesn't contain a video" |
| File > 50 MB Telegram limit | Send direct download URL instead |
| yt-dlp extraction failure | "Couldn't download this video, try again" |
| Network / timeout error | "Something went wrong, please retry" |

---

## Environment Variables

```
BOT_TOKEN=your_telegram_bot_token_here
```

---

## Implementation Order

1. `requirements.txt` + `.env.example`
2. `utils/helpers.py` — URL validation
3. `downloader/pinterest.py` — yt-dlp wrapper
4. `bot/messages.py` — text constants
5. `bot/handlers.py` — Telegram handlers
6. `main.py` — wire everything together & run
