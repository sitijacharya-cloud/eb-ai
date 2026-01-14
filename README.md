# EB Estimation Agent

AI-powered system that automates software project estimation by learning from historical data and generating structured effort estimates.

## Features

- 🤖 **AI-Driven Estimation**: Uses GPT-4 mini to analyze requirements and generate estimates
- 📊 **Historical Data Learning**: Leverages past project data for accurate estimates
- 🎯 **Epic & Task Breakdown**: Automatically decomposes projects into epics and tasks
- 🔧 **Platform-Specific**: Estimates for Flutter, Web App, API, CMS
- ⚡ **LangGraph Workflow**: Intelligent multi-agent orchestration


## Architecture

```
User Requirements → Analyze → Retrieve Similar → Generate Epics → 
Decompose Tasks → Estimate Efforts → Validate → Output
```

## Project Structure

```
.
├── backend/
│   └── app/
│       ├── agents/          # LangGraph agents
│       ├── models/          # Pydantic schemas
│       ├── services/        # Business logic
│       ├── api/             # FastAPI endpoints
│       └── core/            # Config & utilities
├── frontend/                # Streamlit UI
├── data/
│   └── templates/          # Historical estimate JSONs
└── tests/                  # Unit tests
```

## Setup

1. **Clone & Install**
```bash
cd "Ai estimation"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Initialize Knowledge Base**
```bash
python -m backend.app.services.knowledge_base init
```

4. **Run Backend**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

5. **Run Frontend**
```bash
streamlit run frontend/app.py
```

6. **View Workflow Graph** (Optional)
```bash
source venv/bin/activate
python show_workflow_graph.py
open workflow_graph.png
```

## Usage

1. Enter project requirements in the Streamlit UI
2. AI analyzes and generates estimation
3. Review epics and tasks
4. Modify estimates as needed
5. Export to JSON/Excel

## API Endpoints

- `POST /api/v1/estimate` - Generate new estimation
- `GET /api/v1/epics` - List all available epics
- `POST /api/v1/templates` - Upload new template

## Development

```bash
# Run tests
pytest

# Format code
black backend/ frontend/

# Lint
ruff check backend/ frontend/
```

## License

Proprietary - EB Pearls
