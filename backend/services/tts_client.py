"""
Google Cloud Text-to-Speech client.
Converts AI-generated findings and verdicts into audio,
supporting accessibility for visually impaired users.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Guard: google-cloud-texttospeech may not be installed
try:
    from google.cloud import texttospeech as _tts_module  # type: ignore
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False
    _tts_module = None  # type: ignore
    logger.warning("[TTS] google-cloud-texttospeech not installed — audio output disabled")


class TTSClient:
    """
    Google Cloud Text-to-Speech API wrapper.

    Generates MP3 audio for:
      - One-liner verdicts
      - Executive summaries
      - Individual risk findings (plain English)

    Uses Neural2 voices for natural, human-like speech.
    Falls back gracefully when credentials are absent.
    """

    # Default voice configuration — Neural2 for best quality
    DEFAULT_LANGUAGE = "en-US"
    DEFAULT_VOICE_NAME = "en-US-Neural2-D"   # Professional male voice

    def __init__(self):
        self.credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json"
        )
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self._client = None
        self.enabled = (
            _TTS_AVAILABLE
            and bool(self.project_id)
            and (os.path.exists(self.credentials_path) or bool(os.getenv("K_SERVICE")))
        )

    def _get_client(self):
        """Lazy-initialize the TTS client."""
        if self._client is None:
            self._client = _tts_module.TextToSpeechClient()
            logger.info("[TTS] Cloud Text-to-Speech client initialized")
        return self._client

    def synthesize(
        self,
        text: str,
        language_code: str = DEFAULT_LANGUAGE,
        voice_name: str = DEFAULT_VOICE_NAME,
        speaking_rate: float = 0.95,
        pitch: float = 0.0,
    ) -> bytes:
        """
        Convert text to MP3 audio bytes.

        Args:
            text: Plain-text content to speak (max ~5000 chars).
            language_code: BCP-47 language tag (default: en-US).
            voice_name: Google TTS voice name (default: Neural2-D).
            speaking_rate: Speed multiplier 0.25–4.0 (default 0.95 — slightly slower for clarity).
            pitch: Pitch semitones -20.0 to 20.0 (default 0.0).

        Returns:
            Raw MP3 bytes ready to serve as audio/mpeg response.

        Raises:
            RuntimeError: When TTS is not configured or API call fails.
        """
        if not self.enabled:
            raise RuntimeError(
                "Google Cloud Text-to-Speech is not configured. "
                "Set GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS."
            )

        # Sanitize and truncate text
        clean_text = text.strip()[:4500]
        if not clean_text:
            raise ValueError("Text content cannot be empty")

        try:
            client = self._get_client()
            synthesis_input = _tts_module.SynthesisInput(text=clean_text)
            voice_params = _tts_module.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
            )
            audio_config = _tts_module.AudioConfig(
                audio_encoding=_tts_module.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
                effects_profile_id=["headphone-class-device"],
            )
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config,
            )
            logger.info("[TTS] Synthesized %d chars — %d bytes",
                        len(clean_text), len(response.audio_content))
            return response.audio_content

        except Exception as exc:
            logger.error("[TTS] Synthesis failed: %s", exc)
            raise RuntimeError(f"TTS synthesis failed: {exc}") from exc

    def synthesize_finding(self, plain_explanation: str, severity: str) -> bytes:
        """
        Produce TTS audio for a single risk finding.
        Prepends severity label for context.
        """
        text = f"Risk level: {severity}. {plain_explanation}"
        return self.synthesize(text)

    def synthesize_verdict(self, verdict: str, summary: str) -> bytes:
        """
        Produce TTS audio for the final verdict and executive summary.
        """
        text = f"Final verdict: {verdict}. {summary}"
        return self.synthesize(text)

    def is_available(self) -> bool:
        """Return True when TTS API credentials are present."""
        return self.enabled
