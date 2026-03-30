# QA Analysis Report
**Feature:** POD T-Shirt Platform BA Specifications
**Source:** https://bccpoint.atlassian.net/wiki/spaces/PO/pages/189825026/POD+T-Shirt+Platform+BA+Specifications
**Analyzed by:** QA Analyst Agent
**Date:** 2026-03-11
**Status:** Completed

---

## 1. DOCUMENT SUMMARY
This document outlines the business and functional specifications for a Print-on-Demand (POD) T-Shirt platform where users can design shirts using AI, earn credits through registration and delivered orders, and checkout with specific business logic (ESG savings, manual fulfillment).

## 2. USE CASES IDENTIFIED
- **UC01: User Authentication & Onboarding**: Registration (5 bonus credits), Login, Email Verification.
- **UC02: Smart Fit (Size Recommendation)**: User inputs height/weight to get size suggestion.
- **UC03: Design Editor**: Fabric.js based editor for custom designs and shirt color selection.
- **UC04: AI Artwork Generation**: Spend 5 credits to generate 4 designs from prompt. Daily limit = 10.
- **UC05: AI Credits Management**: Bonus on registration, reward on delivery, deduction on AI gen.
- **UC06: Shopping Cart & Checkout**: Multi-step flow, VNPay/Bank Transfer, Guest to User cart merge.
- **UC07: ESG & Price Transparency**: Pie chart showing profit/cost breakdown and savings.
- **UC08: Admin Order Fulfillment**: Order status management and manual export for printing.
- **UC09: System Configuration**: Admin can update base prices and promo codes.

## 3. ANALYSIS FINDINGS

### ✅ Strengths
- Clear business logic for AI credit lifecycle.
- Well-defined cost components (ESG, Ink, Ops).
- Structured Guest-to-User migration path.

### ⚠️ Gaps & Risks
- **Credit Clawback**: Logic for revoking credits on refunded orders needs BA clarification.
- **Manual Fulfillment**: Dependency on manual export/print flow is a scaling bottleneck.
- **Sync Issues**: Guest mode sync might lose data if browser cache is cleared prematurely.

## 4. TEST SCOPE SUMMARY
**In Scope:** Auth flow, AI Generation, Credit logic, Smart Fit, Checkout flow, Admin Panel.
**Out of Scope:** Physical printing quality, 3rd party shipping carrier API uptime.

---
*This report was re-generated to ensure availability in the new Test_Reports directory.*
