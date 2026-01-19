# EB Estimation Agent - System Architecture & LangGraph Flow

## 🏗️ System Overview

The EB Estimation Agent is an AI-powered software project estimation system that uses **LangGraph** to orchestrate 3 intelligent agents, **MySQL** for knowledge management with vector embeddings, and **OpenAI GPT-4o/GPT-4o-mini** for natural language understanding and generation.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│              (Streamlit Frontend - Port 8501)               │
│  - Project input form                                       │
│  - Platform selection                                       │
│  - Real-time estimation display                            │
│  - CSV export functionality                                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST /api/v1/estimate
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER                                │
│              (FastAPI Backend - Port 8000)                  │
│  - /api/v1/estimate    : Generate estimation                │
│  - /api/v1/epics       : List all templates                 │
│  - /api/v1/stats       : System statistics                  │
│  - /api/v1/reload-templates : Reload knowledge base         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LANGGRAPH WORKFLOW ENGINE                      │
│                   (workflow.py)                             │
│                                                             │
│  ┌─────────────────────────────────────────────┐          │
│  │  State Machine with 3 Main Agents           │          │
│  │                                               │          │
│  │  1. Analyze Requirement                      │          │
│  │  2. Retrieve Similar Epics (MySQL)           │          │
│  │  3. Generate Custom Epics                    │          │
│  │     (includes task decomposition +           │          │
│  │      effort estimation in one pass)          │          │
│  │                                               │          │
│  │  + Helper: Create Final Estimation           │          │
│  │  + Helper: Validate Output                   │          │
│  └─────────────────────────────────────────────┘          │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           │                      │
           ▼                      ▼
┌──────────────────────┐  ┌──────────────────────────┐
│  KNOWLEDGE BASE      │  │    AI SERVICE            │
│  (MySQL + Vectors)   │  │    (OpenAI GPT-4o-mini)  │
│                      │  │                          │
│  • Epic Templates    │  │  • Text Generation       │
│  • Vector Embeddings │  │  • JSON Parsing          │
│  • Task History      │  │  • Semantic Analysis     │
│  • Effort Data       │  │  • Task Generation       │
│                      │  │                          │
│  Database:           │  │  Embeddings:             │
│  • MySQL with vectors│  │  • text-embedding-3-small│
│  • Semantic Search   │  │                          │
│  • Platform Mapping  │  │  Models:                 │
│                      │  │  • gpt-4o / gpt-4o-mini  │
└──────────────────────┘  └──────────────────────────┘
```

---

## 🔄 LangGraph Agent Flow (Detailed)

### **Graph Structure**

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ AGENT 1: Analyze Requirement                                │
│ ───────────────────────────────────────────────────────────│
│ Input:  ProjectRequirement (raw user input)                │
│ Process: • Extract domain (dating, social_media, etc.)     │
│          • Identify features list                          │
│          • Detect platforms (Flutter, Web App, API, etc.)  │
│          • Determine complexity (simple/medium/complex)    │
│          • List initial epics                              │
│ Output:  AnalyzedRequirement object                        │
│ AI Call: OpenAI GPT-4o-mini (JSON mode)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ AGENT 2: Retrieve Similar Epics                            │
│ ───────────────────────────────────────────────────────────│
│ Input:  AnalyzedRequirement                                │
│ Process: • Load 8 mandatory epics from config              │
│          • Build semantic search query from analysis       │
│          • Query MySQL with vector similarity              │
│          • Retrieve most similar epics                     │
│          • Platform filtering (Web Service→API mapping)    │
│          • Deduplicate (remove mandatory duplicates)       │
│ Output:  List of Epics (8 mandatory + similar)             │
│ AI Call: None (uses MySQL vector similarity)               │
│ Mandatory Epics:                                           │
│   1. Authentication                                         │
│   2. Project Configuration                                  │
│   3. Deployment                                             │
│   4. Database Design                                        │
│   5. ElasticSearch                                          │
│   6. Notification                                           │
│   7. My Profile                                             │
│   8. Profile Setup                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ AGENT 3: Generate Custom Epics (TWO-PART PROCESSING)       │
│ ───────────────────────────────────────────────────────────│
│ Input:  AnalyzedRequirement + Retrieved Epics              │
│ Process:                                                    │
│   Part 0: Keep 8 mandatory epics UNCHANGED                 │
│   Part 1: MODIFY ~12 retrieved epics (not mandatory)       │
│           • Keep epic/task names exactly as is             │
│           • Adapt platforms to target (Web→Flutter, etc.)  │
│           • Adjust effort hours for platform/complexity    │
│           • Add tasks only if project needs them           │
│           • Never remove tasks or rename epics             │
│   Part 2: GENERATE ~20 new custom epics                    │
│           • Cover features not in mandatory/retrieved      │
│           • Domain-specific (utilities, education, etc.)   │
│           • Complete tasks with effort hours               │
│           • Exact deduplication (name matching)            │
│                                                             │
│ Output:  Complete epics with tasks and hours               │
│          (~40 total: 8 mandatory + 12 modified + 20 new)   │
│ AI Call: OpenAI GPT-4o-mini (JSON mode, max_tokens=8000)   │
│ Note:    All-in-one: modification + generation + tasks     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ HELPER: Create Final Estimation                            │
│ ───────────────────────────────────────────────────────────│
│ Input:  All complete epics from Agent 3                    │
│ Process: • Aggregate epics into ProjectEstimation          │
│          • Calculate total hours by platform               │
│          • Create metadata                                 │
│ Output:  ProjectEstimation object                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ HELPER: Validate Output                                    │
│ ───────────────────────────────────────────────────────────│
│ Checks:                                                     │
│   1. All 8 mandatory epics present ✓                       │
│   2. Each epic has tasks ✓                                 │
│   3. Total effort reasonable ✓                             │
│   4. At least one platform specified ✓                     │
│   5. Validation warnings logged                            │
│                                                             │
│ Output: Final validated estimation                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
                   END
```

---

## 🎯 Agent Details

### **Agent 1: Analyze Requirement**
- **File**: `backend/app/agents/analyze_requirement_agent.py`
- **Purpose**: Parse natural language requirements into structured data
- **Prompt**: Uses `ANALYZE_REQUIREMENT_PROMPT` from `constants.py`
- **Key Logic**:
  - Flexible platform mapping (e.g., "web" → "Web App")
  - Domain classification (dating vs social_media)
  - Complexity assessment based on feature count
- **Output Schema**: `AnalyzedRequirement` Pydantic model

### **Agent 2: Retrieve Similar Epics**
- **File**: `backend/app/agents/retrieve_similar_epic_agent.py`
- **Purpose**: Fetch relevant historical epics from MySQL knowledge base
- **Key Logic**:
  ```python
  # Step 1: Get ALL mandatory epics (8)
  mandatory_epics = mandatory_service.get_mandatory_epics()
  for epic in mandatory_epics:
      retrieved_epics.append(epic)
  
  # Step 2: Semantic search for similar epics per category
  for epic_name, features in epic_categories.items():
      query = f"Epic: {epic_name}. Features: {', '.join(features)}"
      similar = kb.retrieve_similar_epics(
          query_text=query,
          n_results=3,
          similarity_threshold=0.3
      )
      # Filter duplicates
      retrieved_epics += [e for e in similar if not duplicate]
  
  # Step 3: Platform filtering with mapping
  # Map "Web Service" → "API", "Designer" → "CMS"
  # Filter tasks by target platforms
  ```
- **MySQL**: Uses OpenAI embeddings stored in MySQL for semantic similarity
- **Platform Mapping**: Handles legacy platform names (Web Service, Designer)

### **Agent 3: Generate Custom Epics (Two-Part Processing)**
- **File**: `backend/app/agents/generate_custom_epic_agent.py`
- **Purpose**: Modify retrieved epics AND generate new custom epics with complete tasks and effort hours
- **Prompt**: Uses `GENERATE_CUSTOM_EPIC_PROMPT` (targets 15-25 new epics)
- **Token Management**: max_tokens=8000 to prevent truncation
- **Key Features**:
  - **Part 0**: Keep 8 mandatory epics unchanged (standard requirements)
  - **Part 1**: Modify retrieved similar epics (adaptation to project)
    - Keep epic names and task descriptions exactly as is
    - Adapt platforms to match target (Web App → Flutter, etc.)
    - Adjust effort hours based on platform complexity
    - Add tasks only if project explicitly needs them
    - Never remove existing tasks or rename epics
  - **Part 2**: Generate 15-25 new custom epics (gap filling)
    - Domain-aware epic generation (utilities, education, dating, etc.)
    - Complete tasks with descriptions and effort hours
    - Exact deduplication (name matching only)
    - Learn patterns from retrieved epics
  - **Effort Estimation**: 3-tier strategy built-in
    1. Pattern matching from retrieved epics
    2. AI estimation with baselines
    3. Rule-based fallback
  - Complexity multipliers (0.7x simple, 1.0x medium, 1.5x complex)
  - Platform-specific caps (Flutter: 32h, API: 32h, CMS: 24h, Web App: 32h)
- **Example Output**: ~40 complete epics (8 unchanged + 12 modified + 20 new), all with tasks and hours

### **Helper Nodes**

#### **Create Final Estimation**
- **File**: `backend/app/workflow.py`
- **Purpose**: Aggregate all epics into final ProjectEstimation object
- **Processing**: Sum hours by platform, create metadata, format output

#### **Validate Output**
- **File**: `backend/app/workflow.py`
- **Purpose**: Validate estimation meets business rules
- **Checks**:
  - All 8 mandatory epics present
  - Each epic has tasks
  - Total hours reasonable
  - Platform assignments valid
- **Validation Function**: `validate_estimation_quality()` checks thresholds

---

## 💾 Data Flow

### **1. User Request**
```json
{
  "project_name": "Dating App",
  "description": "A dating app with swipe interface, chat, and premium subscriptions",
  "additional_context": "Focus on iOS and Android mobile platforms"
}
```

### **2. After Agent 1 (Analyze)**
```python
AnalyzedRequirement(
    project_name="Dating App",
    domain="dating",
    features=["swipe interface", "chat", "subscriptions"],
    platforms=[Platform.FLUTTER, Platform.API, Platform.CMS],
    complexity="medium",
    initial_epics=["User Matching", "Chat System", "Payment Integration"]
)
```

### **3. After Agent 2 (Retrieve)**
```python
retrieved_epics = [
    # Mandatory (8)
    Epic(name="Authentication", tasks=[...], is_mandatory=True),
    Epic(name="Project Configuration", tasks=[...], is_mandatory=True),
    Epic(name="Database Design", tasks=[...], is_mandatory=True),
    Epic(name="Deployment", tasks=[...], is_mandatory=True),
    Epic(name="ElasticSearch", tasks=[...], is_mandatory=True),
    Epic(name="Notification", tasks=[...], is_mandatory=True),
    Epic(name="My Profile", tasks=[...], is_mandatory=True),
    Epic(name="Profile Setup", tasks=[...], is_mandatory=True),
    
    # Similar from templates
    Epic(name="Feed and Discovery", tasks=[...], source_template="Dating App Platform"),
    Epic(name="Matched Profiles", tasks=[...], source_template="Dating App Platform"),
    # ... more similar epics
]
# Total: 8 mandatory + similar epics (filtered by platform)
```

### **3. After Agent 2 (Retrieve)**
```python
retrieved_epics = [
    # Mandatory (8) - will remain unchanged
    Epic(name="Authentication", tasks=[...], is_mandatory=True),
    Epic(name="Project Configuration", tasks=[...], is_mandatory=True),
    Epic(name="Database Design", tasks=[...], is_mandatory=True),
    Epic(name="Deployment", tasks=[...], is_mandatory=True),
    Epic(name="ElasticSearch", tasks=[...], is_mandatory=True),
    Epic(name="Notification", tasks=[...], is_mandatory=True),
    Epic(name="My Profile", tasks=[...], is_mandatory=True),
    Epic(name="Profile Setup", tasks=[...], is_mandatory=True),
    
    # Similar from templates (~12) - will be modified
    Epic(name="Feed and Discovery", tasks=[...], source_template="Dating App Platform"),
    Epic(name="Matched Profiles", tasks=[...], source_template="Dating App Platform"),
    # ... more similar epics (these will be adapted in Agent 3)
]
# Total: 8 mandatory + ~12 similar epics
```

### **4. After Agent 3 (Two-Part Processing: Modify + Generate)**
```python
all_epics = [
    # Part 0: 8 mandatory epics (UNCHANGED)
    Epic(name="Authentication", tasks=[...], is_mandatory=True),
    # ... 7 more mandatory
    
    # Part 1: ~12 retrieved epics (MODIFIED)
    Epic(
        name="Feed and Discovery",  # ← Name kept from retrieved
        description="Grade Time assignment feed for students",  # ← Adapted to project
        source_template="Dating App Platform",  # ← Origin preserved
        tasks=[
            Task(description="Feed listing",  # ← Original task kept
                 efforts={Platform.FLUTTER: 14, Platform.API: 12}),  # ← Platforms adapted
            Task(description="Handle card gesture interaction",  # ← Original task kept
                 efforts={Platform.FLUTTER: 10}),  # ← Hours adjusted
            # ... more tasks (some kept, some added)
        ]
    ),
    # ... 11 more modified retrieved epics
    
    # Part 2: ~20 custom epics (NEWLY GENERATED)
    Epic(
        name="Assignment Submission - Student",
        source_template="AI Generated",
        tasks=[
            Task(description="Upload assignment files", efforts={Platform.FLUTTER: 12}),
            Task(description="Submission API", efforts={Platform.API: 16}),
            # ... more tasks
        ]
    ),
    Epic(
        name="Gradebook Management - Teacher",
        source_template="AI Generated",
        tasks=[
            Task(description="Grade entry interface", efforts={Platform.FLUTTER: 14}),
            # ... more tasks
        ]
    ),
    # ... 18 more custom generated epics
]
# Total: ~40 complete epics (8 unchanged + 12 modified + 20 new), all with tasks and hours
```

### **5. Final Output**
```python
ProjectEstimation(
    project_name="Dating App",
    description="...",
    target_platforms=[Platform.FLUTTER, Platform.API, Platform.CMS],
    total_hours=1245,
    platform_breakdown={
        Platform.FLUTTER: 420,
        Platform.API: 680,
        Platform.CMS: 145
    },
    epics=[...],  # 12-18 epics typically
    generated_at=datetime.now()
)
```

---

## 🗄️ Knowledge Base (MySQL)

### **Structure**
```
MySQL Database: vector_db
├── Table: epic_templates
│   ├── Columns:
│   │   ├── id (INT, PRIMARY KEY)
│   │   ├── template_name (VARCHAR)
│   │   ├── domain (VARCHAR)
│   │   ├── epic_name (VARCHAR)
│   │   ├── description (TEXT)
│   │   ├── embedding (JSON - vector array)
│   │   ├── metadata (JSON)
│   │   └── created_at (TIMESTAMP)
│   │
│   └── Indexes:
│       └── Vector similarity search enabled
│
└── Table: epic_tasks
    ├── Columns:
    │   ├── id (INT, PRIMARY KEY)
    │   ├── epic_id (INT, FOREIGN KEY)
    │   ├── task_name (VARCHAR)
    │   ├── platform (VARCHAR) - Flutter, Web App, API, CMS
    │   ├── estimated_hour (INT)
    │   └── created_at (TIMESTAMP)
    │
    └── Platform Mapping:
        ├── "Web Service" → "API"
        └── "Designer" → "CMS"
```

### **Embedding Format**
Documents are embedded using OpenAI text-embedding-3-small:
```
Template: Dating App Platform | Domain: dating_social_networking | 
Dating application with user profiles, matching, feed with swipe interface... | 
Epic: Feed and Discovery. 
Tasks: Feed listing, Handle card gesture interaction, Card animation, 
Manage card stack, Show other users dating profile, Like/Dislike User, 
Its a match screen
```

### **Templates**
Epic templates loaded from JSON files:
1. **Template JSON files in `backend/app/data/templates/`**
2. **Mandatory epics from `backend/app/data/mandatory_epics.json`** (8 epics)
3. **Custom domain templates as needed**

---

## ⚙️ Configuration

### **Environment Variables** (`.env`)
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=vector_db

# Optional
LOG_LEVEL=INFO
MAX_TOKENS=8000
```

### **Platform Enum**
```python
class Platform(str, Enum):
    FLUTTER = "Flutter"    # Mobile (iOS/Android)
    WEB_APP = "Web App"    # Frontend
    API = "API"            # Backend
    CMS = "CMS"            # Admin Panel
    QA = "QA"              # Testing
```

### **Mandatory Epics** (`mandatory_epics.json`)
```python
MANDATORY_EPICS = [
    "Authentication",
    "Project Configuration",
    "Deployment",
    "Database Design",
    "ElasticSearch",
    "Notification",
    "My Profile",
    "Profile Setup"
]
# 8 mandatory epics (increased from 7)
```

---

## 🚀 Performance Optimizations

### **Current Setup**
- **3-Agent Architecture**: Streamlined from 5 agents → faster processing
- **All-in-One Agent 3**: Epic generation + task decomposition + effort estimation in one pass
- **MySQL with Vectors**: Efficient storage and retrieval with vector similarity
- **Platform Mapping**: Handles legacy names (Web Service → API, Designer → CMS)
- **Token Management**: max_tokens=8000 prevents JSON truncation
- **Smart Filtering**: Platform-aware task filtering with string comparison fix
- **Conservative Estimates**: Platform-specific caps and complexity multipliers
- **Epic Target**: 15-25 epics (optimized to avoid token limits)

### **Typical Processing Time**
- Agent 1 (Analyze): ~2-4 seconds
- Agent 2 (Retrieve): ~1-2 seconds (MySQL vector search)
- Agent 3 (Generate + Decompose + Estimate): ~10-20 seconds (single comprehensive pass)
- Helper (Create + Validate): <1 second
- **Total**: ~15-30 seconds for complete estimation

### **OpenAI API Calls**
- Analyze: 1 call
- Generate Custom + Decompose + Estimate: 1 call (all-in-one with max_tokens=8000)
- **Total**: 2 calls per estimation (highly efficient)

---

## 🔧 Key Files

```
backend/
├── app/
│   ├── workflow.py              # LangGraph orchestration (3 agents) ⭐
│   ├── agents/
│   │   ├── analyze_requirement_agent.py
│   │   ├── retrieve_similar_epic_agent.py
│   │   └── generate_custom_epic_agent.py  # All-in-one agent ⭐
│   ├── services/
│   │   ├── mysql_knowledge_base.py    # MySQL + vector manager ⭐
│   │   ├── mandatory_epics_service.py  # 8 mandatory epics
│   │   └── openai_service.py          # GPT-4o wrapper (max_tokens=8000)
│   ├── models/
│   │   └── schemas.py                 # Pydantic models ⭐
│   ├── utils/
│   │   └── epic_utils.py              # Shared utilities (deduplication)
│   ├── core/
│   │   ├── config.py                  # Settings
│   │   └── constants.py               # Prompts & constants ⭐
│   └── data/
│       ├── templates/                 # Historical knowledge ⭐
│       │   ├── *.json template files
│       └── mandatory_epics.json       # 8 mandatory epics ⭐

frontend/
└── app.py                             # Streamlit UI
```

---

## 🎨 Frontend Flow

```
1. User fills form:
   ├── Project Name
   ├── Description
   └── Additional Context

2. Frontend sends POST to /api/v1/estimate
   ├── Timeout: 300 seconds (5 min)
   └── Progress indicators shown

3. Backend runs LangGraph workflow
   └── Returns JSON with ProjectEstimation

4. Frontend displays:
   ├── Summary (total hours, platforms)
   ├── Platform breakdown (pie chart)
   ├── Epic list (expandable)
   └── Task details (efforts per platform)

5. User can export to CSV
```

---

## 📈 Future Enhancements

1. **Streaming Progress**: Real-time agent updates to frontend
2. **Epic Editing**: Allow users to modify epics before finalization
3. **Multi-model Support**: Claude, Gemini integration
4. **Learning Loop**: Feedback system to improve estimates
5. **Cost Calculation**: Convert hours to budget estimates
6. **Team Assignment**: Suggest team composition
7. **Timeline Generation**: Create Gantt charts

---

## 🐛 Debugging

### **Check Logs**
```bash
# Backend logs
tail -f backend/app/main.log

# Agent-specific logs
grep "Agent 3" backend/app/main.log

# Platform filtering issues
grep "Platform" backend/app/main.log
```

### **Test Knowledge Base**
```bash
# Initialize MySQL database
python -m backend.app.services.mysql_knowledge_base init

# Check loaded templates
python -c "from backend.app.services.mysql_knowledge_base import get_knowledge_base; kb = get_knowledge_base(); print(f'Loaded epics: {kb.count_epics()}')"
```

### **Test Single Agent**
```python
from backend.app.agents import analyze_requirement_node
from backend.app.models.schemas import ProjectRequirement

requirement = ProjectRequirement(
    project_name="Test App",
    description="A test application",
    additional_context=""
)

state = {"raw_requirements": requirement}
result = analyze_requirement_node(state)
print(result["analyzed_requirement"])
```

---

## 📚 Technology Stack

- **Orchestration**: LangGraph 0.2+
- **AI**: OpenAI GPT-4o / GPT-4o-mini + text-embedding-3-small
- **Vector DB**: MySQL with vector support (or PGVector)
- **Backend**: FastAPI 0.115+
- **Frontend**: Streamlit 1.40+
- **Validation**: Pydantic 2.10+
- **Language**: Python 3.9+
- **Database**: MySQL 8.0+

---

**Last Updated**: January 12, 2026  
**Version**: 3.0.0 (3-Agent Architecture with Token Optimization)
