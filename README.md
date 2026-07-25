# Vendor AI

Vendor AI is an AI-powered inventory management assistant that helps vendors track stock, forecast demand, and get natural-language answers about their inventory — combining a local LLM for conversational queries with a regression model for demand prediction.

Built and presented as a mini-project, with an accompanying academic report and presentation.

## Features

- Conversational interface for querying inventory data in natural language
- Local LLM (via Ollama) for offline, privacy-preserving AI responses — no external API calls needed
- Demand forecasting using a Linear Regression model
- Persistent inventory storage with SQLite
- REST API backend for serving predictions and handling queries

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **LLM:** Phi-3 Mini, served locally via Ollama
- **ML Model:** scikit-learn (Linear Regression) for demand forecasting

## Architecture

1. User submits a query or inventory update through the interface
2. FastAPI routes the request to either:
   - The local LLM (Phi-3 Mini via Ollama) for conversational/natural-language handling
   - The scikit-learn regression model for demand forecasting
3. Results are read from/written to the SQLite database and returned to the user

## Getting Started

### Prerequisites
- Python 3.x
- [Ollama](https://ollama.com) installed locally, with the Phi-3 Mini model pulled:
  ```bash
  ollama pull phi3
  ```

### Setup
```bash
# Clone the repo
git clone https://github.com/TheInfamous-98/vendor-ai.git
cd vendor-ai

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run the backend server
uvicorn main:app --reload
```

Then open `index.html` in your browser, or serve it via a local dev server, to access the frontend.

See `SETUP_AND_MIGRATION.md` for detailed setup and database migration steps.

## Project Background

Vendor AI was developed and presented as a mini-project, with a full academic report, architecture diagrams, and a presentation submitted alongside the working prototype.

## Future Improvements

- Expand forecasting beyond linear regression (e.g. time-series models)
- Add user authentication and multi-vendor support
- Deploy backend for public demo access
