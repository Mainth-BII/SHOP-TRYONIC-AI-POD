# Test Cases: POD T-Shirt Platform (Phase 1 MVP)

**Version:** 2.1  
**Total Cases:** 105 (Planned)  
**Schema:** Enhanced 15-field standard  

| ID | Feature | Module | Title | Type | Priority | Precondition | Test_Data | Steps | Expected_Result | Related_UC | Environment | Status | Error_Message | Screenshot_Path | Executed_At |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-001 | AI Artwork | Generator | Generate artwork with Vietnamese prompt | Functional | High | Logged in, enough credits | Prompt: "Con rồng Việt Nam", Style: "Realistic" | 1. Enter VN prompt 2. Click Generate | System translates to EN, generates 2-4 variations in ≤ 15s | F01 | Chrome | Draft | - | - | - |
| TC-002 | AI Artwork | Generator | Deduct credits for Generation | Functional | High | Credits: 20 | Click Generate | 1. Check balance 2. Click Generate 3. Check balance again | Balance is 15 (-5 credits) | F14/BR-CRD-03 | Chrome | Draft | - | - | - |
| TC-003 | AI Artwork | Quota | Daily quota limit enforcement | Functional | Medium | Daily usage: 9/10 | No extra config | 1. Generate 10th artwork 2. Try to generate 11th | 11th attempt blocked with "Hết lượt tạo hôm nay" message | BR-AI-01 | Chrome | Draft | - | - | - |
| TC-004 | AI Artwork | Upscale | Upscale artwork resolution | Functional | High | Artwork generated (512px) | Click "Dùng artwork này" | 1. Select artwork 2. Click Use | System upscales to ≥2048px (300 DPI) and opens Editor | F01b | Chrome | Draft | - | - | - |
| TC-005 | Guest Mode | Migration | Logic for migrating Cart from Guest to User | Integration | High | Add item as Guest | Product ID: 101, Size: M | 1. Add to cart 2. Login | Cart item from localStorage is synced to server-side cart | Flow 3/BR-GUEST-04 | Chrome | Draft | - | - | - |
| TC-006 | Guest Mode | Blocked Action | Guest cannot checkout without login | Security | High | Guest session | Go to Checkout | 1. Add to cart 2. Go to Checkout | Redirected to Login/Register modal | BR-GUEST-02 | Chrome | Draft | - | - | - |
| TC-007 | Order | Cancellation | User cancels Pending order | Functional | High | Order status: Pending | Order Code: POD-2026... | 1. Open order detail 2. Click Cancel | Order status changes to Canceled | BR-ORD-01 | Chrome | Draft | - | - | - |
| TC-008 | Order | Expiry | Automatic cancellation after 24h unpaid | System | Medium | Unpaid order (Pending) | Created_at: (current - 25h) | 1. Wait for system check | Order status automatically changes to Canceled | BR-ORD-04 | Server | Draft | - | - | - |
| TC-009 | Refund | Policy | Full refund request within 30 days | Functional | Medium | Order Delivered (<30 days) | Refund Reason: "Don't like it" | 1. Request refund | Refund status: Requested. Money back in 90 days. | BR-REF-01 | Chrome | Draft | - | - | - |
| TC-010 | Editor | Safe Zone | Warning when artwork is out of range | UI/UX | High | Use Editor | Move image layer | 1. Drag image to edge | Boundary warning ("Ngoài vùng in safe zone") appears | F06 | Chrome | Draft | - | - | - |
| TC-011 | Admin | CRM | Lock user account and notify | Functional | High | Admin logged in | Target User: user@test.com | 1. Find user 2. Click Lock + Reason | User status = Locked. User receives notification email. | BR-ACC-12/F13 | Admin Dashboard | Draft | - | - | - |
| TC-012 | Auth | Verification | Block checkout for unverified email | Security | High | User registered via Email | Unverified user | 1. Checkout | Blocked with message "Vui lòng xác thực email" | Flow 5/S01 | Chrome | Draft | - | - | - |
| TC-013 | Credits | Refund | Refund credits on AI failure | Functional | Medium | Credits: 5 | Provoke API error | 1. Click Generate 2. AI Fails | Balance remains 5 (+5 refund processed) | BR-AI-03 | Chrome | Draft | - | - | - |
| TC-014 | Fit-Size | Logic | Smart Fit-Size BMI calculation | Functional | Medium | Size chart: S/M/L | H: 170cm, W: 70kg, Gender: M | 1. Enter metrics | System suggests Size L (Confidence 90%) | BR-FIT-02 | Chrome | Draft | - | - | - |
| TC-015 | Plain T-Shirt | Selection | Buying plain T-shirt skipping Editor | Functional | Low | Product: Round Neck | Action: "Mua ngay" | 1. Click Buy Now 2. Select Size | Added to cart directly without Editor | BR-PLAIN-01 | Chrome | Draft | - | - | - |

... (Total 105 cases follow same structure)
