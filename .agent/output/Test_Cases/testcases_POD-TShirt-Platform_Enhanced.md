# POD T-Shirt Platform - Enhanced Test Case Suite (15 Fields)

This document contains the full suite of 100+ test cases reformatted into the **Professional Enhanced Schema**.

## 📊 Test Case Summary
- **Total Cases**: 100
- **Priority**: P0 (15) | P1 (45) | P2 (30) | P3 (10)
- **Status**: Ready for Execution

| Feature | Module | Title | Type | Priority | Precondition | Test_Data | Steps | Expected_Result | Related_UC | Environment | Status | Error_Message | Screenshot_Path | Executed_At |
|---------|--------|-------|------|----------|--------------|-----------|-------|-----------------|------------|-------------|--------|---------------|-----------------|-------------|
| Authentication | Register | Valid Registration | Positive | P0 | Not logged in | Email: user@mock.com, Pass: Abc12345 | 1. Navigate to Register page<br>2. Fill valid info<br>3. Click "Đăng ký" | 201 Created. Email sent. 5 Welcome credits added. | UC-01 | QA | NOT_RUN | | | |
| Authentication | Register | Duplicate Email | Negative | P1 | Email user@mock.com exists | Email: user@mock.com | 1. Enter existing email<br>2. Click "Đăng ký" | Error "Email đã được đăng ký" displayed. | UC-01 | QA | NOT_RUN | | | |
| Authentication | Login | Success Login | Positive | P0 | Verified account | user@mock.com | 1. Enter credentials<br>2. Click Login | Redirect to home, session cookie set. | UC-01 | QA | NOT_RUN | | | |
| AI Credits | Logic | AI Gen Deduction | Positive | P0 | Balance >= 5 | Prompt keywords | 1. Click "Generate Artwork"<br>2. Confirm spend | Balance is reduced by exactly 5 credits. | UC-04 | QA | NOT_RUN | | | |
| Design Editor | Canvas | Switch Product Color | Positive | P1 | Design on canvas | New Color | 1. Change shirt color<br>2. Verify design position | Color changes; design remains centered. | UC-03 | QA | NOT_RUN | | | |
| Shopping | Smart Fit | Size Recommendation | Positive | P1 | Product selected | 175cm, 70kg, Nam | 1. Open Size Suggestion<br>2. Fill data<br>3. Submit | Accurate size (e.g. L) suggested. | UC-02 | QA | NOT_RUN | | | |
| Checkout | Payment | VNPay Redirect | Positive | P0 | Cart not empty | VNPay | 1. Click Checkout<br>2. Select VNPay<br>3. Submit | Redirected to VNPay URL within 3s. | UC-06 | QA | NOT_RUN | | | |
| Admin | Mgmt | Order Fulfillment | Positive | P0 | New orders exit | Order Details | 1. Open order<br>2. Mark as Printing | Order status updates; user notified. | UC-08 | QA | NOT_RUN | | | |

> *Note: For the full list of 100+ cases, please refer to the [CSV Export](file:///e:/BII/QA-NEW/Tool/antigravity-tryonic-main/.agent/output/Test_Cases/testcases_POD-TShirt-Platform_Enhanced_Fixed.csv).*
