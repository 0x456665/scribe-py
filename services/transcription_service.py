import os
import tempfile
from typing import Dict, Any
# import whisper
from loguru import logger
from config.settings import settings
from utils.file_utils import convert_to_wav, get_audio_duration, cleanup_file
from errors.custom_exceptions import TranscriptionError
from transformers import AutomaticSpeechRecognitionPipeline, pipeline
import librosa


class TranscriptionService:
    def __init__(self):
        # self.model_path = settings.WHISPER_MODEL_PATH
        self._model : AutomaticSpeechRecognitionPipeline | None = None

    def _load_model(self):
        """Load Whisper model lazily"""
        if self._model is None:
            try:
                # if not os.path.exists(self.model_path):
                #     raise TranscriptionError(
                #         f"Whisper model not found at {self.model_path}"
                #     )

                self._model = pipeline("automatic-speech-recognition", model="0x456665/whisper-small-medical")
                logger.info("Loaded Whisper model")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise TranscriptionError(
                    f"Failed to load transcription model: {str(e)}"
                )

    async def transcribe_audio(
        self, file_path: str, original_filename: str
    ) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        self._load_model()

        temp_wav_path = None
        try:
            # Get file info
            duration = get_audio_duration(file_path)
            file_size = os.path.getsize(file_path)

            # Convert to WAV if necessary
            if not file_path.lower().endswith(".wav"):
                temp_wav_path = tempfile.mkstemp(suffix=".wav")
                if not convert_to_wav(file_path, temp_wav_path[1]):
                    raise TranscriptionError("Failed to convert audio file")
                transcription_path = temp_wav_path[1]
            else:
                transcription_path = file_path

            # Perform transcription
            logger.info(f"Starting transcription of {original_filename}")

            try:
                audio, _ = librosa.load(transcription_path, sr=16000)
                if (not self._model):
                    raise TranscriptionError("model not loaded properly")
                result =  self._model(audio)
                print(result)
                transcription_text = result.get("text", "")

                if not transcription_text:
                    raise TranscriptionError("No speech detected in audio file")

                logger.info(f"Transcription completed for {original_filename}")

                return {
                    "transcription": transcription_text,
                    "duration": duration,
                    "file_size": file_size,
                    "filename": original_filename,
                }

            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")
                raise TranscriptionError(f"Transcription failed: {str(e)}")

        finally:
            # Clean up temporary files
            if temp_wav_path and os.path.exists(temp_wav_path[1]):
                cleanup_file(temp_wav_path[1])

    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats"""
        return [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"]
