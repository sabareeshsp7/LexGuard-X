"""
Google Cloud Natural Language API client.
Provides entity extraction and content classification
to enrich contract analysis with structured NLP data.
"""

import os
import logging
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Guard: google-cloud-language may not be installed
try:
    from google.cloud import language_v2 as _language_v2  # type: ignore
    _NLP_AVAILABLE = True
except ImportError:
    _NLP_AVAILABLE = False
    _language_v2 = None  # type: ignore
    logger.warning("[NLP] google-cloud-language not installed — NLP enrichment disabled")


class NLPClient:
    """
    Google Cloud Natural Language API wrapper.

    Capabilities used:
      - Entity recognition  (persons, orgs, money, dates, legal terms)
      - Content classification (contract topic detection)
      - Syntax analysis (sentence boundaries for smarter chunking)
    """

    def __init__(self):
        self.credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json"
        )
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self._client = None
        # On Cloud Run, K_SERVICE is set — ADC handles auth automatically
        _is_cloud_run = bool(os.getenv("K_SERVICE"))
        self.enabled = (
            _NLP_AVAILABLE
            and bool(self.project_id)
            and (os.path.exists(self.credentials_path) or _is_cloud_run)
        )

    def _get_client(self):
        """Lazy-initialize the NLP client."""
        if self._client is None:
            self._client = _language_v2.LanguageServiceClient()
            logger.info("[NLP] Cloud Natural Language client initialized")
        return self._client

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from contract text.
        Returns a list of dicts: name, type, salience, metadata.
        """
        if not self.enabled:
            return []

        try:
            client = self._get_client()
            document = _language_v2.Document(
                content=text[:10000],
                type_=_language_v2.Document.Type.PLAIN_TEXT,
            )
            response = client.analyze_entities(
                document=document,
                encoding_type=_language_v2.EncodingType.UTF8,
            )

            entities = [
                {
                    "name": entity.name,
                    "type": _language_v2.Entity.Type(entity.type_).name,
                    "salience": round(entity.salience, 4),
                    "metadata": dict(entity.metadata),
                }
                for entity in response.entities
            ]
            logger.info("[NLP] Extracted %d entities", len(entities))
            return entities

        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "403" in str(exc):
                logger.warning("[NLP] API disabled in GCP project. Disabling NLP enrichment.")
                self.enabled = False
            else:
                logger.error("[NLP] Entity extraction failed: %s", exc)
            return []

    def classify_content(self, text: str) -> List[Dict]:
        """Classify the contract into Google content categories."""
        if not self.enabled:
            return []

        try:
            client = self._get_client()
            document = _language_v2.Document(
                content=text[:5000],
                type_=_language_v2.Document.Type.PLAIN_TEXT,
            )
            response = client.classify_text(document=document)
            categories = [
                {"name": cat.name, "confidence": round(cat.confidence, 4)}
                for cat in response.categories
            ]
            logger.info("[NLP] Classified into %d categories", len(categories))
            return categories

        except Exception as exc:
            logger.error("[NLP] Content classification failed: %s", exc)
            return []

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze overall contract sentiment.
        Returns: { score: float[-1,1], magnitude: float[0,inf] }
        """
        if not self.enabled:
            return {"score": 0.0, "magnitude": 0.0}

        try:
            client = self._get_client()
            document = _language_v2.Document(
                content=text[:10000],
                type_=_language_v2.Document.Type.PLAIN_TEXT,
            )
            response = client.analyze_sentiment(document=document)
            sentiment = response.document_sentiment
            result = {
                "score": round(sentiment.score, 4),
                "magnitude": round(sentiment.magnitude, 4),
            }
            logger.info("[NLP] Sentiment: score=%.2f magnitude=%.2f",
                        result["score"], result["magnitude"])
            return result

        except Exception as exc:
            if "SERVICE_DISABLED" in str(exc) or "403" in str(exc):
                logger.warning("[NLP] API disabled in GCP project. Disabling NLP enrichment.")
                self.enabled = False
            else:
                logger.error("[NLP] Sentiment analysis failed: %s", exc)
            return {"score": 0.0, "magnitude": 0.0}

    def is_available(self) -> bool:
        """Return True when NLP API credentials are present."""
        return self.enabled
