# Answer Agent

A conversational AI agent that can help with calculations, keynote presentations, and emails.

## Project Structure

- `backend/`: Contains the FastAPI backend code
  - `main.py`: The main API server
  - `clients/`: API clients for Gemini MCP
  - `servers/`: MCP servers for various tools (calculator, keynote, email)
- `frontend/`: Contains the React frontend code
  - `src/`: Source code
  - `public/`: Static assets

## Setup and Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- uv (Python package manager)

### Backend Setup

1. Install dependencies using uv:
   ```
   uv sync
   ```

2. Create a `.env` file with your API keys (see `.env_template` for format)

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the frontend:
   ```
   npm run build
   ```

## Running the Application

1. Start the backend server:
   ```
   cd backend
   uv run python backend/main.py
   ```

2. For development, you can run the frontend separately:
   ```
   cd frontend
   npm run dev
   ```

3. Access the application at http://localhost:8000 (when running only the backend)
   or http://localhost:3000 (when running the frontend separately in development mode)

## API Endpoints

- `POST /api/query`: Accepts a JSON body with a `query` field containing the user's question.

## Tools Available

The agent has access to the following tools:
- Calculator: For mathematical calculations
- Keynote: For presentation-related tasks
- Email: For email-related functionality
