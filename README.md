# Buzz! - Social Gaming Platform

A modern web application for social gaming, built with FastAPI (backend) and SvelteKit (frontend). The project uses Docker for containerization and MongoDB for data storage.

## Project Structure
```
buzz/
├── backend/
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configurations
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   └── static/      # Static files
│   ├── scripts/         # Utility scripts
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/            # SvelteKit source code
│   ├── static/         # Static assets
│   ├── package.json    # Node.js dependencies
│   ├── tailwind.config.js
│   └── vite.config.js
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── mongo-init.js   # MongoDB initialization script
└── docker-compose.yaml
```

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd buzz
```

2. Create environment files:
```bash
# Root environment file
cp .env.example .env

# Frontend environment file
cp frontend/.env.example frontend/.env
```

3. Start the application:
```bash
docker compose up --build
```

The services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend API Docs: http://localhost:8000/docs

## Environment Configuration

### Root `.env`
```env
# JWT Settings
JWT_SECRET_KEY=your-secret-key-please-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB Settings
MONGODB_URL=mongodb://root:example@mongodb:27017
MONGODB_DB=buzzdb

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# MongoDB Root Credentials
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
```

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000
```

## Development

### Backend (FastAPI)

Key dependencies:
- FastAPI 0.104.0+
- Motor 3.3.0+ (MongoDB async driver)
- Pydantic 2.4.2+
- Python-Jose (JWT)
- Uvicorn

For local development:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (SvelteKit)

Key features:
- SvelteKit
- TailwindCSS
- ESLint
- Vite

For local development:
```bash
cd frontend
npm install
npm run dev
```

## Docker Setup

The project uses three Docker containers:
- `frontend`: SvelteKit application
- `backend`: FastAPI application
- `mongodb`: MongoDB database

Build and start:
```bash
docker compose up --build
```

Stop and remove volumes:
```bash
docker compose down -v
```

## Database

MongoDB is automatically initialized with sample games data through `docker/mongo-init.js`. The database name is configured as `buzzdb`.

## Available Games

The application comes with pre-configured games:
- Mafia (6-12 players)
- Spyfall (4-8 players)

Games can be modified by editing `docker/mongo-init.js`.

## API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
