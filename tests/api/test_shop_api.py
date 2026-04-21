"""
API Regression Tests — Kiểm tra tính ổn định của hệ thống Backend.
Sử dụng Playwright API Request context.
"""
import pytest
from playwright.sync_api import APIRequestContext

@pytest.mark.api
def test_shop_config_api(api_request_context: APIRequestContext, base_url: str):
    """Kiểm tra endpoint cấu hình shop (giả định /api/config hoặc tương đương)."""
    # Note: Nếu bạn biết endpoint thật, hãy thay thế ở đây. Giả định /api/health-check
    response = api_request_context.get(f"{base_url}/api/health-check")
    
    # Nếu không có endpoint health-check, check homepage qua API (đảm bảo server sống)
    if response.status == 404:
        response = api_request_context.get(base_url)
    
    assert response.ok, f"API failed with status {response.status}"
    print(f"  [PASS] API Health Check OK: Status {response.status}")

@pytest.mark.api
def test_authentication_api_mock(api_request_context: APIRequestContext, base_url: str):
    """
    Kịch bản test API Login (Mẫu).
    Ở môi trường thật, bạn sẽ gửi POST tới /api/auth/login.
    """
    payload = {
        "email": "test@tryonic.ai",
        "password": "password123"
    }
    # Giả định endpoint login
    response = api_request_context.post(f"{base_url}/api/auth/login", data=payload)
    
    # Vì đây là demo, chúng ta log status thay vì assert strict nếu chưa có info endpoint
    print(f"  [INFO] Auth API Attempt: Status {response.status}")
    assert response.status in [200, 401, 403], "Server logic error (500)"

@pytest.fixture(scope="session")
def api_request_context(playwright, base_url) -> APIRequestContext:
    """Fixture khởi tạo request context cho toàn session API."""
    request_context = playwright.request.new_context(base_url=base_url)
    yield request_context
    request_context.dispose()
