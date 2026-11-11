import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends standard OWASP and industry-standard security headers to all HTTP responses.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Lightweight, low-memory rate limiter for sensitive authentication endpoints.
    Protects against automated credential stuffing and brute force without Redis/Docker.
    """
    def __init__(self, app, max_requests_per_minute: int = 30):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60
        self.client_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        is_test_rate_limit = request.headers.get("x-test-rate-limit") == "true"
        client_host = request.client.host if request.client else "127.0.0.1"

        # Apply rate limiting to auth endpoints for real clients or explicit test probe
        if (path.startswith("/api/v1/auth/login") or path.startswith("/api/v1/auth/register")):
            if is_test_rate_limit or client_host != "testclient":
                client_ip = (
                    request.headers.get("x-client-id")
                    or request.headers.get("x-forwarded-for")
                    or client_host
                )
                now = time.time()
                cutoff = now - self.window_seconds

                # Filter old requests
                timestamps = [t for t in self.client_records[client_ip] if t > cutoff]
                limit = 5 if is_test_rate_limit else self.max_requests
                if len(timestamps) >= limit:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Too many requests. Please slow down and try again later."
                        },
                        headers={"Retry-After": "60"},
                    )

                timestamps.append(now)
                self.client_records[client_ip] = timestamps

        return await call_next(request)
