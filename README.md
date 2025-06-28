# Car Rental System - FastAPI + Vite Monorepo

A modern car rental management system built with FastAPI backend and Vite React TypeScript frontend, following Domain-Driven Design (DDD) principles.

## 🏗️ Architecture

- **Backend**: FastAPI with DDD architecture (Python 3.11+)
- **Frontend**: Vite + React + TypeScript
- **Database**: Firebase Firestore
- **Package Manager**: pnpm workspaces
- **DevOps**: Docker Compose

## 📁 Project Structure

```
car-rental-system/
├── apps/
│   ├── backend/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── domain/       # Business logic & entities
│   │   │   ├── application/  # Use cases & DTOs
│   │   │   ├── infrastructure/# External services
│   │   │   └── interfaces/   # FastAPI routers
│   │   └── tests/
│   └── frontend/             # Vite React frontend
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── lib/
│       │   └── types/
│       └── public/
├── packages/                 # Shared packages
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- pnpm 8+
- Docker & Docker Compose (optional)

### Development Setup

1. **Install dependencies**:
   ```bash
   pnpm install
   ```

2. **Start development servers**:
   ```bash
   pnpm dev
   ```
   This runs both backend (port 8000) and frontend (port 3000) concurrently.

3. **Individual services**:
   ```bash
   # Backend only
   pnpm dev:backend
   
   # Frontend only  
   pnpm dev:frontend
   ```

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Development Commands

```bash
# Install dependencies
pnpm install

# Development
pnpm dev                    # Both frontend & backend
pnpm dev:backend           # FastAPI server (port 8000)
pnpm dev:frontend          # Vite dev server (port 3000)

# Building
pnpm build                 # Build both apps
pnpm --filter backend build
pnpm --filter frontend build

# Testing
pnpm test                  # Run all tests
pnpm --filter backend test
pnpm --filter frontend test

# Linting
pnpm lint                  # Lint all code
pnpm --filter backend lint
pnpm --filter frontend lint
```

## 🌐 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔗 Frontend Routes

- Home: http://localhost:3000/
- Contracts: http://localhost:3000/contracts
- Bookings: http://localhost:3000/bookings

## 🏭 Production Deployment

```bash
# Build for production
pnpm build

# Start production servers
cd apps/backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
cd apps/frontend && pnpm preview
```

## 🔧 Configuration

### Backend Environment Variables

Create `apps/backend/.env`:
```env
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
FIREBASE_CREDENTIALS_PATH=firebase-service.json
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your-key
MOYSAR_PK=your-public-key
MOYSAR_SK=your-secret-key
SECRET_KEY=your-secret-key
```

### Frontend Environment Variables

Create `apps/frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

## 🧪 Testing

```bash
# Backend tests
cd apps/backend && poetry run pytest

# Frontend tests  
cd apps/frontend && pnpm test
```

## 📦 Package Management

This project uses pnpm workspaces:

```bash
# Add dependency to specific app
pnpm --filter backend add fastapi
pnpm --filter frontend add react-query

# Add dev dependency
pnpm --filter backend add -D pytest
pnpm --filter frontend add -D vitest
```

## 🚀 Migration from Flask + Next.js

This project migrates from a Flask backend and Next.js frontend to:
- ✅ Better performance with FastAPI async support
- ✅ Cleaner architecture with proper DDD separation
- ✅ Faster development with Vite HMR
- ✅ Better TypeScript integration
- ✅ Auto-generated API documentation

## 📚 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Firebase Admin**: Database and authentication
- **Poetry**: Dependency management

### Frontend  
- **Vite**: Build tool and dev server
- **React 18**: UI framework
- **TypeScript**: Type safety
- **TanStack Query**: Data fetching and caching
- **Tailwind CSS**: Styling
- **Radix UI**: Accessible components

### DevOps
- **Docker**: Containerization
- **pnpm**: Fast package manager
- **ESLint**: Code linting
- **Prettier**: Code formatting