# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this Car Rental Management System built with modern web technologies.

## Project Overview

This is a modern Car Rental Contract Management Web Application built with a clean monorepo architecture:

- **Backend**: FastAPI (Python) with Domain-Driven Design (DDD) running on port 8000
- **Frontend**: Vite + React + TypeScript running on port 3000  
- **Database**: Firebase Firestore (using firebase-admin SDK)
- **Monorepo**: pnpm workspaces for unified dependency management
- **Testing**: pytest (backend) + vitest (frontend) with comprehensive test coverage
- **CI/CD**: GitHub Actions for automated testing and linting

## Project Structure

```
new-structure/
├── package.json                 # Root workspace configuration
├── pnpm-workspace.yaml         # Workspace definitions
├── .github/workflows/          # CI/CD pipelines
├── apps/
│   ├── backend/               # FastAPI application
│   │   ├── app/              # Application source code
│   │   │   ├── main.py       # FastAPI app factory
│   │   │   ├── config.py     # Pydantic settings
│   │   │   ├── domain/       # Business logic & entities
│   │   │   │   ├── entities/ # Contract, User, Car models
│   │   │   │   ├── value_objects/ # Money, DateRange, Location
│   │   │   │   ├── services/ # Domain services
│   │   │   │   └── repositories/ # Repository interfaces
│   │   │   ├── application/  # Use cases & DTOs
│   │   │   │   ├── use_cases/ # Business workflows
│   │   │   │   └── dto/      # Data transfer objects
│   │   │   ├── infrastructure/ # External services
│   │   │   │   ├── persistence/ # Firebase & mock repositories
│   │   │   │   └── dependencies.py # Dependency injection
│   │   │   └── interfaces/   # API layer
│   │   │       ├── api/v1/   # REST endpoints
│   │   │       └── middleware/ # Error handling, CORS
│   │   ├── tests/            # Backend tests
│   │   ├── requirements.txt  # Full dependencies (local dev)
│   │   ├── requirements-ci.txt # CI dependencies (no system libs)
│   │   └── pytest.ini        # Test configuration
│   └── frontend/             # Vite React application
│       ├── src/
│       │   ├── components/   # React components
│       │   ├── pages/        # Route components
│       │   ├── hooks/        # Custom React hooks
│       │   ├── services/     # API client services
│       │   ├── types/        # TypeScript definitions
│       │   ├── utils/        # Utility functions
│       │   └── test/         # Frontend tests
│       ├── package.json      # Frontend dependencies
│       ├── vite.config.ts    # Vite configuration
│       ├── vitest.config.ts  # Test configuration
│       └── eslint.config.js  # Linting configuration
└── packages/                 # Shared packages (future)
```

## Development Commands

### Root Level Commands
```bash
# Install all dependencies across monorepo
pnpm install

# Run both frontend and backend concurrently
pnpm dev

# Run tests across all projects
pnpm test

# Run linting across all projects
pnpm lint

# Build all projects for production
pnpm build
```

### Backend Commands
```bash
# Navigate to backend
cd apps/backend

# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI development server
python app/main.py
# OR using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
PYTHONPATH=. pytest tests/ -v

# Run linting
black app/
isort app/
flake8 app/
mypy app/

# Install CI dependencies (for GitHub Actions)
pip install -r requirements-ci.txt
```

### Frontend Commands
```bash
# Navigate to frontend
cd apps/frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Run tests
pnpm vitest
# OR run tests once
pnpm vitest --run

# Run linting
pnpm lint

# Build for production
pnpm build

# Preview production build
pnpm preview
```

## Architecture Patterns

### Backend: Domain-Driven Design (DDD)

**Domain Layer** (`app/domain/`):
- **Entities**: Core business objects (Contract, User, Car)
- **Value Objects**: Immutable data types (Money, DateRange)
- **Services**: Domain logic that doesn't belong to entities
- **Repositories**: Interfaces for data access

**Application Layer** (`app/application/`):
- **Use Cases**: Business workflows and orchestration
- **DTOs**: Data transfer objects for API communication

**Infrastructure Layer** (`app/infrastructure/`):
- **Persistence**: Firebase and mock repository implementations
- **Dependencies**: Dependency injection container

**Interface Layer** (`app/interfaces/`):
- **API**: REST endpoints and request/response handling
- **Middleware**: Cross-cutting concerns (error handling, CORS)

### Frontend: Modern React with TypeScript

**Component Architecture**:
- Functional components with hooks
- TypeScript for type safety
- React Query for server state management
- React Router for navigation

**State Management**:
- Local state with useState/useReducer
- Server state with React Query
- Global state with Context API when needed

## API Architecture

### Backend Endpoints
- **Base URL**: `http://localhost:8000` (development)
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Health Check**: `GET /health`

**API Versioning**:
- Current: `/api/v1/contracts`
- Future: `/api/v2/` for breaking changes

**Response Format**:
```json
{
  "data": {},
  "message": "Success",
  "status_code": 200
}
```

**Error Format**:
```json
{
  "error": "Validation Error",
  "message": "Invalid request data",
  "status_code": 422,
  "details": []
}
```

### Frontend API Integration
- **Base URL**: `/api/backend/` (proxied to backend)
- **HTTP Client**: Axios with React Query
- **Type Safety**: Generated TypeScript types from backend models

## Environment Configuration

### Backend Environment Variables
```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email

# Optional Services
MEILISEARCH_API_KEY=your-search-key
MOYSAR_PK=your-payment-public-key
MOYSAR_SK=your-payment-secret-key

# Development
PYTHONUNBUFFERED=1
ENVIRONMENT=development
```

### Frontend Environment Variables
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Authentication
VITE_LOGIN_USERNAME=admin
VITE_LOGIN_PASSWORD=password

# Environment
NODE_ENV=development
```

## MCP (Model Context Protocol) Configuration

This project includes MCP configuration for enhanced Claude Code capabilities:

### Configured MCP Servers
- **Firebase MCP Server**: Direct Firebase project management, Firestore operations, Authentication, and 40+ Firebase tools
- **Filesystem MCP Server**: Project file read/write operations with scope limited to project directory
- **Git MCP Server**: Version control operations for repository management

### Setup Requirements
```bash
# Authenticate Firebase CLI (required for Firebase MCP server)
npx -y firebase-tools@latest login --reauth
```

### Configuration File
MCP servers are configured in `.mcp.json` (checked into version control for team collaboration).

### Usage
- MCP servers automatically load when using Claude Code in this project
- Use `/mcp` command to check server status
- See `MCP_SETUP.md` for detailed setup and troubleshooting guide

## Database Design

### Firebase Firestore Collections

**Contracts**:
```typescript
{
  id: string
  user_id: string
  car_id: string
  status: 'draft' | 'active' | 'completed' | 'cancelled'
  start_date: string (ISO)
  end_date: string (ISO)
  total_amount: number
  booking_details: BookingDetails
  extend_details?: ExtendDetails
  transaction_info: TransactionInfo
  installments: Installment[]
  created_at: string (ISO)
  updated_at: string (ISO)
}
```

**Users**:
```typescript
{
  id: string
  name: string
  email: string
  phone: string
  license_number: string
  wallet_balance: number
  created_at: string (ISO)
  updated_at: string (ISO)
}
```

**Cars**:
```typescript
{
  id: string
  make: string
  model: string
  year: number
  license_plate: string
  daily_rate: number
  status: 'available' | 'rented' | 'maintenance'
  created_at: string (ISO)
  updated_at: string (ISO)
}
```

## Testing Strategy

### Backend Testing (pytest)
- **Unit Tests**: Domain entities and services
- **Integration Tests**: API endpoints with TestClient
- **Repository Tests**: Mock and Firebase implementations
- **Coverage**: Aim for >80% code coverage

**Test Structure**:
```python
# tests/test_contracts.py
@pytest.mark.unit
def test_contract_creation():
    # Test domain logic

@pytest.mark.integration
def test_get_contracts_endpoint(client):
    # Test API endpoints
```

### Frontend Testing (vitest + Testing Library)
- **Component Tests**: React component behavior
- **Hook Tests**: Custom hooks logic
- **Integration Tests**: User interactions and workflows
- **E2E Tests**: Critical user journeys (future)

**Test Structure**:
```typescript
// src/test/ContractList.test.tsx
describe('ContractList', () => {
  it('renders contracts correctly', () => {
    render(<ContractList />)
    // Test component
  })
})
```

## CI/CD Pipeline

### GitHub Actions Workflow
**Triggers**: Push to main, Pull Requests
**Steps**:
1. **Setup**: Node.js 20, Python 3.11, pnpm
2. **Install**: All dependencies across monorepo
3. **Test**: Frontend (vitest) + Backend (pytest)
4. **Lint**: ESLint (frontend) + black/isort/flake8 (backend)

**Configuration**: `.github/workflows/test.yml`

### Deployment Strategy
**Development**:
- Local development with hot reload
- Docker Compose for multi-service setup

**Production** (Future):
- Container deployment (Docker)
- Environment-specific configurations
- Health checks and monitoring

## Development Workflow

### Starting Development
```bash
# 1. Clone and setup
git clone <repo-url>
cd new-structure
pnpm install

# 2. Setup backend
cd apps/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Start development servers
cd ../..
pnpm dev  # Starts both frontend and backend
```

### Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# Edit files...

# 3. Test locally
pnpm test
pnpm lint

# 4. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 5. Create PR
gh pr create --title "Add new feature" --body "Description"
```

### Code Quality Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Standard configuration with React rules
- **Python**: black formatting, isort imports, flake8 linting
- **Tests**: Required for new features
- **Documentation**: Update README/CLAUDE.md for significant changes

## Migration from Legacy System

### Completed Migration
- ✅ **Flask → FastAPI**: Modern async framework
- ✅ **Next.js → Vite**: Faster build and development
- ✅ **Monorepo**: Unified dependency management
- ✅ **DDD Architecture**: Clean separation of concerns
- ✅ **Testing**: Comprehensive test setup
- ✅ **CI/CD**: Automated testing and linting

### Future Migration Tasks
- **Domain Logic**: Move business rules from legacy Flask app
- **Database**: Migrate existing data to new schema
- **Authentication**: Implement JWT-based auth
- **UI Components**: Rebuild admin interface with modern React

## Troubleshooting

### Common Issues

**Backend Issues**:
```bash
# Module not found errors
export PYTHONPATH=$PWD

# Firebase connection issues
# Check firebase-service.json credentials

# Port conflicts
# Change port in app/config.py
```

**Frontend Issues**:
```bash
# Dependency conflicts
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Build failures
# Check TypeScript errors
pnpm type-check
```

**CI/CD Issues**:
```bash
# ESLint dependency errors
# Check pnpm-lock.yaml is committed

# Python dependency conflicts
# Use requirements-ci.txt for CI environment
```

## Performance Considerations

### Backend Optimization
- **Async/Await**: Use FastAPI's async capabilities
- **Database**: Implement connection pooling
- **Caching**: Add Redis for frequently accessed data
- **API**: Implement pagination and filtering

### Frontend Optimization
- **Code Splitting**: Lazy load routes and components
- **Bundle Analysis**: Monitor build size
- **State Management**: Optimize React Query cache
- **Assets**: Optimize images and static files

## Security Best Practices

- **Environment Variables**: Never commit secrets
- **Input Validation**: Use Pydantic for backend validation
- **CORS**: Configure appropriate origins
- **Authentication**: Implement proper JWT handling
- **Dependencies**: Regular security updates

## Package Manager Configuration

**Package Manager**: pnpm (v10.12.1)
- **Workspace**: Configured for monorepo
- **Lock File**: pnpm-lock.yaml (committed to repo)
- **Node Version**: 20.x (specified in GitHub Actions)

## Date Formatting Standards

**All dates should be returned as**:
- **Formatted String**: `dd-MM-yyyy HH:mm` format
- **ISO String**: Standard ISO 8601 format
- **Example**: "28-06-2025 15:30" and "2025-06-28T15:30:00.000Z"

## Development Guidelines

### Code Style
- **Backend**: Follow PEP 8, use black formatting
- **Frontend**: Follow ESLint rules, prefer functional components
- **Documentation**: Use docstrings and JSDoc comments
- **Naming**: Use descriptive names, follow language conventions

### Git Workflow
- **Branches**: feature/*, bugfix/*, hotfix/*
- **Commits**: Conventional commits format
- **PRs**: Require CI passes, code review
- **Releases**: Semantic versioning

### Testing Requirements
- **New Features**: Must include tests
- **Bug Fixes**: Add regression tests
- **Coverage**: Maintain >80% coverage
- **Integration**: Test API contracts

This documentation should be updated as the project evolves and new features are added.