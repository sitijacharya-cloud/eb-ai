"""Application constants."""

from typing import List

# Mandatory Epics that MUST be included in every estimation
MANDATORY_EPICS: List[str] = [
    "Authentication",
    "Project Configuration",
    "Deployment",
    "Database Design",
    "Elastic Search",
    "Notification",
    "My Profile",
    "Profile Setup",
]

# Platform names
PLATFORMS = ["Flutter", "Web App", "API", "CMS"]

# Prompts for AI agents
ANALYZE_REQUIREMENT_PROMPT = """You are an expert software requirements analyst specializing in project estimation. Analyze this project requirement and extract structured information for estimation and planning.

Project Requirement:
{requirement}

**CRITICAL ANALYSIS GUIDELINES:**
1. BE PRECISE & COMPREHENSIVE: Extract ALL explicit and implied requirements
2. AVOID ASSUMPTIONS: Only include what's stated or clearly implied by domain norms
3. DEFAULT TO MODERATE: When uncertain about scope, assume standard implementation
4. GROUP LOGICALLY: Features should map cleanly to epics

Extract the following:

1. Domain: Identify the primary business domain
- Use clear, descriptive domain names (e.g., ecommerce, fintech, healthcare, social_media, marketplace, education, logistics, hospitality, real_estate, entertainment, fitness, food_delivery, travel, automotive, etc.)
- Choose ONE primary domain even if hybrid (e.g., "food_delivery" not "social_media + ecommerce")
- Consider the core value proposition and primary user activity
- If truly unique/custom, describe it clearly (e.g., "wedding_inspiration_platform")

2. Features: Extract ALL features mentioned or logically required for this specific domain.

**DOMAIN-AGNOSTIC APPROACH:**
Don't assume features - extract ONLY what's mentioned or clearly required for the stated domain.

**A. Core User Features (Domain-Specific):**
- Account/Profile management (registration, login, profile setup)
- Primary user actions relevant to the domain (e.g., booking, ordering, posting, searching)
- Content creation/consumption (if applicable)
- Interaction features (comments, likes, shares, messaging)
- Search and discovery mechanisms
- User preferences and settings

**B. Admin/Management Features:**
- User management (view, edit, suspend, delete users)
- Content/Data management (approve, reject, moderate)
- Analytics & reporting dashboards
- System configuration and settings
- Role and permission management

**C. Payment & Financial (if applicable):**
- For EACH payment method mentioned: extract as separate feature
- Example: "multiple payment options" → ["credit_card_payment", "debit_card_payment", "wallet_payment"]
- Subscriptions, recurring billing, invoices
- Refunds, disputes, payout processing
- Transaction history and reporting

**D. AI/ML Capabilities (if mentioned):**
- For EACH AI mention: extract specific capabilities
- Recommendations, predictions, classifications
- Content generation, automation
- Pattern recognition, anomaly detection
- Natural language processing

**E. Technical & Infrastructure Features:**
- Real-time features (live updates, WebSocket connections)
- Offline capabilities (sync, cached data)
- Geolocation services (GPS, location tracking, maps)
- Push notifications and alerts
- File/media handling (upload, storage, processing)
- Multi-language support (i18n)
- Accessibility features

**F. Integrations & Third-party Services:**
- Payment gateways (list each: Stripe, PayPal, Razorpay, etc.)
- Social media platforms (Facebook, Instagram, Twitter, etc.)
- Email services (SendGrid, Mailchimp, etc.)
- SMS/WhatsApp services
- Cloud storage (AWS S3, Google Cloud, etc.)
- Authentication providers (OAuth, SSO)
- Analytics tools (Google Analytics, Mixpanel, etc.)
- Domain-specific APIs or services

**G. Common Infrastructure Features (Check if mentioned or implied):**
- CMS Pages (Terms & Conditions, Privacy Policy, About Us, FAQ)
- Onboarding flow (Splash screen, Tutorial, Welcome screens)
- Help & Support (FAQs, Contact forms, In-app support)
- Feedback & Ratings (User reviews, ratings, feedback forms)
- Sharing functionality (Social sharing, referrals, invites)
- Bookmarking/Favorites (Save items for later)
- Activity history (User activity logs, view history)
- Export/Import functionality (Data export, bulk operations)


3. Tech Stack: Technologies mentioned or inferred from requirements

4. Platforms: Choose from these exact values based on WHO uses WHAT interface:
   - "Flutter" (mobile apps for END USERS - Android/iOS)
   - "Web App" (web frontend for END USERS accessing via browser)
   - "API" (backend services - ALWAYS include when any frontend exists)
   - "CMS" (admin/management dashboard - ONLY for admin/staff users)
   
    CRITICAL PLATFORM SELECTION RULES (READ CAREFULLY):
   
   **END USER PLATFORMS** (who are the primary users?):
   • "Mobile App" / "Android" / "iOS" / "Mobile Application" → **"Flutter"** only
   • "Web App" / "Web Application" / "Browser-based" → **"Web App"** only  
   • BOTH mobile and web for end users → **["Flutter", "Web App"]**
   
   **ADMIN PLATFORMS** (separate from end users):
   • "Admin Dashboard" / "Admin Panel" / "dashboard" / "Management Console" / "Admin Portal" → **"CMS"**
   • Admin uses web dashboard → **"CMS"** (NOT "Web App")
   
   **BACKEND**:
   • Always include **"API"** when frontend platforms exist
   
   **DECISION FLOWCHART:**
   ```
   1. What do END USERS use?
      - Mobile only → Flutter
      - Web only → Web App
      - Both mobile & web → Flutter + Web App
   
   2. Is there an admin/management interface?
      - Yes → Add CMS
      - Admin dashboard mentioned → Add CMS
      - Content moderation mentioned → Add CMS
      - User management mentioned → Add CMS
      - Analytics/reporting for staff → Add CMS
      - No → Don't add CMS
   
   3. Add API (always needed for frontends)
   ```
   
   **COMMON MISTAKES TO AVOID:**
   • "Admin has web-based dashboard" → DON'T add "Web App", add "CMS" ✓
   • "Mobile app + admin dashboard" → ["Flutter", "API", "CMS"] NOT ["Flutter", "Web App", "API"] ✓
   • Confusing admin dashboard with user web app → They are DIFFERENT platforms ✓
   
    **CORRECT EXAMPLES:**
   • "Mobile app for customers, web dashboard for admin" → **["Flutter", "API", "CMS"]**
   • "iOS and Android app" → **["Flutter", "API"]**
   • "Web based or web application for users, admin panel" → **["Web App", "API", "CMS"]**
   • "Mobile and web app for users" → **["Flutter", "Web App", "API"]**
   • "Mobile app, no admin mentioned" → **["Flutter", "API"]**

5. Initial Epics: Create one epic per extracted feature (1:1 mapping)

   **CRITICAL INSTRUCTION: Each feature = One epic**
   
   **Process:**
   1. Review the COMPLETE list of features you extracted 
   2. For EACH feature, create ONE corresponding epic with a same feature name
   3. Convert feature names into proper epic names (e.g., "user_registration" → "User Registration")
   4. Add user type suffix if feature is user-specific (e.g., "Profile Management - Buyer")
   
   **User-Specific Features:**
   - If feature is for specific user type, add suffix: "Feature Name - UserType"
   - Examples: "Dashboard - Admin", "Profile - Buyer", "Analytics - Seller"
   
   **Result:** You should have the SAME number of initial epics as features extracted
  

6. Epic Categories: Map each epic to its corresponding feature (1:1 mapping)
   
   **CRITICAL: One epic → One feature mapping**
   
   Since each epic corresponds to exactly one feature, create a 1:1 mapping where:
   - Each epic name is the key
   - The corresponding feature  is the value 
   
   **Example Mapping:**
   If you extracted features: ["user_registration", "email_login", "product_search", "payment_processing", "admin_dashboard"]
   
   Then epic_categories should be:
   - "User Registration": ["user_registration"]
   - "Email Login": ["email_login"]
   - "Product Search": ["product_search"]
   - "Payment Processing": ["payment_processing"]
   - "Admin Dashboard": ["admin_dashboard"]
   
   **Validation Checklist:**
   - [ ] Number of epic_categories entries = Number of features extracted
   - [ ] Each epic maps to exactly ONE feature (single-item array)
   - [ ] All features should appear in epic_categories values
   - [ ] Epic names are properly formatted (title case, with user type suffix if needed)

7. User Types: Extract user roles/types if mentioned or clearly implied by the domain.
   - Include ONLY if explicitly mentioned or domain clearly requires multiple user types
   - Common patterns:
     * Marketplace/E-commerce: Buyer, Seller, Vendor, Admin
     * Healthcare: Patient, Doctor, Nurse, Admin
     * Education: Student, Teacher, Parent, Admin
     * Social/Dating: User, Moderator, Admin
     * Service Booking: Customer, Service Provider, Admin
     * Food Delivery: Customer, Restaurant, Delivery Partner, Admin
     * Real Estate: Buyer, Seller, Agent, Admin
   - Use clear, domain-appropriate role names
   - Include "Admin" if any admin features mentioned
   - Leave empty if system has only one general user type

8. Special Requirements: Identify unique technical needs that significantly impact architecture:
   - **Real-time capabilities** (WebSocket, live updates, chat)
   - **High-volume data processing** (big data, streaming)
   - **Security & Compliance** (GDPR, HIPAA, PCI-DSS, SOC2)
   - **Blockchain integration** (crypto payments, NFTs, smart contracts)
   - **Complex workflows** (multi-step approvals, state machines)
   - **Multi-tenancy** (SaaS with isolated customer data)
   - **High availability** (99.9% uptime, disaster recovery)
   - **Video/Audio processing** (streaming, transcoding, recording)
   - **Geospatial features** (advanced mapping, routing, geofencing)
   - **Machine learning** (model training, inference pipelines)
   - **Third-party integrations** (list specific critical integrations)

Return valid JSON in this format:
{{
  "domain": "domain_name",
  "features": ["feature1", "feature2", "feature3"],
  "tech_stack": ["tech1", "tech2"],
  "platforms": ["Flutter", "API", "CMS", "Web App"],
  "initial_epics": ["Feature 1 Epic Name", "Feature 2 Epic Name", "Feature 3 Epic Name"],
  "epic_categories": {{
    "Feature 1 Epic Name": ["feature1"],
    "Feature 2 Epic Name": ["feature2"],
    "Feature 3 Epic Name": ["feature3"]
  }},
  "user_types": ["usertype1", "usertype2", "usertype3"],
  "special_requirements": ["requirement1"]
}}

IMPORTANT: Each epic in initial_epics must have exactly ONE corresponding feature in epic_categories.
"""

GENERATE_CUSTOM_EPIC_PROMPT = """You are an expert software project estimator with 15+ years of experience. Analyze the project requirements and generate custom epics with complete HIGH-LEVEL task breakdowns and conservative effort estimates.

# INPUTS PROVIDED:

## 1. Project Requirements:
- **Domain**: {domain}
- **Project Type**: {project_type}
- **Target Platforms**: {platforms}
- **User Types**: {user_types}
- **Key Features**: {features}

## 2. Mandatory Epics (already included with fixed hours - learn patterns from these):
{mandatory_epics_summary}

## 3. Retrieved Similar Epics (learn patterns from these):
{retrieved_epics_summary}

## 4. Already Covered Epic Names (DO NOT duplicate):
{existing_epic_names}

---

# YOUR TASK:

Generate CUSTOM epics with HIGH-LEVEL tasks and effort estimates for features NOT covered above.

## LEARNING FROM EXAMPLES:

The mandatory and retrieved epics are REFERENCE EXAMPLES to learn from:

 **LEARN & USE:**
- **Epic names and structure**: What epics exist for this domain?
- **Task descriptions**: What tasks are typically needed?
- **Effort ranges**: How many hours do similar tasks usually take?
- **Task breakdown patterns**: How are features split into deliverable tasks?

 **DO NOT COPY:**
- **Platforms**: Examples may show Flutter, Web App, API, CMS
- You MUST use ONLY your target platforms: {platforms}
- Adapt the effort estimates to your target platforms

**LEARNING PROCESS:**

1. **Study Epic Patterns**: "Authentication epic has 6-8 tasks (signup, login, OTP, password reset)"
2. **Study Task Descriptions**: "Email/Mobile signup with validation" (not just "Signup")
3. **Study Effort Ranges**: "Login tasks typically take 4-8h per platform"
4. **Adapt to Your Platforms**: Saw Web App:8h in example? Your target is Flutter? Use Flutter:8h instead

## CRITICAL RULES:

### 1. Platform Adaptation  MOST IMPORTANT

**YOUR TARGET PLATFORMS: {platforms}**

**You must TRANSLATE examples to your target platforms:**

 **Translation Examples:**

**Example 1 - Mobile App Project:**
```
REFERENCE EXAMPLE (has Web App):
Task: "User profile management"
Efforts: {{"Flutter": 12, "Web App": 12, "API": 16}}

YOUR TARGET: ["Flutter", "API", "CMS"]
YOUR OUTPUT (Web App removed, adapted to target):
Task: "User profile management"  
Efforts: {{"Flutter": 12, "API": 16}}  ← Web App excluded!
```

**Example 2 - Web App Project:**
```
REFERENCE EXAMPLE (has Flutter):
Task: "Dashboard with real-time updates"
Efforts: {{"Flutter": 24, "API": 20}}

YOUR TARGET: ["Web App", "API", "CMS"]
YOUR OUTPUT (Flutter → Web App translation):
Task: "Dashboard with real-time updates"
Efforts: {{"Web App": 24, "API": 20}}  ← Used Web App instead of Flutter!
```

**Example 3 - Filtering Multiple Platforms:**
```
REFERENCE EXAMPLE (has all 4 platforms):
Task: "Notification system"
Efforts: {{"Flutter": 8, "Web App": 8, "API": 12, "CMS": 8}}

YOUR TARGET: ["Flutter", "API"]
YOUR OUTPUT (only target platforms):
Task: "Notification system"
Efforts: {{"Flutter": 8, "API": 12}}  ← Only Flutter + API included!
```

**RULES:**
- If example has your target platform → Use that effort value 
- If example lacks your target platform → Adapt from similar platform (Flutter ↔ Web App) ✅
- If example has extra platforms → Remove them
- Never include platforms outside: {platforms} 

### 2. Task Breakdown (HIGH-LEVEL, NOT GRANULAR)

**Target: 5-10 tasks per epic (MIN 5, MAX 12 for very complex epics)**

Each task should represent a COMPLETE, deliverable feature component that combines related work.

**LEARN FROM RETRIEVED EPICS:**
Study the retrieved/mandatory epics carefully - they show real-world task breakdowns:
- How many tasks per epic? (Usually 5-10)
- What level of granularity? (High-level deliverables, not sub-tasks)
- What are typical task descriptions? (Complete features, not technical steps)
- What are realistic hour ranges? (Usually 4-32 hours per task)

**IMPORTANT:** If you see a retrieved epic with 15+ tasks, it means:
1. That epic covers a LARGE feature area
2. You should create 2-3 SEPARATE epics to cover the same scope
3. Each new epic should have 6-10 tasks (not copy all 15+ into one epic)

Example: If retrieved "Assignment Management" has 20 tasks →
Create multiple epics: "Assignment Creation", "Assignment Grading", "Assignment Review"
Each with 6-8 focused tasks

**REAL-WORLD EXAMPLES of proper task breakdown:**

Epic: "Authentication" → 5-8 tasks
✓ "Email/Mobile signup with validation"
✓ "Email/Mobile login with session management"
✓ "OTP verification with resend functionality"
✓ "Password reset and forgot password flow"
✓ "Social login (Google/Apple ID) integration"
✓ "Manage app features based on user role"

Epic: "Notification" → 6-8 tasks
✓ "Display in-app notification list"
✓ "Manage read/unread status of notifications"
✓ "Route users based on notification type"
✓ "Set up push notifications"
✓ "Handle receiving and sending push notifications"
✓ "Send push notification from admin"

Epic: "My Profile" → 7-9 tasks
✓ "View profile"
✓ "Update profile"
✓ "Settings (notification/privacy preferences)"
✓ "Update email and mobile number"
✓ "Change password"
✓ "Logout"
✓ "Delete account"
✓ "View/Update Preferences"

Epic: "Payment Setup" → 4-5 tasks
✓ "Add, update, remove payment methods (card/bank)"
✓ "List saved payment methods"
✓ "Set default payment method"
✓ "Payment integration (Stripe/PayPal/Apple Pay)"

**ANTI-PATTERNS (What NOT to do):**
✗ DON'T: "Design UI" + "Implement state" + "Add validation" (3 tasks)
✓ DO: "Build screen with state and validation" (1 task)

✗ DON'T: "Create GET endpoint" + "Create POST endpoint" + "Create PUT/DELETE" (3 tasks)
✓ DO: "Implement CRUD API endpoints" (1 task)

✗ DON'T: Copy all 20 tasks from a large retrieved epic into one epic
✓ DO: Split into 3-4 focused epics, each with 5-7 tasks

**Task Categories (combine related items):**

- **Frontend (Flutter/Web App)**: Combine UI, state, navigation, validation into 1-3 tasks
  Example: "Build account linking screens with validation and navigation"

- **Backend (API)**: Group related endpoints, include schema + logic in same task
  Example: "Implement meter management API (schema, CRUD endpoints, validation)"

- **Admin (CMS)**: Group admin screens, data management, reports into 1-2 tasks
  Example: "Build admin dashboard with user management and reports"

### 3. Effort Estimation (Conservative, based on similar tasks)

### 3. Effort Estimation (Conservative, based on similar tasks)

**CRITICAL: Study retrieved epics' hours carefully!**

Look at similar tasks in retrieved/mandatory epics:
- Find tasks with similar descriptions
- Note their hour ranges across platforms
- Use those as baseline (don't go lower without good reason)
- Adjust for complexity, not arbitrarily reduce

**Example:**
Retrieved epic has: "Implement OCR system" → API: 24h
Your similar task should be: 20-30h (not 8h!)

Retrieved epic has: "AI grading with feedback" → Web App: 16h, API: 16h
Your similar task should be: 14-20h per platform (not 8h!)

**Base Guidelines:**
- **Simple CRUD**: 6-10h per platform (was 4-8h)
- **API integration**: 12-20h backend, 8-16h frontend (was 8-16h, 6-12h)
- **Complex workflow**: 16-32h per platform (was 12-24h)
- **UI components**: 6-12h per platform (was 4-8h)
- **AI/ML features**: 40-80h backend minimum for serious AI work

**Platform effort patterns:**
- Flutter: ~1x of Web App
- **API/Web Service: ~1.5-2x of frontend** (more logic, testing, optimization, security)
- CMS: ~0.6-0.8x of Web App (simpler admin interfaces)

**CRITICAL - Backend Hours:**
Backend (API) tasks almost always need MORE hours than frontend:
- **Simple CRUD API**: 1.5x frontend (if frontend is 6h, API should be 8-10h)
- **Complex logic**: 2x frontend (if frontend is 12h, API should be 20-24h)
- **Real-time/Chat**: 2-3x frontend (WebSocket complexity, message queuing)
- **Role management**: 2x frontend (complex permissions, access control)
- **Payment integration**: 1.5-2x frontend (security, webhooks, reconciliation)

**Common Mistakes to Avoid:**
✗ Frontend: 12h, API: 8h → WRONG (API should be higher)
✓ Frontend: 12h, API: 16-20h → CORRECT

**Special Requirements (add 20-80% each):**
- Real-time features (WebSockets, live updates): +30-50%
- AI/ML integration: +50-80%
- Video/audio processing: +40-60%
- Payment gateway integration: +30-50%
- Compliance requirements (GDPR, HIPAA, PCI-DSS): +30-60%
- Multi-language support: +20-30%
- Offline-first architecture: +40-60%
- Advanced security needs: +30-50%
- High availability requirements: +40-60%

**Platform-Specific Factors:**
- Flutter: Custom animations (+30-40%), Offline mode (+40-60%)
- Web App: Cross-browser (+20-30%), Real-time (+40-60%)
- API: Complex logic (+40-80%), High-volume data (+60-80%)
- CMS: Complex reporting (+50-80%)

**Estimation Guidelines:**
- Be CONSERVATIVE (better to over-estimate than under-estimate)
- Learn from similar tasks in retrieved epics (use as baseline, don't reduce)
- If retrieved epic shows 24h for similar work, your range should be 20-30h (not 8h)
- Sum up hours from similar tasks - don't guess lower
- Minimum 6 hours per task per platform (was 4h)
- Maximum 40 hours per task per platform (was 32h)
- For AI/ML tasks: Minimum 40h backend (data prep, training, integration)
- For complex integrations: Minimum 20h backend (was 16h)

**RED FLAGS - Hours that are TOO LOW:**
- ✗ "AI model training and integration" = 8h → Should be 60-80h
- ✗ "OCR system implementation" = 8h → Should be 30-40h
- ✗ "Payment gateway integration" = 8h → Should be 24-32h
- ✗ "Complex dashboard with analytics" = 12h → Should be 30-40h

### 4. Avoid Duplicates
Do NOT generate epics similar to already covered:
{existing_epic_names}

**Semantic duplicates to avoid:**
- "Payment Gateway" ≈ "Payment Processing" ≈ "Payment Integration"
- "User Profile" ≈ "My Profile" ≈ "Profile Management"
- "Authentication" ≈ "Login System" ≈ "User Auth"

### 5. Domain-Specific Focus

**Generate epics that match the project domain and requirements:**

For ANY domain, analyze the features list and create appropriate epics:
- Break down complex features into manageable epics
- Group related functionality together
- Consider the full user journey from onboarding to advanced features
- Include technical infrastructure needs

**Universal Epic Categories (adapt to domain):**

1. **User Management & Authentication**
   - Registration, login, profile management
   - Social login, password reset, email verification
   - Role-based access control

2. **Core Domain Features**
   - Primary business logic specific to the domain
   - Break into multiple epics based on feature complexity
   - Each major feature area = 1-2 epics

3. **Search & Discovery**
   - Search functionality with filters
   - Advanced search, saved searches
   - Recommendations, trending items

4. **Content Management**
   - Create, read, update, delete operations
   - Media uploads, content organization
   - Content moderation (if applicable)

5. **Interactions & Engagement**
   - Comments, likes, shares, ratings
   - Bookmarks, favorites, wishlists
   - Follow/unfollow, connections

6. **Notifications & Communications**
   - Push notifications, email notifications
   - In-app notifications, SMS alerts
   - Real-time chat (if applicable)

7. **Payments & Transactions** (if applicable)
   - Payment gateway integration
   - Subscription management
   - Transaction history, invoices, refunds

8. **Location Features** (if applicable)
   - Location services, GPS tracking
   - Map integration, directions
   - Geofencing, location-based search

9. **Analytics & Reporting**
   - User analytics, engagement metrics
   - Business reports, dashboard
   - Export capabilities

10. **Admin & Configuration**
    - Admin dashboard
    - User management, content moderation
    - System settings, CMS pages

11. **Infrastructure & System**
    - Onboarding flow
    - Settings and preferences
    - Help & support

**SPECIALIZED SYSTEMS (Create Multiple Epics When Applicable):**

When you see these features in ANY domain, create MULTIPLE epics, not just one:

1. **Messaging/Chat System → 2-3 epics:**
   - "[Feature Name] - Chat Integration" (setup, authentication, sending/receiving)
   - "[Feature Name] - Chat History" (list, continue, remove, archive)
   - "Chat Notifications" (push notifications, webhooks) [if separate from main notifications]

2. **Payment/Subscription System → 3-4 epics:**
   - "Payment Gateway Integration" (Stripe, PayPal, etc. setup)
   - "Subscription Management" (plans, upgrade/downgrade, cancel)
   - "Transaction Management" (history, details, filter, download, refunds)
   - "In-App Purchases" (mobile-specific) [if applicable]

3. **Location/Map System → 2-3 epics:**
   - "Location Services" (GPS, permissions, tracking, geofencing)
   - "Map Integration" (Maps SDK, markers, clustering, directions)
   - "Location-Based Search" (geospatial queries, radius search) [if complex]

4. **Admin System → 3-5 epics:**
   - "Admin Dashboard" (overview, statistics, quick actions)
   - "Admin User Management" (admin roles, permissions, team management)
   - "User Management - Admin" (manage app users, view, edit, suspend)
   - "Content Moderation - Admin" (review reports, approve/reject, remove content)
   - "System Configuration - Admin" (settings, CMS pages, email templates)

5. **Multi-User-Type Profiles → 2-3 epics per user type:**
   - "Profile Creation - [UserType]" (setup, onboarding, verification)
   - "Profile Management - [UserType]" (view, edit, settings, preferences)
   - "[UserType] Analytics" (engagement stats, performance reports) [if applicable]

6. **Content/Media Management → 2-3 epics:**
   - "[Content Type] Creation" (create, upload, draft)
   - "[Content Type] Management" (edit, organize, categorize, delete)
   - "[Content Type] Discovery" (browse, search, filter, recommendations)

7. **Booking/Reservation System → 3-4 epics:**
   - "Booking Creation" (search availability, select, book)
   - "Booking Management" (view, modify, cancel)
   - "Calendar/Availability Management" (for providers)
   - "Booking Notifications & Reminders" (confirmations, reminders)

8. **Order/Transaction Flow → 3-4 epics:**
   - "Cart/Basket Management" (add, update, remove items)
   - "Checkout Process" (address, payment, confirmation)
   - "Order Management" (view orders, track status, history)
   - "Order Fulfillment" (for sellers/vendors/providers)

**Pattern Recognition:**
- If a feature has **create + view + edit + delete + share** → Split into 2 epics (Management + Sharing)
- If a feature has **user side + provider side** → Create separate epics per user type
- If a feature has **core functionality + analytics** → Create separate epics
- If a feature has **setup + ongoing management** → Consider 2 epics

### 6. Epic Naming Convention with User Types

**CRITICAL: Include user type in epic name when epics are specific to certain users:**

**User Types Available: {user_types}**

**Naming Rules (Universal across all domains):**

1. **Generic epics** (used by all users or system-wide): Use plain name
   Examples: "Authentication", "Database Design", "Notification", "Search Functionality"
   
2. **User-specific epics** (for specific user type): Add "- UserType" suffix
   Examples: 
   - E-commerce: "Order Management - Buyer", "Inventory Management - Seller"
   - Healthcare: "Appointment Booking - Patient", "Medical Records - Doctor"
   - Education: "Assignment Submission - Student", "Grading System - Teacher"
   - General: "Profile Management - [UserType]", "Dashboard - [UserType]"
   
3. **Multiple user types for same epic**: Use "/" separator
   Examples: "Messaging - Buyer/Seller", "Reviews - Customer/Provider"

**Decision Logic (Domain-Agnostic):**
- If ALL user types use the feature → Generic name (e.g., "Authentication")
- If SPECIFIC user types use the feature → Add user type (e.g., "Dashboard - Admin")
- If feature has different implementations per user type → Create separate epics per type
- For admin features → Always add "- Admin" suffix

**WHY This Matters:**
- Clear ownership: Shows which user type can access/use the feature
- Better organization: Groups features by user journey
- Accurate effort estimation: Different user types may have different requirements
- Improved retrieval: Helps match similar user-specific features from knowledge base

---

# OUTPUT FORMAT:

Return JSON with custom epics array. **Generate 15-25 custom epics** to cover all requirement features comprehensively.

**CRITICAL COVERAGE STRATEGY:**

1. **Study the features list exhaustively** - Each major feature should map to 1-3 epics
2. **Break down complex areas** - If a feature domain is large (e.g., "AI grading"), create multiple focused epics
3. **Cover all user journeys** - Consider onboarding, main workflows, settings, admin
4. **Include infrastructure** - Email, notifications, search, file uploads, etc.
5. **Don't skip mentioned features** - If requirement mentions "OCR", "compliance", "billing" → create epics for them

**Feature-to-Epic Mapping Examples:**
- "Payment processing" mentioned → Create 3-4 epics: Payment Gateway Setup, Card Payment Management, Transaction History, Payment Analytics
- "AI grading" mentioned → Create 4-5 epics: AI Model Integration, Grading Automation, Feedback Generation, Score Adjustment, Analytics Mapping
- "User management" mentioned → Create 2-3 epics: User Registration & Auth, Profile Management, Settings & Preferences
- "Admin dashboard" mentioned → Create 2-4 epics: Admin Dashboard, User Management - Admin, Analytics & Reporting - Admin, System Configuration - Admin

**Epic Count Guidelines by Feature Count:**
- Small project (10-20 features): 15-20 epics
- Medium project (20-40 features): 25-35 epics
- Large project (40+ features): 35-50 epics

**IMPORTANT:** Study the features list carefully and ensure you create epics for:
- Each payment method mentioned (cards, bank, PayPal, Apple Pay, Google Pay)
- Each AI/ML feature (predictions, recommendations, anomaly detection, trend analysis)
- Each integration mentioned (Google Classroom, Canvas, Turnitin, etc.)
- Core user flows (onboarding, profile, account management)
- Platform-specific needs (offline sync, localization, location services)
- Admin features (dashboard, user management, reporting, billing)
- Compliance & security (data privacy, audit logs, encryption)
- Content management (CMS pages, email templates, notifications)

Each epic should have 3-8 HIGH-LEVEL tasks (not granular sub-tasks).

**Epic Naming Examples (include user type when applicable):**
- Generic: "Authentication", "Database Design", "Notification"
- User-specific: "Save Inspirations - Bride/Groom", "Portfolio Uploads - Photographer/Videographer", "Profile Creation - Venue"

```json
{{
  "custom_epics": [
    {{
      "name": "Epic Name - UserType",
      "description": "Brief description",
      "tasks": [
        {{
          "description": "High-level task combining related work (e.g., 'Build login screen with validation and session management')",
          "efforts": {{
            "Platform1": 12,
            "Platform2": 16
          }}
        }},
        {{
          "description": "Another complete deliverable task",
          "efforts": {{
            "Platform1": 8,
            "Platform2": 12
          }}
        }}
      ]
    }}
  ]
}}
```

** FINAL REMINDER - PLATFORM ENFORCEMENT:**

YOUR TARGET PLATFORMS: **{platforms}**

Before returning JSON, verify EVERY task:
-  Does it ONLY have platforms from {platforms}?
-  Does it have "Web App" when target is ["Flutter", "API", "CMS"]? → REMOVE IT!
-  Does it have "Flutter" when target is ["Web App", "API"]? → REPLACE with "Web App"!

**Common mistakes to avoid:**
- Including "Web App" in mobile-only projects
- Including "Flutter" in web-only projects  
- Copying platform keys directly from examples
- Missing target platforms that should be included

**Your output MUST be filtered to target platforms!**

## Validation Checklist:
- [ ] 5-10 HIGH-LEVEL tasks per epic (not 15+ granular sub-tasks)
- [ ] If retrieved epic has 15+ tasks, split into multiple epics (don't copy all into one)
- [ ] Each task is a complete deliverable component
- [ ] No duplicate/similar epic names
- [ ] All epics match project domain and features
- [ ] **CRITICAL: Only platforms from {platforms} included** ← VERIFY THIS!
- [ ] **CRITICAL: No platforms outside {platforms}** ← DOUBLE CHECK!
- [ ] **CRITICAL: Backend (API) hours are 1.5-2x frontend** ← VERIFY THIS!
- [ ] Effort estimates LEARNED from retrieved epics (don't go lower without reason)
- [ ] Hours are CONSERVATIVE (6-40h range per task, minimum 6h)
- [ ] AI/ML tasks have 40-80h backend minimum
- [ ] Complex integrations have 20-40h minimum
- [ ] Backend tasks have appropriate hours (typically 1.5-2x frontend)
- [ ] Task descriptions are detailed (not just "Create", "Update", "Delete")
- [ ] Task descriptions separate UI work from API work from CMS work
- [ ] Generated 20-30 custom epics (not just 10-15)
- [ ] Specialized systems broken into multiple epics (chat, subscription, location, admin)

**COVERAGE CHECKLIST** - Ensure these are addressed if mentioned in requirements:
- [ ] Payment methods (each type needs separate epic if mentioned)
- [ ] AI/ML features (prediction, recommendation, detection, analysis) - Min 40h backend each
- [ ] Each integration mentioned (Google Classroom, Canvas, Turnitin, etc.)
- [ ] Onboarding and initial setup flows
- [ ] Location-based features
- [ ] Offline capabilities
- [ ] Localization/multi-language
- [ ] Admin-specific management features (dashboard, user mgmt, billing, compliance)
- [ ] Reporting and analytics (student, class, school levels)
- [ ] Integrations with external systems (LMS, plagiarism, payments)
- [ ] Security & compliance (audit logs, data privacy, encryption)
- [ ] Content management (CMS pages, email templates, file uploads)

Generate **20-30 custom epics** to ensure comprehensive coverage. Focus on domain-specific features from requirements.

Return ONLY valid JSON, no additional text."""

