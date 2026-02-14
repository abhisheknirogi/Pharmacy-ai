"""
QUICK_START.md - Developer Quick Start Guide

Get up and running in 5 minutes.
"""

# PharmaRec AI - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Clone & Navigate
```bash
git clone https://github.com/your-org/pharmarec-ai.git
cd pharmarec-ai
```

### 2. Create Environment
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### 4. Start Development Servers (2 terminals)
```bash
# Terminal 1: Backend
make run

# Terminal 2: Frontend  
cd frontend && npm run dev
```

### 5. Access Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Test Login:** demo@pharmacy.com / demo123456

---

## 🔑 Essential Commands

```bash
# Setup
make setup              # Install all dependencies

# Development
make run               # Start backend
make dev               # Start both backend & frontend
make test              # Run all tests
make format            # Format code with black
make lint              # Lint with flake8

# Database
make db-init           # Initialize database
make db-reset          # Clear database
make db-seed           # Populate with test data

# Docker
make docker-build      # Build Docker images
make docker-up         # Start Docker services
make docker-down       # Stop Docker services

# Utilities
make clean             # Remove cache files
make help              # Show all commands
```

---

## 📁 Project Structure Quick Reference

```
backend/               # FastAPI application
├── app/
│   ├── main.py       # FastAPI app entry point
│   ├── database.py   # Database setup
│   ├── models/       # SQLAlchemy ORM models
│   ├── schemas/      # Pydantic validation
│   ├── api/routes/   # API endpoints
│   └── services/     # Business logic

frontend/              # Next.js React app
├── src/
│   ├── app/          # Pages (routing)
│   ├── components/   # React components
│   ├── lib/          # Utils & API client
│   └── types/        # TypeScript types

ml-engine/             # ML models & prediction
└── inference/

tests/                 # Test suite
```

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend --cov-report=html

# Specific test
pytest tests/test_backend.py::test_register_user -v

# Watch mode (requires pytest-watch)
ptw tests/
```

---

## 🔐 Authentication

### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@pharmacy.com",
    "password": "SecurePassword123!",
    "full_name": "John Pharmacist"
  }'
```

### Login & Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@pharmacy.com",
    "password": "SecurePassword123!"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer"
# }
```

### Use Token in Requests
```bash
curl http://localhost:8000/api/inventory \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 📊 Common API Endpoints

### Inventory
```bash
# List medicines
curl http://localhost:8000/api/inventory?page=1&page_size=20

# Search medicines
curl "http://localhost:8000/api/inventory/search?q=paracetamol"

# Add medicine
curl -X POST http://localhost:8000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paracetamol 500mg",
    "batch_no": "B12345",
    "stock_qty": 100,
    "reorder_level": 20,
    "price": 5.00
  }'
```

### Sales
```bash
# Record sale
curl -X POST http://localhost:8000/api/sales \
  -d '{
    "medicine_id": 1,
    "quantity": 2,
    "unit_price": 5.00
  }'

# Get sales summary
curl http://localhost:8000/api/sales/summary
```

### AI Reorder Suggestions
```bash
curl http://localhost:8000/api/reorder/suggestions?days=7
```

---

## 🐛 Debugging

### View Backend Logs
```bash
# Real-time logs
tail -f logs/pharmarec.log

# Last 50 lines
tail -50 logs/pharmarec.log

# Search for errors
grep ERROR logs/pharmarec.log
```

### Database Debugging
```bash
# Connect to SQLite database
sqlite3 pharmacy.db

# View tables
.tables

# View schema
.schema medicines

# Query data
SELECT * FROM medicines LIMIT 10;
```

### Frontend Console
```bash
# Open browser DevTools: F12 or Right-click → Inspect
# Check Console for JavaScript errors
# Check Network tab for API calls
```

---

## 🚀 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/inventory-search
```

### 2. Make Changes
```bash
# Edit code in your editor
# Tests run automatically on save (if configured)
```

### 3. Run Tests
```bash
pytest tests/ -v
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add inventory search by batch number"
```

### 5. Push & Create Pull Request
```bash
git push origin feature/inventory-search
# Create PR on GitHub
```

---

## 📝 Code Style

### Python (FastAPI Backend)
```python
# ✅ Good
def get_medicine_by_id(medicine_id: int) -> Optional[Medicine]:
    """Get medicine by ID."""
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()

# ❌ Bad
def get_med(id):
    return db.query(Medicine).filter(Medicine.id==id).first()
```

### TypeScript (Next.js Frontend)
```typescript
// ✅ Good
interface Medicine {
  id: number;
  name: string;
  quantity: number;
}

const getMedicines = async (): Promise<Medicine[]> => {
  const response = await apiClient.get('/inventory');
  return response.data;
};

// ❌ Bad
const getMedicines = async () => {
  return await fetch('/api/inventory');
};
```

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Lock
```bash
# Reset database
make db-reset

# Or manually
rm pharmacy.db
python -c "from backend.app.database import init_db; init_db()"
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or for Node:
rm -rf frontend/node_modules
cd frontend && npm install && cd ..
```

### Frontend Build Error
```bash
# Clear Next.js cache
rm -rf frontend/.next

# Rebuild
cd frontend && npm run build && cd ..
```

---

## 📚 Useful Documentation Files

| Document | Purpose |
|----------|---------|
| README.md | Project overview & features |
| ARCHITECTURE.md | System design & patterns |
| PRODUCTION_DEPLOYMENT.md | Production deployment guide |
| SECURITY.md | Security best practices |
| OPERATIONS_RUNBOOK.md | Daily operations |

---

## 🔗 Useful Links

- **API Documentation:** http://localhost:8000/docs
- **GitHub Repo:** https://github.com/your-org/pharmarec-ai
- **Issue Tracker:** https://github.com/your-org/pharmarec-ai/issues
- **Documentation:** See docs/ folder

---

## ⚠️ Common Gotchas

1. **Forgot to activate virtual environment?**
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Frontend not connecting to backend?**
   - Check NEXT_PUBLIC_API_URL in .env
   - Verify backend is running on 8000
   - Check browser console for CORS errors

3. **Test data not showing?**
   ```bash
   python scripts/seed_db.py
   ```

4. **Can't login with test credentials?**
   - Run: `python scripts/seed_db.py`
   - Use: demo@pharmacy.com / demo123456

---

## 🎓 Learning Path

1. **Day 1:** Read README.md and explore code structure
2. **Day 2:** Run and modify a few API endpoints
3. **Day 3:** Add a new feature (e.g., new field to medicine)
4. **Day 4:** Write tests for your feature
5. **Day 5:** Review ARCHITECTURE.md for design patterns

---

## 💡 Pro Tips

- Use API docs at `/docs` to explore endpoints interactively
- Frontend in /docs has TypeScript interfaces - follow them!
- All database queries use ORM (no raw SQL)
- All inputs validated with Pydantic - trust the schemas
- Errors have codes for easy debugging (see exceptions.py)

---

## 📞 Need Help?

1. Check the documentation files
2. Search existing GitHub issues
3. Ask in Slack #engineering channel
4. Create a new issue with `[HELP]` prefix

---

**Happy coding! 🚀**

