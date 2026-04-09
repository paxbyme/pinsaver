import os
import tempfile
from dataclasses import dataclass

import yt_dlp


@dataclass
class DownloadResult:
    success: bool
    filepath: str | None = None      # local file path (if downloaded)
    direct_url: str | None = None    # best URL when file is too large / fallback
    title: str | None = None
    error: str | None = None
    is_image: bool = False


def download_best(url: str) -> DownloadResult:
    """
    Download the highest-quality video from a Pinterest URL.

    Returns a DownloadResult with either a local filepath or an error.
    On success the caller is responsible for deleting the file.
    """
    tmpdir = tempfile.mkdtemp(prefix="pinsaver_")
    outtmpl = os.path.join(tmpdir, "%(id)s.%(ext)s")

    ydl_opts = {
        # Pinterest uses HLS with separate video+audio streams.
        # bestvideo+bestaudio picks highest resolution video + audio and
        # ffmpeg merges them into a single MP4.
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
        "socket_timeout": 30,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Find the downloaded file
        filepath = ydl.prepare_filename(info)
        # yt-dlp may change extension after merge
        if not os.path.exists(filepath):
            filepath = _find_downloaded_file(tmpdir)

        if filepath is None:
            return DownloadResult(success=False, error="no_file")

        return DownloadResult(
            success=True,
            filepath=filepath,
            direct_url=_best_url(info),
            title=info.get("title"),
        )

    except yt_dlp.utils.DownloadError as exc:
        msg = str(exc).lower()
        if "no video" in msg or "not a video" in msg or "unsupported url" in msg:
            return DownloadResult(success=False, error="no_video")
        return DownloadResult(success=False, error=str(exc))
    except Exception as exc:  # noqa: BLE001
        return DownloadResult(success=False, error=str(exc))


def get_direct_url(url: str) -> DownloadResult:
    """
    Extract the direct video URL without downloading the file.
    Used as a fallback when the file is too large to send via Telegram.
    """
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return DownloadResult(
            success=True,
            direct_url=_best_url(info),
            title=info.get("title"),
        )
    except Exception as exc:  # noqa: BLE001
        return DownloadResult(success=False, error=str(exc))


# ── helpers ──────────────────────────────────────────────────────────────────

def _best_url(info: dict) -> str | None:
    """Pull the best video URL out of yt-dlp's info dict."""
    # Single-format URLs
    if info.get("url"):
        return info["url"]
    # Multi-format: pick the format with the highest resolution
    formats = info.get("formats") or []
    video_formats = [
        f for f in formats
        if f.get("vcodec") not in (None, "none") and f.get("url")
    ]
    if not video_formats:
        return None
    best = max(video_formats, key=lambda f: f.get("height") or 0)
    return best["url"]


def _find_downloaded_file(directory: str) -> str | None:
    """Scan directory for the first video file yt-dlp wrote."""
    for fname in os.listdir(directory):
        if fname.endswith((".mp4", ".webm", ".mkv", ".mov")):
            return os.path.join(directory, fname)
    return None
