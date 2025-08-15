# MindCanvas - AI-Powered Content & Image Explorer

A full-stack web application that allows users to search the web and generate AI images using MCP (Model Context Protocol) servers.

## Features

- **Web Search**: Search the web using Tavily MCP server
- **AI Image Generation**: Generate images using Flux ImageGen MCP server
- **User Authentication**: Secure JWT-based authentication
- **Dashboard**: Manage search and image history
- **Data Export**: Export data to CSV/PDF formats
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works on desktop and mobile devices

## Screenshots

<img src="https://github.com/user-attachments/assets/251a3188-22f4-4f3d-b1b0-19bd2e243015" alt="Alt text" width="400" style="border-radius:15px;"/>

<img src="https://github.com/user-attachments/assets/02e1a0ec-e687-415e-b6de-fc236863bbba" alt="Alt text" width="400" style="border-radius:15px;"/>


## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Database for storing user data and history
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **JWT**: Authentication tokens
- **pytest**: Testing framework

### Frontend
- **React 18**: Frontend framework
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing
- **Playwright**: End-to-end testing

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

5. **Start PostgreSQL:**
   ```bash
   # Option 1: Using Docker
   docker compose up -d db

   # Option 2: Local PostgreSQL
   # Make sure PostgreSQL is running and create database 'MindCanvas'
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env if needed
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

   The app will be available at `http://localhost:3000`

### Docker Setup (Alternative)

Run the entire stack with Docker:

```bash
cd backend
docker compose up --build
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend app on port 3000

## Testing

### Backend Tests

```bash
cd backend
pytest -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

### Frontend Tests

Install Playwright browsers:
```bash
cd frontend
npx playwright install
```

Run E2E tests:
```bash
npm run test:e2e
```

Run tests with UI:
```bash
npm run test:e2e:ui
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `POST /auth/refresh` - Refresh token

### Search
- `POST /search/` - Perform web search
- `GET /search/history` - Get search history

### Image Generation
- `POST /image/generate` - Generate image
- `GET /image/history` - Get image history

### Dashboard
- `GET /dashboard/search` - Get search history for dashboard
- `GET /dashboard/images` - Get image history for dashboard
- `DELETE /dashboard/search/{id}` - Delete search entry
- `DELETE /dashboard/image/{id}` - Delete image entry
- `GET /dashboard/export/csv` - Export data as CSV
- `GET /dashboard/export/pdf` - Export data as PDF


### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
mindcanvas/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and security
│   │   ├── db/             # Database models and CRUD
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # Pydantic models
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   └── docker/             # Docker configurations
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── tests/              # Frontend tests
└── README.md
```

## MCP Integration

The application integrates with MCP (Model Context Protocol) servers:

- **Tavily MCP**: Web search functionality
- **Flux ImageGen MCP**: AI image generation

When API keys are not provided, the app uses mock responses for development.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

