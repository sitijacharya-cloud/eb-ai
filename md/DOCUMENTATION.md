# EB Estimation Agent - Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [LangGraph Workflow](#langgraph-workflow)
3. [Refactored Architecture](#refactored-architecture)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)

---

## System Architecture

### Overview
The EB Estimation Agent is an AI-powered system that automates software project estimation using:
- **LangGraph**: Multi-agent workflow orchestration
- **OpenAI GPT-4o-mini**: Natural language understanding and generation
- **MySQL with Vector Embeddings**: Knowledge base for historical data retrieval
- **FastAPI**: REST API backend
- **Streamlit**: User interface

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (Streamlit)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          LangGraph Workflow (3 Agents)              │   │
│  │  1. Analyze → 2. Retrieve → 3. Modify+Generate →   │   │
│  │  Helper: Final Estimation → Helper: Validate       │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────┬───────────────────────┘
                 │                    │
                 ▼                    ▼
        ┌────────────────┐   ┌──────────────────┐
        │  MySQL + Vec   │   │   OpenAI API     │
        │  (~100 epics)  │   │  (GPT-4o-mini)   │
        └────────────────┘   └──────────────────┘
```

---

## LangGraph Workflow

### Agent Flow

To view the visual graph: `python backend/app/show_workflow_graph.py`

```
[START]
   │
   ▼
┌─────────────────────┐
│ 1. Analyze          │ Extract domain, platforms, complexity
│    Requirement      │ from user requirements
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Retrieve Similar │ Query MySQL for matching epics
│    Epics            │ Always include 8 mandatory epics
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Two-Part Agent   │ Part 0: Keep mandatory epics unchanged
│    Modify+Generate  │ Part 1: Modify retrieved epics
│                     │ Part 2: Generate new custom epics
│                     │ (includes tasks and effort hours)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Helper: Create      │ Aggregate all epics into
│ Final Estimation    │ ProjectEstimation object
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Helper: Validate    │ Check business rules
│ Output              │ (retry if needed)
└──────────┬──────────┘
           │
           ▼
        [END]
```

### Agent Details

#### Agent 1: Analyze Requirement
- **Input**: User's project description
- **Processing**: Extracts structured information using OpenAI
- **Output**: `AnalyzedRequirement`
  - Domain (e-commerce, healthcare, etc.)
  - Target platforms (Flutter, Web App, API, CMS, QA)
  - Complexity (Simple, Medium, Complex)
  - Special requirements
  - User types (if applicable)

#### Agent 2: Retrieve Similar Epics
- **Input**: `AnalyzedRequirement`
- **Processing**: 
  - Always includes 8 mandatory epics from configuration
  - Generates embedding from requirements
  - Queries MySQL with vector similarity (~100 epic templates)
- **Output**: `retrieved_epics` with ~20 epics (8 mandatory + ~12 similar)

#### Agent 3: Two-Part Processing (Modify + Generate)
- **Input**: `AnalyzedRequirement` + `retrieved_epics`
- **Processing**: 
  - **Part 0**: Keep 8 mandatory epics unchanged (standard requirements)
  - **Part 1**: Modify ~12 retrieved similar epics
    - Keep epic and task names exactly as is
    - Adapt platforms to target (Web App → Flutter, etc.)
    - Adjust effort hours based on platform and complexity
    - Add tasks only if project needs additional features
    - Never remove existing tasks or rename epics
  - **Part 2**: Generate 15-25 NEW custom epics
    - Cover features not in mandatory/retrieved epics
    - Domain-aware generation (utilities, education, dating, etc.)
    - Complete tasks with descriptions and effort hours
    - Exact deduplication (name matching)
- **Output**: `generated_epics` (~40 complete epics with tasks and hours)
- **Key Change**: Single comprehensive agent handles modification AND generation

#### Helper: Create Final Estimation
- **Input**: All complete epics from Agent 3
- **Processing**: Aggregate into ProjectEstimation object with platform breakdowns
- **Output**: `final_estimation` with total hours and epic counts

#### Agent 6: Validate Output
- **Input**: `final_estimation`
- **Validation Checks**:
  - All mandatory epics present
  - Each epic has tasks
  - Total effort reasonable (10-20,000 hours)
  - Platform assignments valid
- **Output**: Validation result (retry if failed and retry_count < 2)

---

## Refactored Architecture

### What Changed?

#### Before (Old Architecture)
```
Agent 4: Decompose + Estimate (mixed responsibility) ❌
Agent 5: Pass through (underutilized) ❌
```

#### After (New Architecture)
```
Agent 4: Decompose only (clear responsibility) ✅
Agent 5: Intelligent estimation (single source of truth) ✅
```

### Benefits

1. **Separation of Concerns**
   - Agent 4: "What needs to be done?" (decomposition)
   - Agent 5: "How long will it take?" (estimation)

2. **Better Historical Data Usage**
   - Agent 2's 47 epics fully utilized for pattern matching
   - Historical task matching with similarity scoring

3. **Multiple Estimation Strategies**
   - Historical matching (fast & accurate)
   - AI estimation (context-aware)
   - Rule-based (reliable fallback)

4. **Transparent Calculations**
   - Complexity multipliers clearly defined
   - Estimation method tracked per task
   - Full audit trail in logs

5. **Easier Testing & Maintenance**
   - Clear interfaces between agents
   - Single responsibility per agent
   - Independent unit testing

### Estimation Strategy Decision Tree

```
Task with 0 hours?
├─ Has historical hours? → Keep them ✅
├─ Find similar task? → Copy + adjust ✅
├─ AI estimation? → Generate with context ✅
└─ Fallback → Rule-based estimation ✅
```

---

## API Reference

### Endpoints

#### POST /api/v1/estimate
Generate a new project estimation.

**Request Body:**
```json
{
  "project_name": "E-commerce Platform",
  "description": "Mobile app for buyer-seller marketplace...",
  "platforms": ["Flutter", "API", "CMS", "QA"],
  "special_requirements": ["Payment gateway", "Real-time chat"]
}
```

**Response:**
```json
{
  "project_name": "E-commerce Platform",
  "total_hours": 1245,
  "total_hours_by_platform": {
    "Flutter": 520,
    "API": 380,
    "CMS": 245,
    "QA": 100
  },
  "epics": [...],
  "complexity": "Medium",
  "mandatory_epics_count": 7,
  "custom_epics_count": 3
}
```

#### GET /api/v1/epics
List all available epics in the knowledge base.

#### POST /api/v1/templates
Upload a new estimation template to the knowledge base.

---

## Configuration

### Environment Variables

Create `.env` file:
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DB_PATH=./data/chroma_db
LOG_LEVEL=INFO
```

### Knowledge Base

The system uses ChromaDB with 47 pre-loaded epics covering:
- User Authentication
- Payment Integration
- Product Management
- Order Management
- Notifications
- Admin CMS
- Analytics & Reporting
- And more...

#### Initialize/Reset Knowledge Base
```bash
python -m backend.app.services.knowledge_base init
```

#### Add Custom Templates
Place JSON files in `data/templates/` and run:
```bash
python -m backend.app.services.knowledge_base init
```

### Template Format

```json
{
  "name": "Epic Name",
  "description": "Epic description",
  "domain": "E-commerce",
  "is_mandatory": false,
  "tasks": [
    {
      "description": "Task description",
      "efforts": {
        "Flutter": 8,
        "API": 6,
        "QA": 3
      },
      "user_types": ["Buyer"],
      "source": "Historical"
    }
  ]
}
```

---

## Development

### Project Structure

```
.
├── backend/
│   └── app/
│       ├── agents/          # LangGraph agents (5 agents)
│       ├── models/          # Pydantic schemas
│       ├── services/        # OpenAI, ChromaDB services
│       ├── api/             # FastAPI routes
│       ├── core/            # Config, constants, prompts
│       └── workflow.py      # LangGraph orchestration
├── frontend/
│   └── app.py              # Streamlit UI
├── data/
│   └── templates/          # Historical estimation JSONs
├── tests/                  # Unit tests
└── show_workflow_graph.py  # Graph visualization script
```

### Key Files

- `backend/app/workflow.py` - LangGraph workflow definition
- `backend/app/agents/decompose_task_agent.py` - Agent 4 (decomposition)
- `backend/app/agents/estimate_efforts_agent.py` - Agent 5 (estimation)
- `backend/app/core/constants.py` - Prompts and configuration
- `backend/app/services/knowledge_base.py` - ChromaDB management

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=backend/app
```

### Code Quality

```bash
# Format code
black backend/ frontend/

# Lint
ruff check backend/ frontend/

# Type checking
mypy backend/
```

---

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   ```
   Error: No API key provided
   Solution: Add OPENAI_API_KEY to .env file
   ```

2. **ChromaDB Not Initialized**
   ```
   Error: No collection found
   Solution: python -m backend.app.services.knowledge_base init
   ```

3. **Virtual Environment Not Activated**
   ```
   Error: ModuleNotFoundError
   Solution: source venv/bin/activate
   ```

4. **Graph Visualization Fails**
   ```
   Error: Cannot draw graph
   Solution: Make sure you're using venv: source venv/bin/activate
   ```

### Logs

Check logs for detailed information:
- Backend: Console output when running `uvicorn`
- Frontend: Console output when running `streamlit`

---

## Performance

### Typical Response Times
- Agent 1 (Analyze): ~2-3 seconds
- Agent 2 (Retrieve): ~1 second
- Agent 3 (Generate): ~3-5 seconds
- Agent 4 (Decompose): ~2-3 seconds per epic
- Agent 5 (Estimate): ~1-3 seconds (varies by strategy)
- Total: ~10-20 seconds for complete estimation

### Optimization Tips
1. Use historical matching (fastest strategy)
2. Batch AI calls when possible
3. Cache frequent queries
4. Optimize ChromaDB queries

---

## License

Proprietary - EB Pearls
