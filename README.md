# music-recommendation-llm-app

A music recommendation app using RAG from a Hugging Face dataset and a lightweight LLM backend.

## Requirements

- Node.js and npm
- Python 3
- `AIVERDE_API_KEY` for the LLM backend

## Install

1. Install frontend dependencies:
   ```bash
   npm install
   ```

2. Install backend dependencies if needed:
   ```bash
   python3 -m pip install flask flask-cors langchain langchain-litellm chromadb requests
   ```

## Run the backend

1. Set your API key:
   ```bash
   export AIVERDE_API_KEY="your_key_here"
   ```

2. Start the Flask API:
   ```bash
   python3 web_api.py
   ```

3. The backend listens on `http://0.0.0.0:8000`.

## Run the frontend

1. Start Vite:
   ```bash
   npm run dev
   ```

2. Open the local URL shown in the terminal, usually `http://localhost:5173`.

## Project structure

- `web_api.py` — Flask backend entrypoint
- `rag.py` — retrieval logic for query-based recommendations
- `database/api.py` — Hugging Face MusicSem dataset ingestion
- `database/db.py` — Chroma DB collection and query helpers
- `src/` — frontend React application

## Notes

- The app uses RAG context from the `MusicSem` dataset and includes Spotify links in the recommendation prompt.
- If you need to rebuild or extend the dataset, update `database/api.py` and run the backend again.


## TO RUN THE PROGRAM

