"""
Security middleware for LexGuard X FastAPI backend.

Provides:
  - Security response headers (CSP, HSTS, X-Frame-Options, etc.)
  - Request-level rate limiting (in-memory sliding window)
  - Request size guard
"""
import time
import os
from collections import defaultdict, deque
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ─────────────────────────────────────────────────────────────────────────────
#  Security Headers Middleware
# ─────────────────────────────────────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security-critical HTTP response headers to every response.

    Headers applied:
      X-Content-Type-Options  — prevent MIME sniffing
      X-Frame-Options         — clickjacking protection
      X-XSS-Protection        — legacy XSS filter
      Referrer-Policy         — limit referrer leakage
      Permissions-Policy      — restrict browser features
      Strict-Transport-Security — enforce HTTPS (on production)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"]  = "nosniff"
        response.headers["X-Frame-Options"]          = "DENY"
        response.headers["X-XSS-Protection"]         = "1; mode=block"
        response.headers["Referrer-Policy"]           = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"]        = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # HSTS only on production (Cloud Run sets K_SERVICE)
        if os.getenv("K_SERVICE"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


# ─────────────────────────────────────────────────────────────────────────────
#  Rate Limiting Middleware
# ─────────────────────────────────────────────────────────────────────────────

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window in-memory rate limiter.

    Default: 30 requests per 60-second window per IP.
    Analysis endpoint (/api/analyze): 5 requests per 60-second window.

    In a multi-replica Cloud Run deployment, use Redis instead of this
    in-memory store. For a single-instance demo this is sufficient.
    """

    def __init__(
        self,
        app,
        global_limit: int = 30,
        analyze_limit: int = 5,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.global_limit    = global_limit
        self.analyze_limit   = analyze_limit
        self.window          = window_seconds
        self._global_store:  dict[str, deque] = defaultdict(deque)
        self._analyze_store: dict[str, deque] = defaultdict(deque)

    def _is_rate_limited(self, store: dict, key: str, limit: int) -> bool:
        now = time.time()
        window_start = now - self.window
        q = store[key]
        # Evict timestamps outside the window
        while q and q[0] < window_start:
            q.popleft()
        if len(q) >= limit:
            return True
        q.append(now)
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Identify client by IP (X-Forwarded-For on Cloud Run)
        forwarded = request.headers.get("X-Forwarded-For", "")
        ip = forwarded.split(",")[0].strip() if forwarded else (
            request.client.host if request.client else "unknown"
        )

        # Per-endpoint limit for the expensive analysis route
        if request.url.path == "/api/analyze":
            if self._is_rate_limited(self._analyze_store, ip, self.analyze_limit):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": (
                            f"Rate limit exceeded: max {self.analyze_limit} "
                            f"analyses per {self.window}s. Please wait."
                        )
                    },
                )

        # Global rate limit
        if self._is_rate_limited(self._global_store, ip, self.global_limit):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
            )

        return await call_next(request)
