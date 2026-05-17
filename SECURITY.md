# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security vulnerability in LexGuard X, please **do not** open a public GitHub issue.

Instead, please report it responsibly by emailing: **security@lexguard-x.dev**

You will receive a response within **48 hours**, and we will work with you to:
1. Confirm and reproduce the vulnerability
2. Develop and test a fix
3. Release a patched version
4. Credit you in the release notes (if you wish)

## Security Architecture

### Secrets Management
- All API keys and credentials are managed via environment variables — **never hardcoded**
- GCP Service Account keys are excluded from Git via `.gitignore`
- Cloud Run uses **Workload Identity (ADC)** — no credential files in containers

### Input Validation
- File type validated by MIME type and magic-byte signature inspection
- File size capped at `MAX_FILE_SIZE_MB` (default 20 MB)
- All analysis IDs validated as UUID4 before use
- Filenames sanitized to prevent path traversal attacks

### API Security
- **CORS** restricted to known origins (Firebase Hosting + localhost for dev)
- **Rate limiting**: 60 req/min global, 10 analyses/min per IP (sliding window)
- **Security headers** on every response:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security` (HSTS, Cloud Run production only)
  - `Permissions-Policy` — restricts camera, mic, geolocation, payment

### Data Privacy
- Uploaded contracts are **not permanently stored locally** — they are streamed to Google Cloud Storage and immediately deleted from the server
- No PII is logged — analysis IDs are UUID4 with no correlation to users
- NLP and Vision analysis is performed in-region (`us-central1`)

### Dependency Security
- Dependencies are pinned to minimum compatible versions
- `bandit` SAST scan runs on every CI push
- Regular dependency updates recommended via `pip-audit`

## OWASP Compliance Notes

The following OWASP Top 10 (2021) mitigations are implemented:

| Risk | Mitigation |
|------|-----------|
| A01 Broken Access Control | CORS, rate limiting, UUIDs |
| A02 Cryptographic Failures | HTTPS enforced (HSTS), no plaintext secrets |
| A03 Injection | Input sanitization, parameterized Firestore queries |
| A04 Insecure Design | Threat-modeled architecture, fail-safe defaults |
| A05 Security Misconfiguration | Security headers middleware, ADC over key files |
| A06 Vulnerable Components | Pinned dependencies, Bandit CI scan |
| A07 Auth/Identity Failures | Rate limiting, IP-based abuse prevention |
| A09 Logging/Monitoring Failures | Google Cloud Logging on all API operations |
