from __future__ import annotations
import sys
import os
from datetime import datetime
import pytest

# Force UTF-8 output on Windows (terminal may default to cp932/cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add 'tests/' to front of sys.path so 'config', 'pages', 'utils' are always found
# Must be before any project imports — use insert(0) for highest priority
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from playwright.sync_api import Browser, BrowserContext, Page

# Load .env nếu có — credentials sẽ available qua os.environ
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)  # không ghi đè env vars đã set sẵn (CI)
except ImportError:
    pass

import pages.base_page as _base_page
from utils.report_writer import ReportWriter
from config.environments import get_environment, Environment

# ── Constants ────────────────────────────────────────────────────────────────

REPORT_DIR = "tests/test_reports"
SCREENSHOT_DIR = "screenshots"
HEADLESS = os.getenv("CI", "false").lower() in ("1", "true", "yes")


# ── CLI option: --env ────────────────────────────────────────────────────────

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=os.getenv("TEST_ENV", "test"),
        help="Target environment: test (default) | prod",
    )


# ── Resolve environment once at session start ────────────────────────────────

_active_env: Environment | None = None


def _resolve_env(config) -> Environment:
    global _active_env
    if _active_env is None:
        env_name = config.getoption("--env")
        _active_env = get_environment(env_name)
    return _active_env


# ── pytest_configure — banner + dirs ─────────────────────────────────────────

def pytest_configure(config):
    """Print environment banner and ensure directories exist."""
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("tests/test_reports", exist_ok=True)

    # Register custom markers
    config.addinivalue_line("markers", "production: Test quan trọng trên môi trường Live")


def pytest_sessionstart(session):
    """Print environment banner at the very start of the test session."""
    env = _resolve_env(session.config)
    login_line = f"║  LOGIN: {env.login_email:<52}║" if env.login_email else "║  LOGIN: (không đăng nhập)                                   ║"
    banner = (
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        f"║  🌐 MÔI TRƯỜNG: {env.name.upper():<44}║\n"
        f"║  FE:    {env.fe_url:<53}║\n"
        f"║  API:   {env.api_url:<53}║\n"
        f"║  ADMIN: {env.admin_url:<53}║\n"
        f"  {login_line}\n"
        "╚══════════════════════════════════════════════════════════════╝"
    )
    try:
        print(banner)
    except UnicodeEncodeError:
        print(banner.encode("ascii", errors="replace").decode("ascii"))


# ── Auto-clear screenshots before each session ───────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def _clear_screenshots() -> None:
    """Xóa toàn bộ screenshots cũ trước khi chạy session mới."""
    import shutil
    shot_dir = os.path.join(os.getcwd(), "screenshots")
    if os.path.exists(shot_dir):
        shutil.rmtree(shot_dir)
    os.makedirs(shot_dir, exist_ok=True)
    try:
        print("\n[INFO] Screenshots cũ đã được xóa. Sẵn sàng chụp mới.")
    except UnicodeEncodeError:
        print("\n[INFO] Screenshots cleared. Ready for new captures.")

# ── Session-scoped report ────────────────────────────────────────────────────

_report = ReportWriter(output_dir=REPORT_DIR)


@pytest.fixture(scope="session")
def report() -> ReportWriter:
    yield _report
    paths = _report.save()
    print(f"\n[Report] Files: {paths}")


# ── Environment fixtures ─────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def env(request) -> Environment:
    """Active environment config — inject anywhere you need URLs."""
    return _resolve_env(request.config)


@pytest.fixture(scope="session")
def base_url(request) -> str:
    """FE base URL — resolved from --env flag or TEST_ENV env var."""
    cli_val = request.config.getoption("--base-url", default=None)
    if cli_val:
        return cli_val
    return _resolve_env(request.config).fe_url


@pytest.fixture(scope="session")
def api_url(request) -> str:
    """API base URL for the active environment."""
    return _resolve_env(request.config).api_url


@pytest.fixture(scope="session")
def admin_url(request) -> str:
    """Admin panel URL for the active environment."""
    return _resolve_env(request.config).admin_url


# ── Browser context — desktop ────────────────────────────────────────────────

@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    context: BrowserContext = browser.new_context(
        locale="vi-VN",
        timezone_id="Asia/Ho_Chi_Minh",
        viewport={"width": 1440, "height": 900},
        record_video_dir=f"{REPORT_DIR}/videos" if not HEADLESS else None,
    )
    context.set_default_timeout(30_000)
    pg = context.new_page()
    yield pg
    context.close()


# ── Mobile context — iPhone 12 Pro ──────────────────────────────────────────

@pytest.fixture(scope="function")
def mobile_page(browser: Browser) -> Page:
    context = browser.new_context(
        locale="vi-VN",
        viewport={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        ),
        is_mobile=True,
        has_touch=True,
    )
    context.set_default_timeout(30_000)
    pg = context.new_page()
    yield pg
    context.close()


# ── Tablet context — iPad ────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def tablet_page(browser: Browser) -> Page:
    context = browser.new_context(
        locale="vi-VN",
        viewport={"width": 768, "height": 1024},
        is_mobile=True,
        has_touch=True,
    )
    context.set_default_timeout(30_000)
    pg = context.new_page()
    yield pg
    context.close()


# ── Android context — 360x740 ────────────────────────────────────────────────

@pytest.fixture(scope="function")
def android_page(browser: Browser) -> Page:
    context = browser.new_context(
        locale="vi-VN",
        viewport={"width": 360, "height": 740},
        is_mobile=True,
        has_touch=True,
    )
    context.set_default_timeout(30_000)
    pg = context.new_page()
    yield pg
    context.close()


# ── Page Object Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def home_page(page: Page, base_url: str) -> _base_page.BasePage:
    from pages.home_page import HomePage
    return HomePage(page, base_url)


@pytest.fixture
def studio_page(page: Page, base_url: str) -> _base_page.BasePage:
    from pages.studio_page import StudioPage
    return StudioPage(page, base_url)


@pytest.fixture
def auth_page(page: Page, base_url: str) -> _base_page.BasePage:
    from pages.auth_modal_page import AuthModalPage
    return AuthModalPage(page, base_url)


@pytest.fixture
def checkout_page(page: Page, base_url: str) -> _base_page.BasePage:
    from pages.checkout_page import CheckoutPage
    return CheckoutPage(page, base_url)


@pytest.fixture
def product_list_page(page: Page, base_url: str) -> _base_page.BasePage:
    from pages.product_page import ProductListPage
    return ProductListPage(page, base_url)


@pytest.fixture
def product_detail_page(page: Page, base_url: str) -> _base_page.BasePage:
    from pages.product_page import ProductDetailPage
    return ProductDetailPage(page, base_url)
