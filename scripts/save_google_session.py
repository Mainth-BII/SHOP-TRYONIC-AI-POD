"""
Script tạo Google session một lần duy nhất.

Chạy: python scripts/save_google_session.py

Luồng:
  1. Script mở Chrome BÌNH THƯỜNG (không qua Playwright) — Google không chặn
  2. Bạn tự đăng nhập Google trong Chrome đó
  3. Script tự phát hiện khi login xong → kết nối CDP → lưu cookies
  4. TC_044 dùng session này

Ghi chú:
  - auth_state/ đã gitignore
  - Khi session hết hạn (~30 ngày), chạy lại script này
"""
import os
import sys
import time
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

_ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_DIR  = os.path.join(_ROOT, "auth_state", "chrome_profile")
SESSION_PATH = os.path.join(_ROOT, "auth_state", "google_session.json")
BASE_URL     = "https://shop.tryonic.ai"
DEBUG_PORT   = 9222


def find_chrome():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "Khong tim thay Chrome. Hay cai Chrome tai: https://www.google.com/chrome/"
    )


def kill_existing_chrome():
    """Kill Chrome đang chạy để tránh xung đột --remote-debugging-port."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "chrome.exe"],
            capture_output=True, timeout=5
        )
        time.sleep(2)
        print("  [INFO] Da kill Chrome cu.")
    except Exception:
        pass


def main():
    os.makedirs(PROFILE_DIR, exist_ok=True)

    print("=" * 60)
    print("  SETUP GOOGLE SESSION CHO TC_044")
    print("=" * 60)

    chrome = find_chrome()
    print(f"\nChrome: {chrome}")
    print(f"Profile: {PROFILE_DIR}")

    # Kill Chrome cũ để tránh xung đột port
    kill_existing_chrome()

    # Mở Chrome BÌNH THƯỜNG với remote debugging — không phải Playwright
    proc = subprocess.Popen([
        chrome,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        BASE_URL,
    ])
    print(f"\nChrome da mo (PID={proc.pid})")
    print("\n>>> Hay thuc hien trong Chrome vua mo: <<<")
    print("  1. Click [Dang nhap] tren header")
    print("  2. Click [Tiep tuc voi Google]")
    print("  3. Hoan thanh dang nhap Google")
    print("  4. Script tu dong luu khi phat hien dang nhap (toi da 3 phut)\n")

    # Cho Chrome khoi dong day du (tang len 8s)
    time.sleep(8)

    # Ket noi Playwright qua CDP — retry toi da 5 lan
    with sync_playwright() as p:
        browser = None
        for attempt in range(5):
            try:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{DEBUG_PORT}")
                print(f"  [INFO] Ket noi CDP thanh cong (lan {attempt + 1})")
                break
            except Exception as e:
                print(f"  [RETRY] CDP lan {attempt + 1} that bai: {e}")
                time.sleep(3)

        if not browser:
            print(f"[ERROR] Khong the ket noi Chrome sau 5 lan thu.")
            proc.terminate()
            return

        context = browser.contexts[0] if browser.contexts else None
        if not context:
            print("[ERROR] Khong tim thay browser context.")
            browser.disconnect()
            proc.terminate()
            return

        page = context.pages[0] if context.pages else context.new_page()
        if page.url != BASE_URL:
            try:
                page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
            except Exception:
                pass

        # Poll cho den khi dang nhap thanh cong
        logged_in = False
        for tick in range(90):  # 90 x 2s = 180s
            try:
                is_login_btn = page.locator(
                    "header :text('Dang nhap'), header button:has-text('Dang nhap'), "
                    "header :text('Đăng nhập')"
                ).first.is_visible(timeout=1000)
            except Exception:
                is_login_btn = True

            if not is_login_btn:
                logged_in = True
                print(f"\n[OK] Phat hien dang nhap thanh cong sau {(tick + 1) * 2}s!")
                break

            remaining = 180 - (tick + 1) * 2
            print(f"  Cho dang nhap... {remaining}s con lai", end="\r")
            time.sleep(2)

        if not logged_in:
            print("\n[WARN] Timeout 3 phut — chua phat hien dang nhap. Luu session hien tai.")

        time.sleep(1)

        # Luu cookies/localStorage
        context.storage_state(path=SESSION_PATH)
        # CDP-connected browser dùng close() thay vì disconnect()
        try:
            browser.close()
        except Exception:
            pass

    proc.terminate()
    print(f"\n[DONE] Session da luu -> {SESSION_PATH}")
    print("TC_044 se dung file nay de bo qua buoc Google OAuth.\n")


if __name__ == "__main__":
    main()
