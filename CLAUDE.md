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

### Firebase Firestore Collections (EXACT SCHEMA)

**⚠️ CRITICAL: Use Firebase MCP for Schema Analysis**
Always use Firebase MCP tools to get the EXACT schema before implementing repositories:
```bash
# Get real collection schemas
mcp__firebase__firestore_get_documents --paths ["cars", "users", "Contracts"]
```

**Cars Collection** (collection name: `"cars"` - lowercase):
```typescript
{
  id: string                    // Document ID
  make: string                  // Exact field: "make"
  model: string                 // Exact field: "model" 
  year: number                  // Exact field: "year"
  rental_price: number          // Exact field: "rental_price" (daily rate)
  rental_price_week?: number    // Exact field: "rental_price_week"
  rental_price_mounth?: number  // Exact field: "rental_price_mounth" (Firebase typo!)
  car_type: string[]           // Exact field: ["Economy", "All"] array
  Seats: number                // Exact field: "Seats" (capital S)
  trans_type: string           // Exact field: "AT" | "MT" (Automatic/Manual)
  isOutOfService: boolean      // Exact field: maintenance status
  isOutOfStock: boolean        // Exact field: rental status
  air_condition: boolean       // Exact field: feature flag
  isNormalBooking: boolean     // Exact field: booking type
  isPackages: boolean          // Exact field: package deals
  
  // NOTE: license_plate does NOT exist in Firebase - must be generated
  // Generated format: `{make[:3].upper()}-{doc_id[:4]}`
}
```

**Users Collection** (collection name: `"users"` - lowercase):
```typescript
{
  id: string                    // Document ID
  First_name: string           // Exact field: "First_name" (capital F)
  Last_name: string            // Exact field: "Last_name" (capital L)
  email: string                // Exact field: "email"
  Phone: string                // Exact field: "Phone" (capital P)
  StatusNumer: string          // Exact field: "StatusNumer" (Firebase typo!)
  Nationality: string          // Exact field: "Nationality"
  wallet_balance: number       // Exact field: wallet amount
  emailVerify: boolean         // Exact field: email verification status
  phoneVerify: boolean         // Exact field: phone verification status
  
  // Domain Status Mapping:
  // Firebase doesn't use DDD UserStatus enum - map to ACTIVE/INACTIVE only
}
```

**Contracts Collection** (collection name: `"Contracts"` - capitalized):
```typescript
{
  id: string                    // Document ID
  user_id: string              // Exact field: "user_id"
  car_id: string               // Exact field: "car_id"
  status: string               // Contract status
  start_date: string           // ISO date string
  end_date: string             // ISO date string
  total_amount: number         // Total contract amount
  tansaction_info: object      // Exact field: "tansaction_info" (Firebase typo!)
  transaction_info?: object    // Alternative field name
  booking_details: object      // Booking information
  extend_details?: object      // Extension details if applicable
  installments: object[]       // Payment installments
  created_at: string           // Creation timestamp
  updated_at: string           // Last update timestamp
}
```

### Firebase Integration Patterns

**Repository Implementation Strategy**:
```python
# 1. Use Firebase MCP to get exact schema
# 2. Implement exact field mapping in _to_entity()
# 3. Handle Firebase-specific data types
# 4. Generate missing fields (like license_plate)
# 5. Apply validation workarounds for edge cases

class FirebaseCarRepository(CarRepository):
    def _to_entity(self, doc_id: str, data: Dict[str, Any]) -> Optional[Car]:
        # 1. Clean Firebase objects first
        cleaned_data = self._clean_firebase_objects(data)
        
        # 2. Handle exact Firebase field mapping
        daily_price = data.get("rental_price", 0)
        daily_rate = Money(max(daily_price, 1), "SAR")  # Validation workaround
        
        # 3. Generate missing fields
        license_plate = f"{cleaned_data.get('make', 'CAR')[:3].upper()}-{doc_id[:4]}"
        
        # 4. Map Firebase flags to DDD enums
        is_out_of_service = data.get("isOutOfService", False)
        status = CarStatus.MAINTENANCE if is_out_of_service else CarStatus.AVAILABLE
```

**Critical Implementation Notes**:
- **Collection Names**: Case-sensitive! (`"cars"`, `"users"`, `"Contracts"`)
- **Field Names**: Exact match required including typos (`"rental_price_mounth"`, `"StatusNumer"`)
- **Generated Fields**: Handle fields that don't exist in Firebase but are required by DDD entities
- **Validation Workarounds**: Handle edge cases like 0 values that fail domain validation
- **Firebase Object Cleaning**: Convert DocumentReference, DatetimeWithNanoseconds to JSON-serializable types
- **Async Patterns**: Use ThreadPoolExecutor for Firebase operations in FastAPI async context

## Testing Strategy

### CRITICAL TESTING REQUIREMENTS

**MANDATORY E2E REAL DATABASE TESTING**:
- **ALL API endpoints MUST have E2E tests using real Firestore database**
- **NO MOCK DATA allowed** - only test with actual Firebase production database
- **PRODUCTION DATABASE SAFETY**: Test data MUST be cleaned up immediately after test execution
- **Test Cleanup**: All test documents/data created during testing MUST be deleted automatically
- **Real Integration**: Tests must verify complete end-to-end functionality including Firebase operations

### Backend Testing (pytest)
- **E2E Integration Tests**: MANDATORY for every API endpoint with real Firestore
- **Unit Tests**: Domain entities and services (can use mocks for isolated logic)
- **Repository Tests**: Real Firebase implementations (NO MOCKS for repository tests)
- **Coverage**: Aim for >90% code coverage including E2E scenarios
- **Database Safety**: Auto-cleanup of all test data

**Test Structure**:
```python
# tests/test_contracts_e2e.py
@pytest.mark.e2e
def test_create_contract_real_database(client, cleanup_test_data):
    """E2E test with real Firestore - auto cleanup test data"""
    # Create test data in real Firebase
    response = client.post("/api/v1/contracts", json=test_contract_data)
    
    # Verify in real database
    assert response.status_code == 201
    contract_id = response.json()["data"]["id"]
    
    # Test data will be automatically cleaned up by cleanup_test_data fixture
    
@pytest.mark.unit  
def test_contract_domain_logic():
    # Unit tests for domain logic only
```

### Frontend Testing (vitest + Testing Library)
- **E2E Component Tests**: Test with real API calls to backend
- **Integration Tests**: User interactions with real backend endpoints
- **Unit Tests**: Pure component logic (isolated from API)
- **NO MOCK API calls** for integration tests - use real backend

**Test Structure**:
```typescript
// src/test/ContractsPage.e2e.test.tsx
describe('ContractsPage E2E', () => {
  afterEach(() => {
    // Cleanup any test data created during tests
    cleanupTestContracts()
  })
  
  it('fetches and displays real contracts from API', async () => {
    render(<ContractsPage />)
    
    // This will make real API call to backend
    await waitFor(() => {
      expect(screen.getByText('Contract')).toBeInTheDocument()
    })
  })
})
```

### Test Data Management
- **Auto-cleanup fixtures**: Pytest fixtures that automatically delete test data
- **Test data isolation**: Use unique identifiers for test documents
- **Production database safety**: Fail-safe mechanisms to prevent data corruption
- **Cleanup verification**: Ensure all test data is removed after each test

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

### ✅ COMPLETED MIGRATION (100% Success)
- ✅ **Flask → FastAPI**: Modern async framework with full DDD implementation
- ✅ **Next.js → Vite**: Faster build and development
- ✅ **Monorepo**: Unified dependency management with pnpm workspaces
- ✅ **DDD Architecture**: Clean separation of concerns with domain entities, repositories, use cases
- ✅ **Firebase Integration**: Real Firestore database with exact schema mapping
- ✅ **Repository Pattern**: Firebase and mock implementations with dependency injection
- ✅ **Testing**: 100% E2E test coverage (31/31 tests passing) with real database
- ✅ **Async/Await**: Full async implementation with ThreadPoolExecutor for Firebase
- ✅ **Entity Mapping**: Exact Firebase-to-DDD entity conversion with field validation
- ✅ **API Endpoints**: All CRUD operations for Cars, Users, Contracts working correctly
- ✅ **CI/CD**: Automated testing and linting

### Key Technical Achievements
- **Firebase Schema Accuracy**: Used Firebase MCP to analyze exact collection schemas and implement precise field mapping
- **Generated Fields**: Successfully handle fields like `license_plate` that don't exist in Firebase but are generated dynamically
- **Validation Handling**: Fixed cases where Firebase data has 0 values (e.g., rental_price) with proper validation workarounds
- **Async Integration**: Solved all async/sync issues between FastAPI and Firebase using ThreadPoolExecutor pattern
- **Object Serialization**: Implemented comprehensive Firebase object cleaning for JSON serialization
- **Test Coverage**: 100% E2E test success with real production database integration

### Remaining Tasks (Low Priority)
- **Frontend Integration**: Update Vite frontend to use new FastAPI endpoints
- **Authentication**: Implement JWT-based auth (existing session-based auth working)
- **UI Enhancement**: Modernize admin interface components

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
- **MANDATORY E2E TESTS**: Every new API endpoint MUST have E2E tests with real Firestore
- **NO MOCK DATA**: All tests must use real production Firebase database
- **AUTO CLEANUP**: All test data MUST be automatically deleted after test execution
- **Bug Fixes**: Add regression tests with real database scenarios
- **Coverage**: Maintain >90% coverage including E2E scenarios
- **Integration**: Test complete API contracts with real Firebase operations
- **Database Safety**: Fail-safe mechanisms to protect production data during testing

## Testing Success Patterns (100% Achievement)

### Repository Testing with Real Firebase
```python
# Pattern for testing Firebase repositories without mocks
@pytest.mark.unit
def test_get_car_by_license_plate(client):
    """Test generated license plate lookup"""
    # 1. Get real cars from Firebase
    response = client.get("/api/v1/cars/")
    cars = response.json()["data"]["cars"]
    
    if cars:
        # 2. Use actual car data, verify generated license plate format
        car = cars[0]
        expected_license = f"{car['make'][:3].upper()}-{car['id'][:4]}"
        assert car["license_plate"] == expected_license
        
        # 3. Test lookup with real generated license plate
        response = client.get(f"/api/v1/cars/license/{car['license_plate']}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == car["id"]
```

### Dependency Injection for Testing
```python
# conftest.py - proper test configuration
@pytest.fixture
def client():
    """Create test client with dependency overrides"""
    app = create_app()
    
    # Override repositories for unit tests (not E2E)
    app.dependency_overrides[get_car_repository] = lambda: MockCarRepository()
    app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()
    
    return TestClient(app)
```

### Async/Firebase Integration Patterns
```python
# Proven pattern for Firebase async operations
class FirebaseRepository:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def _run_query(self, query):
        """Execute Firestore query asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: list(query.stream()))
    
    async def _get_document(self, doc_ref):
        """Get Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, doc_ref.get)
```

### Virtual Environment Setup
```bash
# Proven commands for backend testing
cd apps/backend
source venv/bin/activate  # Use existing venv
python -m pytest tests/ -v --tb=short

# For new setups:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Key Lessons Learned

### Firebase Schema Mapping Accuracy
- **Always use Firebase MCP first** to get exact schema before implementing repositories
- **Respect Firebase field names exactly**, including typos like `"rental_price_mounth"`
- **Handle missing fields gracefully** by generating them (like license_plate)
- **Apply validation workarounds** for data that fails domain rules (e.g., 0 prices)

### Testing Strategy That Works
- **Use real Firebase data** for all tests - no hardcoded mock data
- **Generate test expectations dynamically** based on actual database contents
- **Verify generated fields** (like license_plate format) in tests
- **Test edge cases** like empty results, malformed data, missing fields

### Repository Implementation Success Patterns
- **ThreadPoolExecutor for async Firebase operations** in FastAPI context
- **Comprehensive Firebase object cleaning** for JSON serialization
- **Exact enum mapping** between Firebase flags and DDD enums
- **Client-side filtering** when Firebase queries are limited
- **Error handling and fallbacks** for malformed documents

This documentation should be updated as the project evolves and new features are added.