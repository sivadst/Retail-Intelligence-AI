# Retail Intelligence AI V2 - SETUP GUIDE

## Quick Start (Docker Recommended)

### Prerequisites
- Docker & Docker Compose installed
- 4GB RAM minimum
- Internet connection (for model downloads)

### Steps

1. **Navigate to project root**
   ```bash
   cd "Retail Intelligence AI"
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (OpenAI API key, etc)
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to be ready** (30-60 seconds)
   ```bash
   docker-compose ps
   ```

5. **Access application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

6. **Create account**
   - Go to http://localhost:3000/register
   - Sign up with email/password
   - Upload sample data

### Local Development (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` for all available options. Critical ones:

```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

## First-Time Usage

1. Register at /register
2. You'll be org owner (all permissions)
3. Navigate to /overview to see dashboard
4. Go to datasets section to upload CSV/Excel
5. Once processed, queries will work in AI assistant

## Troubleshooting

**Ports already in use?**
- Modify docker-compose.yml ports section
- Or kill conflicting processes

**Frontend can't reach backend?**
- Check backend health: http://localhost:8000/health
- Verify CORS in backend/app/main.py
- Check NEXT_PUBLIC_API_URL in frontend/.env

**Database connection error?**
```bash
docker-compose down
docker volume rm <project>_postgres_data
docker-compose up -d
```

**Out of memory?**
- Docker Desktop: increase memory in settings
- Or run backend separately from Docker

## Architecture Overview

```
┌─────────────────┐
│   Next.js (3000)│  ← User interface
└────────┬────────┘
         │ HTTP/HTTPS
┌────────▼────────┐
│ FastAPI (8000)  │  ← API server
├─────────────────┤
│ - Auth          │
│ - Datasets      │
│ - Analytics     │
│ - AI Assistant  │
│ - Forecasting   │
│ - Alerts        │
└────────┬────────┘
         │
    ┌────┼────┬─────────┐
    │    │    │         │
┌───▼──┐│ ┌──▼──┐ ┌──▼──┐
│ PG   │ │ Redis  │ CH   │
│(5432)│ │(6379)  │(9000)│
└──────┘ └────────┘ └─────┘
         Storage    Analytics
```

## API Overview

### Auth
- POST /auth/register
- POST /auth/login
- GET /auth/me
- POST /auth/refresh
- POST /auth/logout

### Datasets
- POST /datasets/upload
- GET /datasets
- GET /datasets/{id}
- DELETE /datasets/{id}

### AI Assistant
- POST /ai/chat
- GET /ai/conversations/{id}

### Analytics (To be completed)
- GET /analytics/kpis
- GET /analytics/sales-over-time
- GET /analytics/sales-by-category

### Forecasting (To be completed)
- POST /forecasting/predict

## Key Features Implemented

✅ Multi-tenant architecture
✅ JWT authentication
✅ Role-based access control (RBAC)
✅ Async database (PostgreSQL)
✅ Background jobs (Celery)
✅ Type safety (TypeScript + Python types)
✅ Error handling
✅ CORS security
✅ Responsive UI

## Files Structure

Frontend:
- `/app` - Next.js pages
- `/components` - React components
- `/stores` - State management (Zustand)
- `/lib` - API client, utilities
- `/types` - TypeScript types

Backend:
- `/app/routers` - API endpoints
- `/app/models` - SQLAlchemy ORM models
- `/app/schemas` - Pydantic request/response
- `/app/services` - Business logic
- `/app/core` - Auth, permissions, exceptions

## Next Steps

1. Try uploading sample retail data
2. Explore analytics dashboard
3. Test AI assistant (requires OpenAI key)
4. Try forecasting feature
5. Set up alerts

For full documentation, see README.md

---

Built for production. Ready to scale. 🚀
