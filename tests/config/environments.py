"""Environment configuration for Tryonic QA test suite.

Usage:
    pytest --env=test   → chạy trên môi trường TEST
    pytest --env=prod   → chạy trên môi trường PRODUCTION (login mainth@bccii.co.jp)
    pytest              → mặc định TEST (an toàn)

Hoặc set env var: TEST_ENV=prod pytest ...
"""

import os

# Load .env TRƯỚC khi định nghĩa constants (os.getenv dùng ngay bên dưới)
try:
    from pathlib import Path
    from dotenv import load_dotenv
    _dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=_dotenv_path, override=False)
except ImportError:
    pass
from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    """Holds all URLs and default credentials for a specific environment."""
    name: str
    fe_url: str
    api_url: str
    admin_url: str
    login_email: str = ""
    login_password: str = ""
    admin_email: str = ""
    admin_password: str = ""
    affiliate_email: str = ""      # tài khoản affiliate (đã được duyệt)
    affiliate_password: str = ""
    customer_email: str = ""       # tài khoản khách hàng mua qua link affiliate
    customer_password: str = ""

    def __str__(self) -> str:
        email_hint = f" | LOGIN={self.login_email}" if self.login_email else ""
        return (
            f"[{self.name.upper()}] "
            f"FE={self.fe_url} | API={self.api_url} | ADMIN={self.admin_url}"
            f"{email_hint}"
        )


# ── Environment definitions ──────────────────────────────────────────────────

TEST = Environment(
    name="test",
    fe_url="https://test.shop.tryonic.ai",
    api_url="https://api.test.shop.tryonic.ai",
    admin_url="https://admin.test.shop.tryonic.ai",
    login_email=os.getenv("DAILY_TEST_EMAIL", ""),
    login_password=os.getenv("DAILY_TEST_PASSWORD", ""),
    admin_email=os.getenv("ADMIN_TEST_EMAIL", ""),
    admin_password=os.getenv("ADMIN_TEST_PASSWORD", ""),
    affiliate_email=os.getenv("AFFILIATE_EMAIL", ""),
    affiliate_password=os.getenv("AFFILIATE_PASSWORD", ""),
    customer_email=os.getenv("CUSTOMER_EMAIL", ""),
    customer_password=os.getenv("CUSTOMER_PASSWORD", ""),
)

PROD = Environment(
    name="prod",
    fe_url="https://shop.tryonic.ai",
    api_url="https://api.shop.tryonic.ai",
    admin_url="https://admin.shop.tryonic.ai",
    login_email=os.getenv("PROD_EMAIL", ""),
    login_password=os.getenv("PROD_PASSWORD", ""),
    admin_email=os.getenv("ADMIN_TEST_EMAIL", ""),
    admin_password=os.getenv("ADMIN_TEST_PASSWORD", ""),
    affiliate_email=os.getenv("AFFILIATE_EMAIL", ""),
    affiliate_password=os.getenv("AFFILIATE_PASSWORD", ""),
    customer_email=os.getenv("CUSTOMER_EMAIL", ""),
    customer_password=os.getenv("CUSTOMER_PASSWORD", ""),
)

# ── Lookup ────────────────────────────────────────────────────────────────────

_ENVS = {
    "test": TEST,
    "staging": TEST,   # alias
    "prod": PROD,
    "production": PROD,  # alias
    "live": PROD,       # alias
}


def get_environment(name: str) -> Environment:
    """Resolve environment by name. Raises ValueError if unknown."""
    key = name.strip().lower()
    if key not in _ENVS:
        valid = ", ".join(sorted(set(e.name for e in _ENVS.values())))
        raise ValueError(
            f"Unknown environment '{name}'. Valid: {valid}"
        )
    return _ENVS[key]
