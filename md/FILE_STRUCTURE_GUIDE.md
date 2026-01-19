# EB Estimation Agent - File Structure & Purpose Guide

**Generated:** January 19, 2026  
**Project:** AI-powered Software Estimation System

---

## 📁 Complete Project Structure

```
Ai estimation/
│
├── 📂 backend/                          # Backend API and AI agents
│   ├── __init__.py                      # Python package initializer
│   │
│   ├── 📂 app/                          # Main application code
│   │   ├── __init__.py                  # App package initializer
│   │   ├── main.py                      # 🔴 FastAPI application entry point
│   │   ├── workflow.py                  # 🔴 LangGraph workflow orchestration
│   │   ├── show_workflow_graph.py       # Workflow visualization generator
│   │   │
│   │   ├── 📂 agents/                   # AI Agent implementations (3-agent system)
│   │   │   ├── __init__.py
│   │   │   ├── analyze_requirement_agent.py      # 🔴 Agent 1: Analyzes user requirements
│   │   │   ├── retrieve_similar_epic_agent.py    # 🔴 Agent 2: Retrieves similar epics from DB
│   │   │   └── generate_custom_epic_agent.py     # 🔴 Agent 3: Generates custom epics with tasks
│   │   │
│   │   ├── 📂 api/                      # REST API endpoints
│   │   │   ├── __init__.py
│   │   │   └── estimation.py            # 🔴 /api/v1/estimate endpoint
│   │   │
│   │   ├── 📂 core/                     # Core configuration and constants
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # 🔴 Application configuration (OpenAI, MySQL)
│   │   │   └── constants.py             # 🔴 AI prompts and mandatory epic list
│   │   │
│   │   ├── 📂 data/                     # Static data files
│   │   │   └── mandatory_epics.json     # 🔴 8 mandatory epics with fixed tasks/hours
│   │   │
│   │   ├── 📂 models/                   # Data models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py               # 🔴 Pydantic models (Epic, Task, Platform, etc.)
│   │   │
│   │   ├── 📂 services/                 # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── openai_service.py        # 🔴 OpenAI API wrapper
│   │   │   ├── mysql_knowledge_base.py  # 🔴 MySQL vector DB operations
│   │   │   └── mandatory_epics_service.py # 🔴 Loads mandatory epics from JSON
│   │   │
│   │   └── 📂 utils/                    # Utility functions
│   │       ├── __init__.py
│   │       └── epic_utils.py            # 🔴 Epic name similarity checker
│   │
│   └── 📂 scripts/                      # Standalone utility scripts
│       ├── compare_estimates.py         # 🔴 CLI tool for comparing estimations
│       └── comparison_utils.py          # 🔴 Comparison logic and metrics
│
├── 📂 frontend/                         # Streamlit UI
│   ├── app.py                           # 🔴 Streamlit frontend application
│   └── 📂 assets/
│       └── logo.png                     # EB logo
│
├── 📂 comparison/                       # Estimation comparison files
│   ├── wedmap_template.json            # Actual WedMap estimation (baseline)
│   ├── Wed Map_estimation.json         # AI-generated WedMap estimation
│   ├── gradetime_template.json         # Actual GradeTime estimation
│   └── grade time_estimation.json      # AI-generated GradeTime estimation
│
├── 📂 json_template/                    # Historical project templates (102 templates)
│   ├── template1.json
│   ├── template2.json
│   └── ... (102 total JSON files loaded into MySQL)
│
├── 📂 md/                               # Documentation files
│   ├── DOCUMENTATION.md                 # Complete system documentation
│   ├── SYSTEM_ARCHITECTURE.md           # Architecture deep dive
│   ├── HOW_THE_SYSTEM_WORKS.md          # System workflow explanation
│   ├── LANGGRAPH_STATE_EXPLAINED.md     # LangGraph state management
│   ├── QUICK_START_MYSQL.md            # MySQL setup guide
│   ├── TOKEN_LIMITS_CHALLENGE.md        # Token optimization strategies
│   ├── COMPARISON_TOOL_GUIDE.md         # Comparison tool usage
│   ├── COMPARISON_IMPLEMENTATION.md     # Comparison tool implementation details
│   ├── COMPARISON_WORKFLOW.md           # Comparison workflow
│   ├── WORKFLOW_COMPARISON.md           # Workflow comparison analysis
│   └── CLEAR_AND_INSERT_GUIDE.md        # DB management guide
│
├── 📂 venv/                             # Python virtual environment
│
├── .env                                 # 🔴 Environment variables (API keys, DB credentials)
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # 🔴 Python dependencies
├── README.md                            # Project overview
│
├── workflow_graph.png                   # Visual workflow diagram
├── 4omini_report.md                     # Comparison report (GPT-4o-mini)
├── gpt40miniv2.md                       # Comparison report v2
├── 4.1_report.md                        # Earlier comparison report
│
├── insert_json_mysql.py                 # 🔴 Script to load templates into MySQL
├── mysql_test.py                        # MySQL connection test
└── test_mysql_retrieval.py              # Test vector retrieval from MySQL
```

---

## 🔴 Core Files - Detailed Purpose

### **Backend Core Files**

#### 1. `backend/app/main.py`
**Purpose:** FastAPI application entry point  
**Why Created:** Central hub for starting the REST API server  
**What It Does:**
- Initializes FastAPI application
- Loads configuration from `.env`
- Sets up CORS middleware for frontend communication
- Registers API routes (`/api/v1/estimate`)
- Initializes MySQL knowledge base on startup
- Provides health check endpoint

**Key Functions:**
```python
@app.get("/") - Health check endpoint
@app.on_event("startup") - Initializes knowledge base
```

---

#### 2. `backend/app/workflow.py`
**Purpose:** LangGraph workflow orchestration  
**Why Created:** Manages the 3-agent estimation workflow  
**What It Does:**
- Defines the estimation state graph (StateGraph)
- Connects 3 agents in sequence:
  1. Analyze Requirements → 2. Retrieve Similar Epics → 3. Generate Custom Epics
- Handles state transitions between agents
- Compiles the workflow into executable graph
- Returns final estimation result

**Key Functions:**
```python
build_estimation_graph() - Builds and compiles LangGraph
run_estimation_workflow() - Executes workflow with user input
```

---

#### 3. `backend/app/agents/analyze_requirement_agent.py`
**Purpose:** **Agent 1** - Analyzes user requirements  
**Why Created:** First step in estimation pipeline  
**What It Does:**
- Takes raw user input (project description)
- Calls OpenAI GPT-4o-mini to extract structured information:
  - Domain (e.g., e-commerce, social media)
  - Features (comprehensive list)
  - Platforms (Flutter, Web App, API, CMS)
  - Initial epics (1:1 mapping with features)
  - Epic categories (feature-to-epic mapping)
  - Complexity (simple/medium/complex)
  - User types (Buyer, Seller, Admin, etc.)
- Validates platform selection (corrects Web App vs CMS confusion)
- Returns `AnalyzedRequirement` object

**Key Logic:**
- Platform correction: "mobile + admin dashboard" → Flutter + API + CMS (not Web App)
- Feature extraction: Extracts ALL features (payment methods, AI features, integrations)
- 1:1 epic mapping: Each feature becomes one epic

---

#### 4. `backend/app/agents/retrieve_similar_epic_agent.py`
**Purpose:** **Agent 2** - Retrieves similar epics from MySQL  
**Why Created:** Leverages historical project data  
**What It Does:**
- Loads 8 mandatory epics from `mandatory_epics.json`
- Queries MySQL vector database for similar epics using:
  - Epic categories from Agent 1
  - Vector similarity search (OpenAI embeddings)
- Performs semantic deduplication (avoids duplicates like "User Profile" vs "Profile Management")
- Filters tasks by target platforms (removes irrelevant platforms)
- Returns combined list: mandatory + retrieved epics

**Key Logic:**
```python
# Vector search for each epic category
for epic_name, features in epic_categories.items():
    query = f"Epic: {epic_name}. Features: {features}"
    similar_epics = kb.retrieve_similar_epics(query, n_results=5, threshold=0.4)
```

---

#### 5. `backend/app/agents/generate_custom_epic_agent.py`
**Purpose:** **Agent 3** - Generates custom epics with tasks and hours  
**Why Created:** Creates project-specific estimation  
**What It Does:**
- Takes analyzed requirements + retrieved epics
- Calls OpenAI to generate 15-25 custom epics with:
  - Epic name (with user type suffix if applicable)
  - Description
  - 3-8 high-level tasks per epic
  - Effort estimates per platform (hours)
- Validates epic quality:
  - Checks for low epic count (< 15)
  - Checks for low hours (< expected minimums)
  - Checks platform coverage
- Combines mandatory + retrieved + custom epics
- Returns final estimation

**Key Logic:**
- Platform adaptation: Translates retrieved epic platforms to target platforms
- User-type naming: Adds "- UserType" suffix (e.g., "Dashboard - Admin")
- Conservative estimation: Minimum 6h per task, learns from retrieved patterns

---

### **Backend Services**

#### 6. `backend/app/services/openai_service.py`
**Purpose:** OpenAI API wrapper  
**Why Created:** Centralized OpenAI communication  
**What It Does:**
- Manages OpenAI client initialization
- Provides `generate_json_completion()` method
- Handles JSON parsing and validation
- Uses GPT-4o-mini model (configurable)
- Implements retry logic and error handling

**Key Methods:**
```python
generate_json_completion(prompt, system_message) - Returns parsed JSON
```

---

#### 7. `backend/app/services/mysql_knowledge_base.py`
**Purpose:** MySQL vector database operations  
**Why Created:** Storage and retrieval of historical project templates  
**What It Does:**
- Connects to MySQL database (vector_db)
- Stores epic templates with embeddings (text-embedding-3-small)
- Performs vector similarity search using cosine similarity
- Loads JSON templates from `json_template/` folder
- Retrieves similar epics based on query text

**Key Methods:**
```python
load_templates_from_directory() - Loads 102 JSON templates into MySQL
retrieve_similar_epics(query, n_results, threshold) - Vector search
_get_embedding(text) - Generates OpenAI embeddings
_cosine_similarity(a, b) - Calculates similarity score
```

**Database Schema:**
```sql
Table: json_embeddings
- estimation_id: int
- estimation_name: varchar (e.g., "Template: WedMap")
- epic_id: int
- epic_name: varchar
- task_name: varchar
- platform: varchar (Flutter, API, CMS, Web App)
- estimated_hour: int
- embedding: blob (vector embedding)
```

---

#### 8. `backend/app/services/mandatory_epics_service.py`
**Purpose:** Loads mandatory epics from configuration  
**Why Created:** Ensures all estimations include required epics  
**What It Does:**
- Reads `mandatory_epics.json` file
- Converts JSON to Epic/Task objects
- Validates platform enums
- Returns list of 8 mandatory epics with fixed tasks and hours

**Mandatory Epics:**
1. Project Configuration
2. Database Design
3. Authentication
4. Profile Setup
5. Elastic Search
6. Notification
7. My Profile
8. Deployment

---

### **Backend API**

#### 9. `backend/app/api/estimation.py`
**Purpose:** REST API endpoint for estimation  
**Why Created:** HTTP interface for frontend  
**What It Does:**
- Exposes POST `/api/v1/estimate` endpoint
- Accepts JSON: `{project_name, description, additional_context}`
- Calls `run_estimation_workflow()` to generate estimation
- Returns JSON estimation result with epics/tasks/hours
- Handles errors and validation

**Request Format:**
```json
{
  "project_name": "E-commerce Platform",
  "description": "Build a marketplace...",
  "additional_context": "Need mobile app and admin panel"
}
```

**Response Format:**
```json
{
  "success": true,
  "estimation": {
    "project_name": "...",
    "epics": [...],
    "total_hours": 3278,
    "analyzed_requirement": {...}
  }
}
```

---

### **Backend Configuration**

#### 10. `backend/app/core/config.py`
**Purpose:** Application configuration  
**Why Created:** Centralized settings management  
**What It Does:**
- Loads environment variables from `.env`
- Defines configuration class with:
  - OpenAI API key
  - OpenAI model (gpt-4o-mini)
  - MySQL connection details (host, user, password, database)
- Provides singleton `get_config()` function

---

#### 11. `backend/app/core/constants.py`
**Purpose:** AI prompts and constant values  
**Why Created:** Centralized prompt management  
**What It Does:**
- Defines `MANDATORY_EPICS` list (8 epic names)
- Contains `ANALYZE_REQUIREMENT_PROMPT` (2500+ line prompt for Agent 1)
- Contains `GENERATE_CUSTOM_EPIC_PROMPT` (3000+ line prompt for Agent 3)
- Includes platform selection rules, feature extraction guidelines
- Defines validation checklists and coverage requirements

**Key Prompts:**
- `ANALYZE_REQUIREMENT_PROMPT`: Extracts features, platforms, epics, 1:1 mapping
- `GENERATE_CUSTOM_EPIC_PROMPT`: Generates 15-25 custom epics with tasks/hours

---

### **Backend Data Models**

#### 12. `backend/app/models/schemas.py`
**Purpose:** Pydantic data models  
**Why Created:** Type safety and validation  
**What It Does:**
- Defines all data structures:
  - `Platform` enum (Flutter, Web App, API, CMS)
  - `ProjectRequirement` (user input)
  - `AnalyzedRequirement` (Agent 1 output)
  - `Task` (description, efforts dict, source)
  - `Epic` (name, tasks, is_mandatory, source_template)
  - `EstimationState` (LangGraph state)
  - `EstimationResult` (final output)

---

#### 13. `backend/app/data/mandatory_epics.json`
**Purpose:** Fixed mandatory epic definitions  
**Why Created:** Ensures consistency across all estimations  
**What It Does:**
- Stores 8 mandatory epics with:
  - Epic name
  - Description
  - Pre-defined tasks with fixed hours per platform
- Used by `mandatory_epics_service.py`

**Example Structure:**
```json
{
  "mandatory_epics": [
    {
      "name": "Authentication",
      "description": "User authentication system",
      "tasks": [
        {
          "description": "Email signup",
          "efforts": {"Flutter": 8, "API": 8}
        }
      ]
    }
  ]
}
```

---

### **Backend Utilities**

#### 14. `backend/app/utils/epic_utils.py`
**Purpose:** Epic name similarity checker  
**Why Created:** Prevent duplicate epics with similar names  
**What It Does:**
- Implements `is_similar_epic_name(name1, name2)` function
- Normalizes epic names (removes "MT -", "MA -", common words)
- Calculates word overlap ratio
- Returns True if ≥80% words overlap
- Prevents duplicates like:
  - "User Profile" vs "Profile Management"
  - "Payment Gateway" vs "Payment Integration"
  - "MT - Authentication" vs "Authentication"

---

### **Comparison Tool**

#### 15. `backend/scripts/compare_estimates.py`
**Purpose:** CLI tool for comparing actual vs predicted estimations  
**Why Created:** Measure AI estimation accuracy  
**What It Does:**
- Compares two JSON estimation files across 5 dimensions:
  1. Total Hours Comparison
  2. Platform Coverage
  3. User Role Coverage
  4. Epic Coverage (with fuzzy matching)
  5. Task Coverage (granularity analysis)
- Generates Markdown and PDF reports
- Provides coverage percentages and detailed breakdowns

**Usage:**
```bash
python backend/scripts/compare_estimates.py \
  --actual wedmap_template.json \
  --predicted "Wed Map_estimation.json" \
  --output report
```

---

#### 16. `backend/scripts/comparison_utils.py`
**Purpose:** Comparison logic and metrics  
**Why Created:** Reusable comparison functions  
**What It Does:**
- Extracts platforms, user roles, epics, tasks from JSON
- Implements fuzzy epic matching (SequenceMatcher)
- Calculates coverage percentages
- Groups epics by user type
- Generates status emojis (✅, ⚠️, ❌)

**Key Functions:**
```python
fuzzy_match_epics(actual, predicted, threshold=0.8)
compare_total_hours(actual_hours, predicted_hours)
compare_platforms(actual_platforms, predicted_platforms)
compare_epics(actual_epics, predicted_epics)
compare_tasks(actual_epics, predicted_epics, matched)
compare_epics_by_user_type(actual, predicted)
```

---

### **Frontend**

#### 17. `frontend/app.py`
**Purpose:** Streamlit user interface  
**Why Created:** User-friendly web interface for estimation  
**What It Does:**
- Provides web UI with 2 tabs:
  - "New Estimation": Form for creating estimations
  - "About": System information
- Submits requests to backend API (http://localhost:8000)
- Displays estimation results in expandable table format:
  - Expandable epics with tasks
  - Editable hours per platform
  - Assumption text fields
  - Export to JSON/CSV
- Shows metrics: total hours, epic count, platform breakdown

**Key Features:**
- Real-time estimation generation
- Platform-specific hour editing
- CSV/JSON export
- Visual epic/task hierarchy

---

### **Root Level Files**

#### 18. `.env`
**Purpose:** Environment variables  
**Why Created:** Secure configuration storage  
**What It Contains:**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=Nepal@2001
MYSQL_DATABASE=vector_db
```

---

#### 19. `requirements.txt`
**Purpose:** Python dependencies  
**Why Created:** Package management  
**What It Contains:**
```
fastapi==0.115.0
uvicorn==0.31.0
pydantic==2.9.2
openai==1.51.2
langchain==0.3.4
langgraph==0.2.35
mysql-connector-python==9.1.0
numpy==1.26.4
streamlit==1.40.1
python-dotenv==1.0.1
markdown==3.7
pdfkit==1.0.0
tabulate==0.9.0
```

---

#### 20. `insert_json_mysql.py`
**Purpose:** Load JSON templates into MySQL  
**Why Created:** Initial database setup  
**What It Does:**
- Reads all JSON files from `json_template/` folder
- Generates embeddings for each epic using OpenAI
- Inserts into MySQL `json_embeddings` table
- Loads 102 templates with 2648 epics total

**Usage:**
```bash
python insert_json_mysql.py
```

---

#### 21. `mysql_test.py`
**Purpose:** Test MySQL connection  
**Why Created:** Debug database connectivity  
**What It Does:**
- Tests connection to MySQL server
- Verifies credentials
- Checks database existence

---

#### 22. `test_mysql_retrieval.py`
**Purpose:** Test vector retrieval from MySQL  
**Why Created:** Verify vector search functionality  
**What It Does:**
- Tests `retrieve_similar_epics()` method
- Validates cosine similarity calculations
- Checks embedding quality

---

### **Documentation Files** (`md/` folder)

#### 23. `md/DOCUMENTATION.md`
**Purpose:** Complete system documentation  
**What It Contains:**
- System overview
- Architecture diagram
- Setup instructions
- API documentation
- Usage examples

---

#### 24. `md/SYSTEM_ARCHITECTURE.md`
**Purpose:** Deep dive into architecture  
**What It Contains:**
- 3-agent workflow explanation
- LangGraph state management
- MySQL vector database design
- Platform handling logic
- Token optimization strategies

---

#### 25. `md/HOW_THE_SYSTEM_WORKS.md`
**Purpose:** Step-by-step workflow explanation  
**What It Contains:**
- Detailed flow from user input to estimation output
- Agent-by-agent processing breakdown
- Example inputs and outputs
- Edge case handling

---

#### 26. `md/LANGGRAPH_STATE_EXPLAINED.md`
**Purpose:** LangGraph state management guide  
**What It Contains:**
- EstimationState schema
- State transitions between agents
- Error handling
- State debugging tips

---

#### 27. `md/COMPARISON_TOOL_GUIDE.md`
**Purpose:** How to use comparison tool  
**What It Contains:**
- CLI usage examples
- Report interpretation
- Coverage metrics explained
- Fuzzy matching thresholds

---

#### 28. `md/TOKEN_LIMITS_CHALLENGE.md`
**Purpose:** Token optimization strategies  
**What It Contains:**
- Token limit issues (15-25 epics max)
- Solutions implemented:
  - Targeted retrieval per epic category
  - Summary formatting of retrieved epics
  - max_tokens=8000 limit
- Alternative approaches considered

---

## 🔄 Data Flow

```
1. User Input (Frontend)
   ↓
2. POST /api/v1/estimate (Backend API)
   ↓
3. Workflow Execution (LangGraph)
   ├── Agent 1: Analyze Requirements
   │   ├── Extract features
   │   ├── Identify platforms
   │   └── Create 1:1 epic mapping
   │   ↓
   ├── Agent 2: Retrieve Similar Epics
   │   ├── Load 8 mandatory epics
   │   ├── Query MySQL (vector search)
   │   ├── Filter by platform
   │   └── Deduplicate
   │   ↓
   └── Agent 3: Generate Custom Epics
       ├── Generate 15-25 custom epics
       ├── Add tasks (3-8 per epic)
       ├── Estimate hours per platform
       ├── Validate quality
       └── Combine all epics
       ↓
4. Return Estimation JSON
   ↓
5. Display in Frontend (Expandable Table)
```

---

## 📊 Key Metrics & Files

### Performance Files
- `4omini_report.md` - GPT-4o-mini accuracy: 84.21% epic coverage
- `gpt40miniv2.md` - Latest comparison report
- `workflow_graph.png` - Visual workflow diagram

### Template Files
- `json_template/` - 102 historical project templates
- 2648 total epics in database
- Used for vector similarity search

### Comparison Files
- `comparison/wedmap_template.json` - Actual WedMap estimation (baseline)
- `comparison/Wed Map_estimation.json` - AI-generated (84.21% coverage)
- `comparison/gradetime_template.json` - Actual GradeTime estimation
- `comparison/grade time_estimation.json` - AI-generated

---

## 🚀 Quick Start Commands

### 1. Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Start Frontend
```bash
streamlit run frontend/app.py
```

### 3. Load Templates into MySQL
```bash
python insert_json_mysql.py
```

### 4. Run Comparison
```bash
python backend/scripts/compare_estimates.py \
  --actual wedmap_template.json \
  --predicted "Wed Map_estimation.json" \
  --output report
```

---

## 📈 System Statistics

- **Total Project Files:** ~50 files
- **Total Lines of Code:** ~15,000+ lines
- **Historical Templates:** 102 projects
- **Total Epics in DB:** 2,648 epics
- **Mandatory Epics:** 8 epics (always included)
- **Custom Epics Generated:** 15-25 per project
- **Current Accuracy:** 84.21% epic coverage, 91.90% task coverage
- **Platforms Supported:** 4 (Flutter, Web App, API, CMS)

---

## 🎯 Key Improvements Implemented

1. **Domain-Agnostic Feature Extraction** (9 universal categories)
2. **Feature Coverage Validation** (automatic gap-filling)
3. **Enhanced Epic Generation** (CRITICAL INSTRUCTIONS for coverage)
4. **Platform Filtering Fix** (enum comparison bug fixed)
5. **1:1 Feature-to-Epic Mapping** (prevents feature loss)
6. **Comparison Tool** (5-dimension analysis with fuzzy matching)
7. **Streamlit Interactive UI** (expandable epics, editable hours)

---

**End of File Structure Guide**
