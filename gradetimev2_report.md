# Estimation Comparison Report

**Generated:** 2026-01-14 09:57:24
**Fuzzy Match Threshold:** 0.5

---

## 1. Total Hours Comparison

**Status:** ❌ OVERESTIMATED

| Metric | Value |
|--------|-------|
| Actual Hours | 3908 |
| Predicted Hours | 4914 |
| Difference | +1006 (+25.74%) |

## 2. Platform Coverage

**Status:** ✅ 100.00% Coverage

| Metric | Count |
|--------|-------|
| Actual Platforms | 3 |
| Predicted Platforms | 3 |
| Matched | 3 |

**✅ Matched Platforms:**
- API
- CMS
- Web App

## 3. User Role Coverage

**Status:** ❌ 0.00% Coverage

| Metric | Count |
|--------|-------|
| Actual User Roles | 0 |
| Predicted User Roles | 0 |
| Matched | 0 |

## 4. Epic Coverage

**Status:** ⚠️ 72.50% Coverage

| Metric | Count |
|--------|-------|
| Actual Epics | 40 |
| Predicted Epics | 41 |
| Matched (Total) | 29 |
| Matched (Exact) | 18 |
| Matched (Fuzzy) | 11 |
| Missing | 11 |
| Extra | 12 |

**✅ Matched Epics:**

| Actual Epic | Predicted Epic | Match Type | Similarity |
|-------------|----------------|------------|------------|
| Project Configuration | Project Configuration | EXACT | 1.00 |
| Database Design | Database Design | EXACT | 1.00 |
| Authentication | Authentication | EXACT | 1.00 |
| Profile Setup | Profile Setup | EXACT | 1.00 |
| My Profile | My Profile | EXACT | 1.00 |
| Notification | Notification | EXACT | 1.00 |
| Dashboard - Teacher | Dashboard - Teacher | EXACT | 1.00 |
| Rubric Management - Teacher | Rubric Management - Teacher | EXACT | 1.00 |
| Assignment Types & Marking Flows - Teacher | Assignment Types & Marking Flows - Teacher | EXACT | 1.00 |
| Settings & Class Management - Teacher | Settings & Class Management - Teacher | EXACT | 1.00 |
| Class Analytics - Teacher | Class Analytics - Teacher | EXACT | 1.00 |
| Google Classroom Integration | Google Classroom Integration | EXACT | 1.00 |
| Turnitin Integration | Turnitin Integration | EXACT | 1.00 |
| Admin Dashboard - School | Admin Dashboard - School | EXACT | 1.00 |
| Class & course management - School | Class & course management - School | EXACT | 1.00 |
| School Level Analytics - School | School Level Analytics - School | EXACT | 1.00 |
| Integration Management - School | Integration Management - School | EXACT | 1.00 |
| Deployment | Deployment | EXACT | 1.00 |
| Email Notification | Tenant Isolation | FUZZY | 0.53 |
| Elastic Search | ElasticSearch | FUZZY | 0.96 |
| File Upload System - Teacher | Detailed Marking Review - Teacher | FUZZY | 0.52 |
| OCR Integration - Teacher | Assignment Creation - Teacher | FUZZY | 0.67 |
| Student Analytics - Teacher | Feedback Editing - Teacher | FUZZY | 0.53 |
| Canvas Integration | Analytics Mapping - Admin | FUZZY | 0.51 |
| Admin User Management - School | Compliance Management - Admin | FUZZY | 0.58 |
| Teacher Management - School | Billing Management - Admin | FUZZY | 0.53 |
| Students Management - School | CMS - Instructor Management | FUZZY | 0.55 |
| Audit log - School | Audit Logs & Security Monitoring | FUZZY | 0.60 |
| Admin User Management | Trust Index Algorithm Management | FUZZY | 0.57 |

**❌ Missing Epics (in Actual but not Predicted):**
- CMS Pages
- Grading Defaults & Style Guide - Teacher
- Marking Review & Individual Results - Teacher
- Role-base permission - School
- Subscription & billing - School
- Data & compliance - School
- Card Payment Setup - School
- School Management
- Admin Dashboard
- Transactions
- Backend Configurations and Authentication

**➕ Extra Epics (in Predicted but not Actual):**
- Security & Privacy (End User)
- Watch Security (Watch App) - End User
- MT - Review And Rating
- Access Log
- AI Grading and Feedback Automation
- OCR Document Ingestion
- Plagiarism Similarity Scoring
- Report Exports - Admin
- Class Overview Pages - Admin
- Asynchronous AI Processing
- Data Privacy and Minimization
- Audit and Logging

## 5. Task Coverage & Granularity

**Status:** ✅ 85.37% Overall Coverage

| Metric | Value |
|--------|-------|
| Avg Actual Tasks per Epic | 5.53 |
| Avg Predicted Tasks per Epic | 4.49 |
| Granularity Difference | -18.77% |

**Epic-by-Epic Task Analysis:**

| Epic Name | Actual Tasks | Predicted Tasks | Coverage | Granularity |
|-----------|--------------|-----------------|----------|-------------|
| Project Configuration | 4 | 3 | 75.00% | 📊 SIMILAR |
| Database Design | 3 | 1 | 33.33% | 📉 LESS_GRANULAR |
| Authentication | 12 | 13 | 100.00% | 📊 SIMILAR |
| Profile Setup | 2 | 3 | 100.00% | 📈 MORE_GRANULAR |
| My Profile | 9 | 8 | 88.89% | 📊 SIMILAR |
| Notification | 4 | 5 | 100.00% | 📊 SIMILAR |
| Dashboard - Teacher | 6 | 6 | 100.00% | 📊 SIMILAR |
| Rubric Management - Teacher | 8 | 8 | 100.00% | 📊 SIMILAR |
| Assignment Types & Marking Flows - Teacher | 20 | 20 | 100.00% | 📊 SIMILAR |
| Settings & Class Management - Teacher | 4 | 4 | 100.00% | 📊 SIMILAR |
| Class Analytics - Teacher | 6 | 6 | 100.00% | 📊 SIMILAR |
| Google Classroom Integration | 10 | 10 | 100.00% | 📊 SIMILAR |
| Turnitin Integration | 5 | 5 | 100.00% | 📊 SIMILAR |
| Admin Dashboard - School | 2 | 2 | 100.00% | 📊 SIMILAR |
| Class & course management - School | 6 | 6 | 100.00% | 📊 SIMILAR |
| School Level Analytics - School | 3 | 3 | 100.00% | 📊 SIMILAR |
| Integration Management - School | 2 | 2 | 100.00% | 📊 SIMILAR |
| Deployment | 1 | 1 | 100.00% | 📊 SIMILAR |
| Email Notification | 3 | 3 | 100.00% | 📊 SIMILAR |
| Elastic Search | 3 | 3 | 100.00% | 📊 SIMILAR |
| File Upload System - Teacher | 3 | 3 | 100.00% | 📊 SIMILAR |
| OCR Integration - Teacher | 6 | 3 | 50.00% | 📉 LESS_GRANULAR |
| Student Analytics - Teacher | 7 | 3 | 42.86% | 📉 LESS_GRANULAR |
| Canvas Integration | 13 | 3 | 23.08% | 📉 LESS_GRANULAR |
| Admin User Management - School | 4 | 3 | 75.00% | 📊 SIMILAR |
| Teacher Management - School | 8 | 3 | 37.50% | 📉 LESS_GRANULAR |
| Students Management - School | 5 | 9 | 100.00% | 📈 MORE_GRANULAR |
| Audit log - School | 3 | 3 | 100.00% | 📊 SIMILAR |
| Admin User Management | 4 | 2 | 50.00% | 📉 LESS_GRANULAR |

---

## Overall Summary

**Overall Coverage Score:** ⚠️ 64.47%

| Dimension | Coverage |
|-----------|----------|
| Platform Coverage | 100.00% |
| User Role Coverage | 0.00% |
| Epic Coverage | 72.50% |
| Task Coverage | 85.37% |

### Key Findings

❌ **Hours estimation needs improvement** (25.74% difference)

✅ **Best Coverage:** Platforms (100.00%)
❌ **Needs Improvement:** User Roles (0.00%)
