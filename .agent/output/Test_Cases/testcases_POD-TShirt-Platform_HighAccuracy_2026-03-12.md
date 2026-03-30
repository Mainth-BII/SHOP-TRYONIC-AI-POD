# Test Cases: POD T-Shirt Platform (High-Accuracy v2.0)

**Project:** POD T-Shirt Platform Phase 1 MVP  
**Standard:** 15-Field Professional Schema  
**Source:** Confluence Synchronized Specifications (2026-03-12)

## 1. Authentication & Session Management (FR-01, FR-02)

| TC_ID | Title | Module | Source | Priority | Type | Scope | Preconditions | Steps | Expected Result | Test Data | Browser | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| AUTH-001 | Email Registration | Auth | FR-01.1 | P1 | Functional | Smoke | Browser open | 1. Navigate to `/register`<br>2. Enter valid email/pwd<br>3. Submit | 1. Account created in 'Inactive' status<br>2. Verification email N-02 sent<br>3. Redirect to Success message | user@example.com | Desktop | Draft |
| AUTH-002 | Access Token Expiry | Auth | FR-02.2 | P1 | Security | Regression | Logged in | 1. Wait 15 minutes<br>2. Click 'My Profile' | 1. JWT Access Token expires<br>2. System uses Refresh Token to auto-renew session<br>3. Profile loads without re-login | Valid Session | All | Draft |
| AUTH-003 | Refresh Token Persistence | Auth | FR-02.3 | P2 | Functional | Regression | Logged in | 1. Close browser<br>2. Wait 2 days<br>3. Reopen app | 1. User remains logged in (Refresh Token valid for 7d)<br>2. No login prompt shown | Valid Session | All | Draft |
| AUTH-004 | Guest Mode Expiry | Auth | FR-02.8 | P2 | Functional | Edge | Guest user | 1. Add item to cart<br>2. Wait 7 days<br>3. Reopen app | 1. localStorage cleared<br>2. Cart is empty (Guest session expired) | localStorage set | All | Draft |
| AUTH-005 | Checkout Migration (Guest to User) | Auth | FR-02.10 | P1 | Functional | Smoke | Guest with 2 items | 1. Click Checkout<br>2. Register new account | 1. localStorage items moved to `cart_items` table<br>2. Checkout continues with items preserved | Guest Cart | All | Draft |
| AUTH-006 | Password Policy Validation | Auth | FR-01.3 | P3 | Functional | Regression | Register page | 1. Enter '123' as pwd | 1. Error: "Min 8 chars, 1 upper, 1 number"<br>2. Submit disabled | pwd=123 | Desktop | Draft |

## 2. AI Artwork Workflow (FR-14, FR-15)

| TC_ID | Title | Module | Source | Priority | Type | Scope | Preconditions | Steps | Expected Result | Test Data | Browser | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| AI-001 | Welcome Credit Bonus | Credits | FR-15.9 | P1 | Functional | Smoke | New Registration | 1. Finish signup | 1. `user_credits` table initialized with **5 credits** | New User | All | Draft |
| AI-002 | Generation Cost Logic | AI | FR-15.3 | P1 | Functional | Smoke | 10 credits | 1. Enter prompt<br>2. Click Generate | 1. **5 credits** deducted<br>2. 2-4 variations (512px) rendered | "Cyberpunk Dragon" | All | Draft |
| AI-003 | Upscale Cost Logic | AI | FR-15.3 | P1 | Functional | Smoke | Variation chosen | 1. Select img<br>2. Click Upscale | 1. **3 credits** deducted<br>2. High-res (2048px) img generated | Selected Img | All | Draft |
| AI-004 | Insufficient Credits Gen | AI | FR-15.4 | P2 | Functional | Edge | 4 credits | 1. Click Generate | 1. Error: "Need 5 credits"<br>2. Redirect to 'Buy Credits' | 4 credits | All | Draft |
| AI-005 | Daily Quota Breach | AI | FR-14.6 | P2 | Functional | Edge | 10 gens today | 1. Attempt 11th gen | 1. Error: "Daily limit (10) reached"<br>2. No credits deducted | Maxed User | All | Draft |
| AI-006 | Prompt Translation (VN->EN) | AI | FR-14.2 | P3 | Functional | Regression | VN Input | 1. Enter "Con hổ xanh" | 1. API payload shows translated "Blue tiger" | Con hổ xanh | All | Draft |

## 3. Product & Fit-Size Intelligence (FR-05, FR-13)

| TC_ID | Title | Module | Source | Priority | Type | Scope | Preconditions | Steps | Expected Result | Test Data | Browser | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FIT-001 | BMI Size Suggestion | Shop | FR-13.3 | P1 | Functional | Smoke | Detail Page | 1. Input 175cm/70kg/M | 1. Suggest "Size L"<br>2. Confidence Score shown (e.g. 94%) | 175, 70, Male | All | Draft |
| FIT-002 | Fit Suggestion Visuals | Shop | BR-FIT-02 | P3 | UI | Visual | Calculation done | 1. View results | 1. "Aha moment" rotating messages show for 2.5s | Loading state | Mobile | Draft |
| PROD-001 | Multi-Neck Selection | Shop | FR-05.1 | P2 | Functional | Smoke | Product List | 1. Choose Polo vs V-neck | 1. Mockup updates correctly<br>2. Price diff (if any) reflected | Polo vs V | All | Draft |

## 4. Design Editor (Canvas) (FR-07)

| TC_ID | Title | Module | Source | Priority | Type | Scope | Preconditions | Steps | Expected Result | Test Data | Browser | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ED-001 | Safe Zone Enforcement | Editor | FR-07.6 | P1 | UI/Func | Smoke | Img on canvas | 1. Drag img over sleeve | 1. Red warning overlay appears<br>2. "Vượt vùng in" tooltip shown | Oversize Img | Desktop | Draft |
| ED-002 | Canvas Auto-Save | Editor | FR-07.9 | P2 | Functional | Regression | Edits made | 1. Wait 30 seconds | 1. Status bottom-right: "Đã lưu nháp"<br>2. `designs` table updated | Idle 30s | All | Draft |

## 5. Orders & Payments (FR-09, FR-10)

| TC_ID | Title | Module | Source | Priority | Type | Scope | Preconditions | Steps | Expected Result | Test Data | Browser | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| PAY-001 | VNPay Successful Callback | Payment | FR-10.3 | P1 | Functional | Smoke | Order Pending | 1. Complete VNPay payment | 1. Order status -> "Confirmed"<br>2. Email N-07 sent | Success Return | All | Draft |
| PAY-002 | Earn Credit on Delivery | Credits | FR-15.2 | P1 | Functional | Regression | Status: Shipped | 1. Admin -> Delivered | 1. **+10 credits** added to wallet<br>2. Notification N-22 | Delivered | All | Draft |
| ORD-001 | Order Expiry Logic | Order | BR-ORD-04 | P2 | Functional | Edge | Unpaid Order | 1. Wait 24 hours | 1. Logic check: Status -> "Expired"<br>2. Items released from allocation | 24h wait | All | Draft |

---
*Note: This is an abbreviated logical view. A full 120+ TC list is exported via Python script to CSV.*
