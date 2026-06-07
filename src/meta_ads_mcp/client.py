import os
import threading
import time
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

load_dotenv()

_api_initialized = False
_ad_account: AdAccount | None = None
_account_currency: str | None = None
_rate_limiter: "MetaRateLimiter | None" = None


class MetaRateLimiter:
    """Small point bucket for Meta Marketing API development-tier throttling."""

    def __init__(self, max_score: int, decay_seconds: int, enabled: bool = True) -> None:
        self.max_score = max_score
        self.decay_seconds = decay_seconds
        self.enabled = enabled
        self._available = float(max_score)
        self._last_checked = time.monotonic()
        self._lock = threading.Lock()

    @property
    def _points_per_second(self) -> float:
        return self.max_score / self.decay_seconds

    def acquire(self, points: int) -> None:
        if not self.enabled:
            return

        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last_checked
                self._available = min(self.max_score, self._available + elapsed * self._points_per_second)
                self._last_checked = now

                if self._available >= points:
                    self._available -= points
                    return

                needed = points - self._available
                wait_seconds = needed / self._points_per_second

            time.sleep(max(wait_seconds, 0.1))


def get_rate_limiter() -> MetaRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        enabled = os.environ.get("META_API_RATE_LIMIT_ENABLED", "true").lower() not in {"0", "false", "no"}
        max_score = int(os.environ.get("META_API_RATE_LIMIT_MAX_SCORE", "60"))
        decay_seconds = int(os.environ.get("META_API_RATE_LIMIT_DECAY_SECONDS", "300"))
        _rate_limiter = MetaRateLimiter(max_score=max_score, decay_seconds=decay_seconds, enabled=enabled)
    return _rate_limiter


def throttle_meta_api(points: int = 1) -> None:
    get_rate_limiter().acquire(points)


def throttle_read() -> None:
    throttle_meta_api(1)


def throttle_write() -> None:
    throttle_meta_api(3)


def get_ad_account() -> AdAccount:
    global _api_initialized, _ad_account

    if not _api_initialized:
        app_id = os.environ["META_APP_ID"]
        app_secret = os.environ["META_APP_SECRET"]
        access_token = os.environ["META_ACCESS_TOKEN"]
        FacebookAdsApi.init(app_id, app_secret, access_token, api_version="v25.0")
        _api_initialized = True

    if _ad_account is None:
        account_id = os.environ["META_AD_ACCOUNT_ID"]
        _ad_account = AdAccount(account_id)

    return _ad_account


def get_account_currency() -> str:
    global _account_currency
    if _account_currency is None:
        account = get_ad_account()
        throttle_read()
        account.api_get(fields=[AdAccount.Field.currency])
        _account_currency = account[AdAccount.Field.currency]
    return _account_currency
