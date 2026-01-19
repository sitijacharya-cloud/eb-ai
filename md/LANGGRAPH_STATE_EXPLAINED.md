# LangGraph State Management - Complete Explanation

## 📍 Where is the State Defined?

The state is defined in **TWO places** in your system:

### 1. **Type Definition** (in `backend/app/workflow.py`)

```python
class EstimationGraphState(TypedDict):
    """State for the estimation workflow graph."""
    raw_requirements: Any  # ProjectRequirement
    analyzed_requirement: Any  # AnalyzedRequirement
    retrieved_epics: Any  # List[Epic]
    generated_epics: Any  # List[Epic] - now includes tasks and efforts (complete)
    final_estimation: Any  # ProjectEstimation
    validation_errors: list
    current_step: str
    retry_count: int
```

**Location**: `/Users/ebpearls/Desktop/Ai estimation/backend/app/workflow.py` (lines 20-29)

This is the **schema/type definition** that tells LangGraph what fields the state should have.

### 2. **Initial State** (in `backend/app/workflow.py`)

```python
def run_estimation_workflow(project_requirement: ProjectRequirement):
    # Build graph
    app = build_estimation_graph()
    
    # Initialize state
    initial_state = {
        "raw_requirements": project_requirement,
        "analyzed_requirement": None,
        "retrieved_epics": None,
        "generated_epics": None,  # Will contain complete epics with tasks and efforts
        "final_estimation": None,
        "validation_errors": [],
        "current_step": "initialized",
        "retry_count": 0
    }
    
    # Run workflow - state gets passed through all agents
    final_state = app.invoke(initial_state)
```

**Location**: `/Users/ebpearls/Desktop/Ai estimation/backend/app/workflow.py`

This is the **actual state object** with initial values that gets passed through the workflow.

---

## 🔄 How State Flows Through All Agents (3-Agent System)

LangGraph automatically passes the state through each agent node. Each agent:
1. **Receives** the current state as input
2. **Reads** data it needs from the state
3. **Returns** a dictionary with **updates** to merge into the state
4. LangGraph **merges** the updates into the state
5. **Passes** the updated state to the next agent

**Note:** The system now uses **3 agents** (down from 5):
- Agent 1: Analyze Requirement
- Agent 2: Retrieve Similar Epics
- Agent 3: Two-Part Processing (Part 0: Keep mandatory unchanged, Part 1: Modify retrieved, Part 2: Generate new custom epics with complete tasks + hours)

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INITIAL STATE                                 │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "raw_requirements": ProjectRequirement(...),                   │
│   "analyzed_requirement": None,                                  │
│   "retrieved_epics": None,                                       │
│   "generated_epics": None,                                       │
│   "final_estimation": None,                                      │
│   "validation_errors": [],                                       │
│   "current_step": "initialized",                                 │
│   "retry_count": 0                                               │
│ }                                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT 1: analyze_requirement_node                   │
├─────────────────────────────────────────────────────────────────┤
│ INPUT (reads from state):                                        │
│   - state["raw_requirements"]                                    │
│                                                                  │
│ PROCESSING:                                                      │
│   - Calls OpenAI to analyze requirements                         │
│   - Creates AnalyzedRequirement object                           │
│                                                                  │
│ OUTPUT (returns dictionary):                                     │
│   return {                                                       │
│     "analyzed_requirement": AnalyzedRequirement(...),            │
│     "current_step": "analyze_requirement_complete"               │
│   }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    LangGraph merges ↓
                           │
┌─────────────────────────────────────────────────────────────────┐
│                    STATE AFTER AGENT 1                           │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "raw_requirements": ProjectRequirement(...),    ← unchanged   │
│   "analyzed_requirement": AnalyzedRequirement(...), ← NEW!      │
│   "retrieved_epics": None,                         ← unchanged  │
│   "generated_epics": None,                                       │
│   "final_estimation": None,                                      │
│   "validation_errors": [],                                       │
│   "current_step": "analyze_requirement_complete",  ← UPDATED!   │
│   "retry_count": 0                                               │
│ }                                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            AGENT 2: retrieve_similar_epic_node                   │
├─────────────────────────────────────────────────────────────────┤
│ INPUT (reads from state):                                        │
│   - state["analyzed_requirement"]                                │
│                                                                  │
│ PROCESSING:                                                      │
│   - Queries vector database with analyzed requirement            │
│   - Retrieves 8 mandatory + 15 similar epics                     │
│                                                                  │
│ OUTPUT (returns dictionary):                                     │
│   return {                                                       │
│     "retrieved_epics": [Epic(...), Epic(...), ...],              │
│     "current_step": "retrieve_similar_epics_complete"            │
│   }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    LangGraph merges ↓
                           │
┌─────────────────────────────────────────────────────────────────┐
│                    STATE AFTER AGENT 2                           │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "raw_requirements": ProjectRequirement(...),                   │
│   "analyzed_requirement": AnalyzedRequirement(...),              │
│   "retrieved_epics": [Epic(...), Epic(...), ...],  ← NEW!       │
│   "generated_epics": None,                                       │
│   "final_estimation": None,                                      │
│   "validation_errors": [],                                       │
│   "current_step": "retrieve_similar_epics_complete", ← UPDATED! │
│   "retry_count": 0                                               │
│ }                                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            AGENT 3: generate_custom_epic_node (TWO-PART)        │
│  Part 0: Keep mandatory unchanged | Part 1: Modify retrieved    │
│  Part 2: Generate new custom epics (all with tasks + hours)    │
├─────────────────────────────────────────────────────────────────┤
│ INPUT (reads from state):                                        │
│   - state["analyzed_requirement"]                                │
│   - state["retrieved_epics"]  (8 mandatory + ~12 similar)       │
│                                                                  │
│ PROCESSING:                                                      │
│   Part 0: Keep 8 mandatory epics UNCHANGED                      │
│   Part 1: Modify ~12 retrieved similar epics                    │
│      - Keep epic/task names exactly as is                       │
│      - Adapt platforms (Web App → Flutter, etc.)                │
│      - Adjust effort hours                                      │
│      - Add tasks only if needed                                 │
│   Part 2: Generate ~20 NEW custom epics with AI                 │
│      - Domain-specific generation                               │
│      - Complete tasks with efforts                              │
│      - Exact deduplication                                      │
│   Result: ~40 complete epics (8 + 12 + 20) ALL WITH TASKS      │
│                                                                  │
│ OUTPUT (returns dictionary):                                     │
│   return {                                                       │
│     "generated_epics": [Epic(complete), ...],  (~40 total)      │
│     "current_step": "generate_custom_epics_complete"             │
│   }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    LangGraph merges ↓
                           │
┌─────────────────────────────────────────────────────────────────┐
│                    STATE AFTER AGENT 3                           │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "raw_requirements": ProjectRequirement(...),                   │
│   "analyzed_requirement": AnalyzedRequirement(...),              │
│   "retrieved_epics": [Epic(...), ...],                           │
│   "generated_epics": [Epic(complete), ...],      ← NEW! DONE!   │
│   "final_estimation": None,                                      │
│   "validation_errors": [],                                       │
│   "current_step": "generate_custom_epics_complete", ← UPDATED!  │
│   "retry_count": 0                                               │
│ }                                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              HELPER: create_final_estimation_node                │
├─────────────────────────────────────────────────────────────────┤
│ INPUT (reads from state):                                        │
│   - state["raw_requirements"]                                    │
│   - state["analyzed_requirement"]                                │
│   - state["generated_epics"]                                     │
│                                                                  │
│ PROCESSING:                                                      │
│   - Aggregates all epics into ProjectEstimation                  │
│   - Calculates total hours by platform                           │
│   - Creates final estimation object                              │
│                                                                  │
│ OUTPUT (returns dictionary):                                     │
│   return {                                                       │
│     "final_estimation": ProjectEstimation(...),                  │
│     "current_step": "create_final_estimation_complete"           │
│   }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VALIDATION NODE                                 │
├─────────────────────────────────────────────────────────────────┤
│ INPUT (reads from state):                                        │
│   - state["final_estimation"]                                    │
│                                                                  │
│ PROCESSING:                                                      │
│   - Checks 8 mandatory epics present                             │
│   - Validates total hours reasonable                             │
│   - Checks all epics have tasks                                  │
│                                                                  │
│ OUTPUT (returns dictionary):                                     │
│   return {                                                       │
│     "validation_errors": [warnings],                             │
│     "current_step": "validation_passed"                          │
│   }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL STATE (END)                             │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "raw_requirements": ProjectRequirement(...),                   │
│   "analyzed_requirement": AnalyzedRequirement(...),              │
│   "retrieved_epics": [Epic(...), ...],                           │
│   "generated_epics": [Epic(complete), ...],                      │
│   "final_estimation": ProjectEstimation(...),                    │
│   "validation_errors": [warnings],               ← UPDATED!     │
│   "current_step": "validation_passed",           ← UPDATED!     │
│   "retry_count": 0                                               │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 How Each Agent Accesses State

### Example from Agent 1 (Analyze Requirement)

**File**: `backend/app/agents/analyze_requirement_agent.py`

```python
def analyze_requirement_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Agent receives state as parameter."""
    
    # READ from state
    raw_requirements = state["raw_requirements"]  # ← Access state data
    
    # Do processing...
    analyzed = AnalyzedRequirement(
        project_name=raw_requirements.project_name,
        domain="utilities",
        features=[...],
        # ...
    )
    
    # RETURN updates (LangGraph will merge these into state)
    return {
        "analyzed_requirement": analyzed,  # ← Add/update this field
        "current_step": "analyze_requirement_complete"  # ← Update this field
    }
```

### Example from Agent 3 (Two-Part Processing: Modify + Generate)

**File**: `backend/app/agents/generate_custom_epic_agent.py`

```python
def generate_custom_epic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent receives state as parameter.
    
    This two-part agent does:
    Part 0: Keep 8 mandatory epics unchanged
    Part 1: Modify ~12 retrieved similar epics
    Part 2: Generate ~20 new custom epics
    All with complete tasks and effort hours!
    """
    
    # READ from state (uses data from Agent 1 and Agent 2)
    analyzed_req = state["analyzed_requirement"]  # ← From Agent 1
    retrieved_epics = state.get("retrieved_epics", [])  # ← From Agent 2
    
    # Separate mandatory and retrieved
    mandatory_epics = [e for e in retrieved_epics if e.is_mandatory]
    similar_epics = [e for e in retrieved_epics if not e.is_mandatory]
    
    all_epics: List[Epic] = []
    
    # Part 0: Add mandatory unchanged
    for mandatory in mandatory_epics:
        all_epics.append(mandatory)
    
    # Part 1 & 2: Modify retrieved + Generate custom with AI
    # ... (comprehensive prompt to OpenAI)
    
    # Process modified retrieved epics (platforms adapted, hours adjusted)
    # Process new custom epics (complete with tasks + efforts)
    
    # RETURN updates (all ~40 epics now have complete tasks with hours!)
    return {
        "generated_epics": all_epics,  # ← ~40 complete epics (8 + 12 + 20)
        "current_step": "generate_custom_epics_complete"
    }
```

---

## 🧩 How LangGraph Handles State

LangGraph uses a **merge strategy** for state updates:

1. **Initial State** is created when workflow starts
2. **Each agent** returns a dictionary with updates
3. **LangGraph merges** the updates into the state:
   - New keys are added
   - Existing keys are overwritten with new values
   - Keys not mentioned in the return dict stay unchanged
4. **Updated state** is passed to the next agent

### Key Points

✅ **State is SHARED** - All agents can access all state fields  
✅ **State is CUMULATIVE** - Each agent adds to the state  
✅ **State is TYPED** - `EstimationGraphState` defines the schema  
✅ **State is AUTOMATIC** - LangGraph handles passing and merging  

---

## 📂 File Locations Summary

| What | Where |
|------|-------|
| **State Schema** | `backend/app/workflow.py` |
| **State Initialization** | `backend/app/workflow.py` |
| **Graph Building** | `backend/app/workflow.py` |
| **Agent 1 (Analyze)** | `backend/app/agents/analyze_requirement_agent.py` |
| **Agent 2 (Retrieve)** | `backend/app/agents/retrieve_similar_epic_agent.py` |
| **Agent 3 (Two-Part: Modify + Generate)** | `backend/app/agents/generate_custom_epic_agent.py` |
| **Helper: create_final_estimation** | `backend/app/workflow.py` |
| **Helper: validate_output** | `backend/app/workflow.py` |
| **Data Models** | `backend/app/models/schemas.py` |
| **Constants (8 Mandatory Epics)** | `backend/app/core/constants.py` |
| **Mandatory Epics JSON** | `backend/app/data/mandatory_epics.json` |

---

## 🎯 Key Takeaways

1. **State Definition**: `EstimationGraphState` (TypedDict) in `workflow.py`
2. **State Initialization**: `initial_state` dictionary in `run_estimation_workflow()`
3. **State Access**: Each agent receives `state: Dict[str, Any]` as parameter
4. **State Updates**: Each agent returns `Dict[str, Any]` with updates
5. **State Merging**: LangGraph automatically merges updates into state
6. **State Flow**: Passed sequentially through **3 agents** + helper nodes
7. **State Persistence**: Each agent can access data from ALL previous agents
8. **Two-Part Agent 3**: Keeps mandatory unchanged, modifies retrieved epics, generates new custom epics - all with complete tasks and hours in one pass!

**Current System: 3 Agents + 2 Helper Nodes**
- **Agent 1**: Analyze Requirement (extract structure)
- **Agent 2**: Retrieve Similar Epics (MySQL vector search, 8 mandatory + ~12 similar epics)
- **Agent 3**: Two-Part Processing (Part 0: Keep mandatory unchanged | Part 1: Modify retrieved | Part 2: Generate custom - all with complete tasks + hours, max_tokens=8000!)
- **Helper 1**: create_final_estimation_node (aggregate to ProjectEstimation)
- **Helper 2**: validate_output_node (check 8 mandatory epics + business rules)

**Recent Improvements (January 2026):**
- ✅ MySQL with vector embeddings (replaced ChromaDB)
- ✅ Platform filtering fix (string comparison for "Flutter", "API", etc.)
- ✅ Token limit optimization (15-25 epics target, max_tokens=8000)
- ✅ Platform mapping ("Web Service" → "API", "Designer" → "CMS")
- ✅ Semantic deduplication in Agent 3
- ✅ 3-tier estimation strategy (pattern matching, AI, rules)

The state acts as a **shared memory** that accumulates information as it flows through the workflow! 🔄

---

**Last Updated**: January 12, 2026  
**Version**: 3.0 (3-Agent Architecture with MySQL & Token Optimization)
