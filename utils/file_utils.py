import os
import aiofiles
from pathlib import Path
from typing import Optional
import ffmpeg
from loguru import logger


async def save_upload_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """Save uploaded file to disk"""
    file_path = Path(upload_dir) / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)

    return str(file_path)


def is_audio_file(filename: str) -> bool:
    """Check if file is a supported audio format"""
    allowed_extensions = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}
    return Path(filename).suffix.lower() in allowed_extensions


def get_audio_duration(file_path: str) -> Optional[float]:
    """Get audio file duration in seconds"""
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe["streams"][0]["duration"])
        return duration
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None


def convert_to_wav(input_path: str, output_path: str) -> bool:
    """Convert audio file to WAV format suitable for Whisper"""
    try:
        (
            ffmpeg.input(input_path)
            .output(output_path, acodec="pcm_s16le", ac=1, ar="16000")
            .overwrite_output()
            .run(quiet=True)
        )
        return True
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        return False


def cleanup_file(file_path: str) -> None:
    """Remove file from disk"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")
