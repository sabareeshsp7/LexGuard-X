import os
from dotenv import load_dotenv

load_dotenv()


class StorageClient:
    """
    Google Cloud Storage client for persisting contracts and reports.
    Gracefully no-ops when GCS is not configured.
    """

    def __init__(self):
        self.contracts_bucket = os.getenv("GCS_CONTRACTS_BUCKET", "")
        self.reports_bucket = os.getenv("GCS_REPORTS_BUCKET", "")
        self._client = None
        # On Cloud Run, K_SERVICE is set — ADC handles auth automatically (no key file needed)
        _is_cloud_run = bool(os.getenv("K_SERVICE"))
        _creds_ok = os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json")) or _is_cloud_run
        self.enabled = bool(self.contracts_bucket and _creds_ok)

    def _get_client(self):
        if self._client is None:
            from google.cloud import storage
            self._client = storage.Client()
        return self._client

    def upload_contract(self, file_bytes: bytes, filename: str, analysis_id: str) -> str:
        """Upload contract to GCS. Returns public/signed URL."""
        if not self.enabled:
            print("[GCS] Not configured. Skipping upload.")
            return f"local://{analysis_id}/{filename}"

        try:
            client = self._get_client()
            bucket = client.bucket(self.contracts_bucket)
            blob_name = f"contracts/{analysis_id}/{filename}"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(file_bytes, content_type="application/octet-stream")
            url = f"gs://{self.contracts_bucket}/{blob_name}"
            print(f"[GCS] Uploaded contract: {url}")
            return url
        except Exception as e:
            print(f"[GCS] Upload error: {e}")
            return f"local://{analysis_id}/{filename}"

    def upload_report(self, report_data: str, analysis_id: str) -> str:
        """Upload JSON report to GCS."""
        if not self.enabled or not self.reports_bucket:
            return f"local://reports/{analysis_id}.json"

        try:
            client = self._get_client()
            bucket = client.bucket(self.reports_bucket)
            blob_name = f"reports/{analysis_id}.json"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(report_data, content_type="application/json")
            url = f"gs://{self.reports_bucket}/{blob_name}"
            print(f"[GCS] Uploaded report: {url}")
            return url
        except Exception as e:
            print(f"[GCS] Report upload error: {e}")
            return f"local://reports/{analysis_id}.json"
