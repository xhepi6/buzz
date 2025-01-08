

# Buzz!

Buzz! is a modern web application built with a FastAPI backend and a SvelteKit frontend. It utilizes Docker Compose for streamlined development and deployment.

## Project Structure

```
Buzz/
├── backend/              # FastAPI backend application
├── frontend/             # SvelteKit frontend application
├── docker/               # Dockerfiles for backend and frontend
├── docker-compose.yaml   # Docker Compose configuration
├── .env                  # Environment variables (excluded from version control)
├── .env.example          # Example environment variables (included in repo)
├── .gitignore            # Git ignore file
├── .pre-commit-config.yaml # Pre-commit hooks configuration
```

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.
- Node.js and Yarn for local frontend development (optional).

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/buzz.git
   cd buzz
   ```

2. Copy the `.env.example` file to create a `.env` file:

   ```bash
   cp .env.example .env
   ```

3. Modify the `.env` file to suit your environment. The `.env.example` file provides a starting point.

4. Start the services using Docker Compose:

   ```bash
   docker-compose up --build
   ```

5. Access the application:

   - Backend: [http://localhost:8000](http://localhost:8000)
   - Frontend: [http://localhost:3000](http://localhost:3000)

## Backend

The backend is built with FastAPI and is configured with the following dependencies:

### Dependencies

- `fastapi>=0.104.0`
- `uvicorn>=0.24.0`
- `aioredis>=2.0.1`
- `pydantic>=2.4.2`
- `pydantic-settings>=2.0.3`
- `python-dotenv>=1.0.0`

### Development Commands

Run the backend locally:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend

The frontend is built with SvelteKit and uses Vite as its build tool.

### Scripts

- `dev`: Run the development server.
- `build`: Build the application for production.
- `preview`: Preview the production build.

Run the frontend locally:

```bash
yarn install
yarn dev
```

## Environment Variables

The environment variables are managed in a `.env` file. Ensure you set the following variables:

```env
# Redis configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Frontend configuration
VITE_API_URL=http://localhost:8000
```

## Pre-commit Hooks

This project uses `pre-commit` hooks for code linting and formatting. Install the hooks:

```bash
pre-commit install
```

Run the hooks manually:

```bash
pre-commit run --all-files
```

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

