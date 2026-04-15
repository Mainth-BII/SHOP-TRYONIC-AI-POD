"""Pytest fixtures shared across all Tryonic tests."""

import os
from datetime import datetime
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

import pages.base_page as _base_page
from utils.report_writer import ReportWriter

# ── Constants ────────────────────────────────────────────────────────────────

BASE_URL = os.getenv("BASE_URL", "https://pre-launch.tryonic.ai")
HEADLESS = os.getenv("CI", "false").lower() in ("1", "true", "yes")

# ── Screenshot run directory ─────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def _setup_run_dir() -> None:
    """
    Create screenshots/DD-MM-YYYY/Lan_N/ for this session and wire it
    into BasePage.SESSION_RUN_DIR so every take_screenshot() call lands there.

    Lần 1 = first run of the day (08:00), Lần 2 = second run (16:00).
    """
    date_str = datetime.now().strftime("%d-%m-%Y")
    date_folder = os.path.join("screenshots", date_str)
    os.makedirs(date_folder, exist_ok=True)

    existing = [
        d for d in os.listdir(date_folder)
        if os.path.isdir(os.path.join(date_folder, d)) and d.startswith("Lan_")
    ]
    run_num = len(existing) + 1
    run_dir = os.path.join(date_str, f"Lan_{run_num}")
    os.makedirs(os.path.join("screenshots", run_dir), exist_ok=True)

    _base_page.SESSION_RUN_DIR = run_dir
    print(f"\n[INFO] Screenshots: screenshots/{run_dir}/")


# ── Session-scoped report ────────────────────────────────────────────────────

_report = ReportWriter(output_dir="test_reports")


@pytest.fixture(scope="session")
def report() -> ReportWriter:
    yield _report
    paths = _report.save()
    print(f"\n[Report] Files: {paths}")


# ── Base URL ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def base_url(request) -> str:
    # pytest-playwright also provides base_url from --base-url flag.
    # Fall back to our constant if not supplied via CLI.
    cli_val = request.config.getoption("--base-url", default=None)
    return cli_val or BASE_URL


# ── Browser context — desktop ────────────────────────────────────────────────

@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    context: BrowserContext = browser.new_context(
        locale="vi-VN",
        timezone_id="Asia/Ho_Chi_Minh",
        viewport={"width": 1440, "height": 900},
        record_video_dir="test_reports/videos" if not HEADLESS else None,
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


# ── pytest-playwright options ────────────────────────────────────────────────

def pytest_configure(config):  # noqa: ARG001
    """Ensure screenshots folder exists."""
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("test_reports", exist_ok=True)
