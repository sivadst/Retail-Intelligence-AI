"""PROJECT STRUCTURE GUIDE

## Directory Layout

```
retail-intelligence-ai-v2/
│
├── 📁 frontend/                          # Next.js 14 Application
│   ├── app/                              # App Router
│   │   ├── layout.tsx                   # Root layout
│   │   ├── page.tsx                     # Landing page
│   │   ├── globals.css                  # Global styles
│   │   ├── (auth)/                      # Auth route group
│   │   │   ├── layout.tsx               # Auth layout
│   │   │   ├── login/page.tsx           # Login page
│   │   │   ├── register/page.tsx        # Register page
│   │   ├── (dashboard)/                 # Protected routes
│   │   │   ├── layout.tsx               # Dashboard shell
│   │   │   ├── overview/page.tsx        # Main dashboard
│   │   │   ├── analytics/page.tsx       # Analytics
│   │   │   ├── forecasting/page.tsx     # Forecasting
│   │   │   ├── ai-assistant/page.tsx    # Chat AI
│   │   │   ├── alerts/page.tsx          # Alerts
│   │   │   ├── reports/page.tsx         # Reports
│   │   │   ├── settings/page.tsx        # Settings
│   │   │   ├── team/page.tsx            # Team management
│   │   └── api/                         # API routes (proxy to FastAPI)
│   ├── components/
│   │   ├── layout/                      # Layout components
│   │   │   ├── Sidebar.tsx              # Navigation sidebar
│   │   │   ├── Header.tsx               # Top header
│   │   ├── dashboard/                   # Dashboard components
│   │   │   ├── KpiCards.tsx             # KPI display
│   │   │   ├── SalesChart.tsx           # Charts
│   │   ├── ai/                          # AI components
│   │   │   ├── ChatInterface.tsx        # Chat UI
│   │   ├── ui/                          # shadcn/ui components
│   ├── hooks/                           # Custom React hooks
│   ├── lib/
│   │   ├── api.ts                       # Axios API client
│   │   ├── utils.ts                     # Utility functions
│   │   ├── constants.ts                 # Constants
│   ├── stores/
│   │   ├── auth.ts                      # Zustand auth store
│   ├── types/
│   │   ├── index.ts                     # TypeScript types
│   ├── public/                          # Static assets
│   ├── package.json                     # Dependencies
│   ├── tsconfig.json                    # TypeScript config
│   ├── next.config.js                   # Next.js config
│   ├── tailwind.config.js               # Tailwind config
│   ├── Dockerfile                       # Docker container
│   └── .gitignore                       # Git ignore
│
├── 📁 backend/                           # FastAPI Application
│   ├── app/
│   │   ├── main.py                      # FastAPI app factory
│   │   ├── config.py                    # Settings/Environment
│   │   ├── database.py                  # SQLAlchemy setup
│   │   ├── dependencies.py              # DI (auth, perms)
│   │   ├── __init__.py                  # Package init
│   │   ├── routers/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Auth endpoints
│   │   │   ├── datasets.py              # Dataset CRUD
│   │   │   ├── ai_assistant.py          # AI chat
│   │   │   ├── analytics.py             # Analytics (stub)
│   │   │   ├── forecasting.py           # Forecasting (stub)
│   │   ├── models/                      # SQLAlchemy ORM
│   │   │   ├── __init__.py              # All models
│   │   │   ├── user.py                  # User model
│   │   ├── schemas/                     # Pydantic validation
│   │   │   ├── __init__.py              # All schemas
│   │   ├── services/                    # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py          # Auth logic
│   │   │   ├── dataset_service.py       # Dataset processing
│   │   │   ├── analytics_service.py     # Analytics logic
│   │   │   ├── forecasting_service.py   # Forecasting
│   │   │   ├── ai_service.py            # LLM service
│   │   ├── core/                        # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py              # JWT, password
│   │   │   ├── permissions.py           # RBAC
│   │   │   ├── exceptions.py            # Custom errors
│   │   ├── tasks/                       # Celery jobs
│   │   │   ├── __init__.py
│   │   │   ├── dataset_tasks.py         # Processing
│   │   │   ├── report_tasks.py          # Reports
│   │   │   ├── alert_tasks.py           # Alerts
│   ├── alembic/                         # Database migrations
│   │   ├── versions/                    # Migration scripts
│   │   ├── env.py                       # Migration config
│   ├── tests/                           # Test suite
│   ├── requirements.txt                 # Python dependencies
│   ├── Dockerfile                       # Docker container
│   └── alembic.ini                      # Alembic config
│
├── 📋 Configuration Files (Root)
│   ├── docker-compose.yml               # Local dev setup
│   ├── .env.example                     # Environment template
│   ├── .env                             # Local environment
│   ├── .gitignore                       # Git ignore rules
│
├── 📚 Documentation (Root)
│   ├── README.md                        # Main documentation
│   ├── SETUP.md                         # Quick start guide
│   ├── API_EXAMPLES.md                  # API usage examples
│   ├── DEPLOYMENT.md                    # Production guide
│   ├── CONTRIBUTING.md                  # Dev guidelines
│   └── SAMPLE_DATA.csv                  # Test data
```

## Key Components

### Authentication Flow
```
Register → Create Org → Hash Password → Create User
   ↓          ↓            ↓               ↓
POST /auth/register
   ↓
Login → Verify Password → Generate Tokens
   ↓        ↓                ↓
POST /auth/login → Response with access_token + refresh_token
   ↓
Store in localStorage
   ↓
Attach to Authorization header for requests
```

### Authorization Flow
```
Request with Bearer token
   ↓
Verify token signature & expiration
   ↓
Load user from database
   ↓
Check user.role against required Permission
   ↓
Execute endpoint (or return 403 Forbidden)
```

### Data Flow: Dataset Upload
```
User selects file (frontend)
   ↓
FormData POST /datasets/upload
   ↓
Save to storage/ directory
   ↓
Create Dataset record (pending)
   ↓
Return Dataset ID
   ↓
(Async) Celery processes:
   - Validate file format
   - Infer schema
   - Parse into PostgreSQL
   - Calculate statistics
   - Update processing_status to "completed"
```

### API Response Format

All endpoints return:
```json
{
  "data": {...},        // On success (200, 201)
  "detail": "..."       // On error (4xx, 5xx)
}
```

Errors include status code + detail string:
```json
{
  "detail": "User role 'viewer' lacks 'delete_dataset' permission"
}
```

## Database Schema

### Core Tables

**organizations**
- id (PK)
- name (unique)
- description
- is_active
- created_at, updated_at

**users**
- id (PK)
- email (unique)
- full_name
- hashed_password
- role (enum: owner, admin, analyst, viewer)
- organization_id (FK)
- is_active, email_verified
- created_at, updated_at, last_login

**datasets**
- id (PK)
- name
- organization_id (FK)
- file_path, file_size, file_type
- row_count, column_count
- columns_schema (JSON)
- processing_status
- created_at, updated_at

**chat_messages**
- id (PK)
- user_id (FK)
- conversation_id
- message_type (user, assistant, system)
- content, sql_query, chart_type
- created_at

**alerts**
- id (PK)
- organization_id (FK)
- name, description
- condition (JSON)
- enabled
- created_at, updated_at

## Naming Conventions

### Files
- React components: PascalCase.tsx (e.g., Dashboard.tsx)
- Pages: lowercase with hyphens (e.g., ai-assistant.tsx)
- Utilities: camelCase.ts (e.g., formatDate.ts)
- API routes: snake_case.py (e.g., auth.py)
- Database models: PascalCase (e.g., User, Organization)

### Functions
- Backend: snake_case (e.g., get_current_user)
- Frontend: camelCase (e.g., handleSubmit)
- Async functions: prefix with async (e.g., async def fetch_data)

### Variables
- Constants: UPPER_SNAKE_CASE
- Regular variables: camelCase (frontend), snake_case (backend)
- Sensitive data: stored in .env, never in code

## Development Workflow

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **Watch frontend logs**
   ```bash
   docker-compose logs frontend -f
   ```

3. **Watch backend logs**
   ```bash
   docker-compose logs backend -f
   ```

4. **Make changes**
   - Frontend changes auto-reload on save
   - Backend requires container restart for models/config changes

5. **Test changes**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/docs

6. **Commit code**
   ```bash
   git add .
   git commit -m "[type]: description"
   git push
   ```

## Adding New Features

### New API Endpoint
1. Create schema in `app/schemas/__init__.py`
2. Create route in `app/routers/new_feature.py`
3. Add service logic in `app/services/new_feature_service.py`
4. Include router in `app/main.py`
5. Test with curl or Postman

### New Frontend Page
1. Create file in `app/(dashboard)/page_name/page.tsx`
2. Add to sidebar navigation in `components/layout/Sidebar.tsx`
3. Import types from `@/types`
4. Use `useAuthStore` for auth check

### New Database Model
1. Create model in `app/models/__init__.py`
2. Create Alembic migration
3. Run migration: `alembic upgrade head`

## Testing

### Backend
```bash
# Run all tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app

# Specific test
docker-compose exec backend pytest tests/test_auth.py::test_login
```

### Frontend
```bash
# Run tests
npm test

# Coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## Performance Considerations

- Use database indexes on frequently queried columns
- Implement caching for KPI calculations
- Paginate large result sets
- Use async processing for heavy computations
- Monitor query performance
- Profile frontend bundle size

## Security Considerations

- Never log sensitive data (passwords, tokens)
- Always validate and sanitize user input
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting
- Use HTTPS in production
- Rotate secrets regularly
- Implement audit logging

---

For detailed docs, see README.md
For API usage, see API_EXAMPLES.md
For deployment, see DEPLOYMENT.md
"""
