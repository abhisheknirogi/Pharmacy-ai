"""
ARCHITECTURE.md - System Architecture & Design Documentation

This document describes the overall architecture, design decisions, 
and technical implementation of PharmaRec AI.
"""

# PharmaRec AI - System Architecture

## Overview

PharmaRec AI is a enterprise-grade, AI-powered pharmacy management platform built with modern technologies and best practices for scalability, reliability, and maintainability.

**Key Principles:**
- Microservices-ready separation of concerns
- Horizontal scalability
- Event-driven architecture (ready for queuing)
- Observable and monitorable
- Security-first design
- Type-safe codebase (Python+TypeScript)

---

## Directory Structure & Module Organization

```
pharmarec-ai/
├── backend/                     # FastAPI backend service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application factory
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── exceptions.py       # Custom exception classes
│   │   ├── middleware.py       # HTTP middleware (error, logging, security)
│   │   ├── responses.py        # Standardized response models
│   │   │
│   │   ├── api/                # API layer
│   │   │   ├── routes/         # Route handlers (grouped by domain)
│   │   │   │   ├── auth.py     # Authentication endpoints
│   │   │   │   ├── inventory.py
│   │   │   │   ├── sales.py
│   │   │   │   ├── reorder.py
│   │   │   │   └── pdf_parser.py
│   │   │
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── medicine.py
│   │   │   ├── sale.py
│   │   │   └── pharmacy.py
│   │   │
│   │   ├── schemas/            # Pydantic validation schemas
│   │   │   ├── user.py
│   │   │   ├── medicine.py
│   │   │   ├── sale.py
│   │   │   └── pharmacy.py
│   │   │
│   │   ├── services/           # Business logic layer
│   │   │   ├── reorder_engine.py    # AI reorder logic
│   │   │   ├── sales_reader.py      # File parsing
│   │   │   └── expiry_alerts.py     # Expiry detection
│   │   │
│   │   ├── ml_client/          # ML integration
│   │   │   └── reorder_predictor.py
│   │   │
│   │   └── utils/              # Utilities
│   │       └── logging.py
│   │
│   ├── tests/                   # Test suite
│   │   └── test_backend.py
│   │
│   └── pyproject.toml
│
├── frontend/                    # Next.js frontend
│   ├── src/
│   │   ├── app/                # App router pages
│   │   ├── components/         # React components
│   │   ├── lib/                # Utilities & API client
│   │   ├── hooks/              # Custom React hooks
│   │   └── types/              # TypeScript types
│   │
│   ├── package.json
│   └── tsconfig.json
│
├── ml-engine/                  # Machine learning
│   ├── inference/
│   │   └── predict.py          # Prediction engine
│   ├── training/
│   │   ├── train_reorder.py    # Model training
│   │   └── train_expiry.py
│   ├── models/                 # Serialized models
│   └── data/
│       ├── raw/
│       └── processed/
│
├── desktop-agent/              # Windows desktop agent
│   └── agent_v2.py
│
├── infra/                      # Infrastructure
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   └── Dockerfile.frontend
│   ├── nginx/                  # Reverse proxy config
│   ├── prometheus/             # Monitoring config
│   └── k8s/                    # Kubernetes manifests (future)
│
├── scripts/                    # Utility scripts
│   ├── seed_db.py
│   ├── health_check.py
│   └── backup.sh
│
├── tests/                      # Integration tests
│   └── test_backend.py
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── versions/
│   └── script.py.mako
│
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production
├── requirements.txt
├── .env.example
├── .env.production
├── Makefile
├── README.md
├── IMPLEMENTATION_COMPLETE.md
├── PRODUCTION_DEPLOYMENT.md
└── ARCHITECTURE.md
```

---

## Design Patterns & Principles

### 1. Layered Architecture

```
┌─────────────────────────────────────┐
│ Presentation Layer (REST API/Docs)  │
├─────────────────────────────────────┤
│ Route Handlers (FastAPI Routes)     │
├─────────────────────────────────────┤
│ Business Logic (Services Layer)     │
├─────────────────────────────────────┤
│ Data Access (Models/Database)       │
├─────────────────────────────────────┤
│ External Services (ML, Files, etc)  │
└─────────────────────────────────────┘
```

**Benefits:**
- Clear separation of concerns
- Easy to test each layer independently
- Simple to scale individual components
- Straightforward to replace components

### 2. Dependency Injection

```python
# Backend uses FastAPI's dependency injection
from fastapi import Depends

@router.get("/medicines")
def get_medicines(db: Session = Depends(get_db)):
    return db.query(Medicine).all()
```

**Benefits:**
- Easy testing (mock dependencies)
- Loose coupling between components
- Clear requirements declaration

### 3. Service Layer Pattern

```python
# Business logic isolated in services
class ReorderService:
    @staticmethod
    def generate_suggestions(medicines: List[Medicine]) -> List[ReorderSuggestion]:
        # Complex logic here
        pass

# Route handlers call services
@router.get("/suggestions")
def get_suggestions(db: Session = Depends(get_db)):
    service = ReorderService()
    return service.generate_suggestions(db.query(Medicine).all())
```

**Benefits:**
- Complex logic testable independently
- Reusable across routes
- Easy to add new features

### 4. Repository Pattern (Optional - Future)

```python
# Repository abstracts database access
class MedicineRepository:
    def get_all(self) -> List[Medicine]: ...
    def get_by_id(self, id: int) -> Optional[Medicine]: ...
    def save(self, medicine: Medicine) -> Medicine: ...
    
# Services use repositories
class MedicineService:
    def __init__(self, repo: MedicineRepository):
        self.repo = repo
    
    def get_all_with_low_stock(self) -> List[Medicine]:
        return [m for m in self.repo.get_all() if m.stock_qty < m.reorder_level]
```

---

## Request/Response Flow

### Successful Request

```
1. HTTP Request
   │
   ▼
2. Nginx (Rate Limit, SSL Termination)
   │
   ▼
3. FastAPI Middleware Stack
   ├─ CORS (Allow origins)
   ├─ Security Headers (Add headers)
   ├─ Rate Limiting (Check limit)
   ├─ Request Logging (Log details)
   └─ Exception Handling (Catch errors)
   │
   ▼
4. Route Handler (Validation via Pydantic)
   │
   ▼
5. Business Logic (Service Layer)
   │
   ▼
6. Database Operations (SQLAlchemy)
   │
   ▼
7. Response Construction (SuccessResponse)
   │
   ▼
8. Middleware processing (add headers)
   │
   ▼
9. HTTP 200 Response with JSON body
```

### Error Request

```
1. HTTP Request
   │
   ▼
2. Middleware Stack
   │
   ▼
3. Route Handler or Service throws PharmaRecException
   │
   ▼
4. ErrorHandlingMiddleware catches exception
   │
   ▼
5. Logs error with context
   │
   ▼
6. Returns ErrorResponse with proper status code
   │
   ▼
7. HTTP 4xx/5xx Response
```

---

## Data Models & Relationships

### Entity Relationship Diagram

```
┌──────────────┐
│ Users        │
├──────────────┤
│ id (PK)      │
│ email        │
│ password_hash│
│ full_name    │
│ is_active    │
│ created_at   │
└──────┬───────┘
       │
       │ Admin/Staff
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
┌──────────────┐            ┌──────────────┐
│ Pharmacy     │            │ Medicine     │
├──────────────┤            ├──────────────┤
│ id (PK)      │            │ id (PK)      │
│ name         │            │ name         │
│ address      │            │ generic_name │
│ phone        │            │ batch_no     │
│ email        │            │ stock_qty    │
│ license_no   │            │ reorder_level│
│ created_at   │            │ expiry_date  │
└──────────────┘            │ price        │
                            │ manufacturer │
                            │ created_at   │
                            │ updated_at   │
                            └──────┬───────┘
                                   │
                                   │ One-to-Many
                                   │
                                   ▼
                            ┌──────────────┐
                            │ Sales        │
                            ├──────────────┤
                            │ id (PK)      │
                            │ medicine_id  │ (FK)
                            │ qty_sold     │
                            │ unit_price   │
                            │ total_amount │
                            │ sale_date    │
                            │ notes        │
                            │ created_at   │
                            └──────────────┘
```

### Key Relationships

**Users ↔ Pharmacy** (Many-to-One)
- Multiple users can manage one pharmacy
- Future: Users can manage multiple pharmacies

**Medicine ↔ Sales** (One-to-Many)
- One medicine has many sales transactions
- Enables sales history and analytics

**Medicine ↔ Expiry Alerts** (Future)
- Track expiry dates
- Generate alerts 30/60/90 days before expiry

---

## API Endpoint Architecture

### RESTful Conventions

```
# Inventory Management
GET    /api/inventory                 # List medicines
POST   /api/inventory                 # Create medicine
GET    /api/inventory/{id}            # Get single medicine
PUT    /api/inventory/{id}            # Update medicine
DELETE /api/inventory/{id}            # Delete medicine
GET    /api/inventory/search          # Search medicines

# Sales Tracking
POST   /api/sales                     # Record sale
GET    /api/sales                     # Get sales history
GET    /api/sales/summary             # Sales analytics
GET    /api/sales/daily-revenue       # Revenue report

# AI Reorder
GET    /api/reorder/suggestions       # AI suggestions
GET    /api/reorder/{medicine_id}     # Prediction for medicine
GET    /api/reorder/analysis          # Detailed analysis

# Authentication
POST   /api/auth/register              # Register user
POST   /api/auth/login                 # Login (JWT)
GET    /api/auth/me                    # Current user

# Health & Monitoring
GET    /health                         # Health check
GET    /version                        # Version info
GET    /diagnostics                    # System diagnostics
```

### Response Format (Standardized)

**Success (200)**
```json
{
  "success": true,
  "data": { /* ... */ },
  "message": "Operation successful"
}
```

**Paginated (200)**
```json
{
  "success": true,
  "data": [ /* array */ ],
  "meta": {
    "current_page": 1,
    "page_size": 20,
    "total_items": 500,
    "total_pages": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

**Error (4xx/5xx)**
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "status_code": 400,
  "request_id": "uuid",
  "details": { /* optional */ }
}
```

---

## Security Architecture

### Authentication Flow

```
1. User Registration
   └─ Email + Password
   └─ Hash password with bcrypt
   └─ Store in database
   
2. User Login
   └─ Verify email exists
   └─ Compare password with hash (bcrypt.verify)
   └─ Generate JWT token (expire in 24h)
   └─ Return token to client
   
3. Subsequent Requests
   └─ Client includes "Authorization: Bearer <token>"
   └─ Server verifies JWT signature
   └─ Server extracts user_id from token
   └─ Route handler receives authenticated user
   
4. Token Expiry
   └─ Client receives 401 Unauthorized
   └─ Frontend redirects to login
   └─ User must re-authenticate
```

### Authorization Levels (Future Enhancement)

```
- Admin
  └─ Full system access
  └─ User management
  └─ Configuration
  
- Manager
  └─ Inventory management
  └─ Sales reporting
  └─ Reorder approvals
  
- Staff
  └─ POS/Sales entry
  └─ Inventory view
  └─ Limited reporting
```

### Data Protection

**In Transit:**
- HTTPS/TLS 1.2+ for all connections
- Certificate pinning (optional, for mobile)

**At Rest:**
- Passwords hashed with bcrypt (cost factor 12)
- Database passwords encrypted in ENV
- Sensitive config in secrets management (Vault, AWS Secrets Manager)

**Future Enhancements:**
- Database encryption (TDE)
- Encryption key rotation
- Audit logging for compliance

---

## Scalability Architecture

### Horizontal Scaling

```
Load Balancer (Nginx)
│
├─ Backend Instance 1 (8000)
├─ Backend Instance 2 (8001)
├─ Backend Instance 3 (8002)
│
Shared Resources:
├─ Database (PostgreSQL primary + replica)
├─ Cache (Redis cluster)
├─ Session store (Redis)
└─ Static assets (S3/CDN)
```

### Caching Layers

```
Level 1: Nginx Cache (Static assets)
└─ CSS, JS, images
└─ Cache-Control headers
└─ 30 days for versioned assets

Level 2: Redis Cache (API responses)
└─ Medicine list (1 hour)
└─ Sales summary (30 minutes)
└─ Reorder suggestions (1 hour)

Level 3: Database Query Cache (via ORM)
└─ SQLAlchemy query result caching
└─ Invalidated on writes
```

### Database Scaling

**Current (SQLite):**
- Single file database
- Good for development
- Up to ~100MB data

**Production (PostgreSQL):**
- Primary-Replica replication
- Read replicas for analytics
- Connection pooling (20-50 connections)
- Query optimization and indexing

**Future:**
- Sharding by pharmacy_id
- Materialized views for analytics
- TimescaleDB for time-series data (sales history)
- Read-only replicas in different regions

---

## Error Handling & Resilience

### Exception Hierarchy

```python
PharmaRecException (base)
├─ ValidationError (422)
├─ AuthenticationError (401)
├─ AuthorizationError (403)
├─ ResourceNotFoundError (404)
├─ DuplicateResourceError (409)
├─ DatabaseError (500)
├─ ExternalServiceError (503)
├─ RateLimitError (429)
└─ ConfigurationError (500)
```

### Retry Strategy

```python
# Transient failures (retry with backoff)
- Connection timeouts
- Database connection pool exhausted
- External service temporarily unavailable

# Permanent failures (don't retry)
- Invalid authentication
- Resource not found
- Input validation errors

# Backoff strategy
- Attempt 1: immediately
- Attempt 2: wait 1s
- Attempt 3: wait 2s
- Attempt 4: wait 4s
- Max 3-4 attempts
```

### Circuit Breaker Pattern (Future)

```python
# Prevent cascading failures
- Track failure rate
- Open circuit on high failure rate
- Fast-fail new requests
- Half-open to test recovery
- Resume on successful requests
```

---

## Monitoring & Observability

### The Three Pillars

**1. Metrics (Prometheus)**
- Request rate (RPS)
- Response time (p50, p95, p99)
- Error rate
- Resource usage (CPU, memory)

**2. Logs (ELK Stack)**
- Request entry/exit
- Database operations
- Errors and warnings
- Business-relevant events

**3. Traces (Jaeger - Future)**
- Request path through system
- Service dependencies
- Timing of each component
- Error propagation

### Key Performance Indicators

```
Availability (SLA: 99.9%)
└─ Uptime monitoring
└─ Alerting on downtime

Performance (SLO)
├─ p95 latency < 200ms
├─ p99 latency < 500ms
└─ Cache hit rate > 85%

Reliability
├─ Error rate < 0.1%
├─ Database query p95 < 50ms
└─ Failed jobs < 1%
```

---

## Testing Strategy

### Test Pyramid

```
         /\
        /  \
       / E2E \                Integration & E2E (10%)
      /______\
      /        \
     /  API    \               API & Service (30%)
    / Tests    \
   /___________\
   /            \
  / Unit Tests  \              Unit Tests (60%)
 /______________\
```

### Test Coverage

- **Unit Tests:** Models, Schemas, Services (aim > 80%)
- **Integration Tests:** API endpoints with database (aim > 60%)
- **E2E Tests:** Critical user journeys (aim > 40%)

### Test Types

```bash
# Unit tests (fast, isolated)
pytest tests/unit/

# Integration tests (slower, with dependencies)
pytest tests/integration/

# Performance tests (load testing)
ab -n 10000 -c 100 http://localhost:8000/api/inventory

# Security tests
# - SQL injection (Burp Suite)
# - XSS (OWASP ZAP)
# - Authentication bypass (manual)
```

---

## Deployment & Release Strategy

### Deployment Phases

```
1. Development
   └─ Local machine
   └─ SQLite data
   └─ Hot reload enabled
   
2. Staging
   └─ Production-like environment
   └─ PostgreSQL data
   └─ Full test suite
   
3. Production
   └─ HA setup
   └─ Monitoring enabled
   └─ Backup configured
```

### Release Process

```
1. Code Review
   └─ Peer review
   └─ CI/CD pipeline passes
   
2. Testing
   └─ Unit tests
   └─ Integration tests
   └─ Staging deployment
   
3. Deployment
   └─ Blue-green or canary
   └─ Monitoring alerts
   └─ Rollback plan
   
4. Validation
   └─ Health checks
   └─ Critical path tests
   └─ User validation
```

---

## Future Enhancements

### Phase 2 (Months 4-6)
- [ ] Role-based access control (RBAC)
- [ ] Multi-pharmacy support
- [ ] Advanced reporting (PDF export)
- [ ] WhatsApp bot integration
- [ ] Barcode scanner support

### Phase 3 (Months 6-9)
- [ ] Mobile app (React Native)
- [ ] Advanced ML models (Prophet, LSTM)
- [ ] Real-time notifications (WebSocket)
- [ ] Customer loyalty program
- [ ] Supply chain integration

### Phase 4 (Months 9-12)
- [ ] Kubernetes deployment
- [ ] Global CDN
- [ ] Blockchain for compliance (optional)
- [ ] AI-powered chatbot
- [ ] Price optimization engine

---

## Conclusion

PharmaRec AI is architected for:
- **Scalability:** From 1 pharmacy to 10,000+ pharmacies
- **Reliability:** 99.9% uptime SLA
- **Maintainability:** Clean code, good documentation
- **Observability:** Comprehensive monitoring and logging
- **Security:** Production-grade security practices

The foundation is solid for a successful SaaS product launch and growth.

