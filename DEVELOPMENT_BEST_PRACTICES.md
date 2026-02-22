# Development Best Practices Guide

This guide maintains the god-tier code quality standards for PharmaRec AI.

## Backend Best Practices

### API Endpoints
```python
# ✅ DO: Comprehensive validation and error handling
@router.post("/medicine", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(
    medicine: MedicineCreate = Body(..., description="Medicine data"),
    db: Session = Depends(get_db)
) -> MedicineResponse:
    """
    Create a new medicine with proper validation.
    
    - Validates input using Pydantic
    - Checks for duplicates
    - Logs operation
    - Returns proper status code
    """
    try:
        # Validation and business logic
        db_medicine = Medicine(**medicine.dict())
        db.add(db_medicine)
        db.commit()
        db.refresh(db_medicine)
        logger.info(f"Created medicine: {db_medicine.name}")
        return db_medicine
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating medicine: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create medicine")

# ❌ DON'T: Weak validation and error handling
@router.post("/medicine")
def create_medicine(medicine: dict, db: Session):
    db.add(medicine)
    db.commit()
    return medicine
```

### Models & Schemas
```python
# ✅ DO: Full validation with constraints
class MedicineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    stock_qty: int = Field(..., ge=0)
    
    @field_validator("price")
    def validate_price(cls, v):
        if v > 999999.99:
            raise ValueError("Price too high")
        return round(v, 2)

# ❌ DON'T: No validation
class MedicineCreate(BaseModel):
    name: str
    price: float
    stock_qty: int
```

### Error Handling
```python
# ✅ DO: Structured error responses
if not medicine:
    logger.warning(f"Medicine not found: ID {medicine_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Medicine with ID {medicine_id} not found"
    )

# ❌ DON'T: Generic errors
if not medicine:
    raise Exception("Not found")
```

### Database Operations
```python
# ✅ DO: Proper transaction management
try:
    db_medicine = Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
except Exception as e:
    db.rollback()
    logger.error(f"Error: {str(e)}")
    raise

# ❌ DON'T: No error handling
db.add(medicine)
db.commit()
```

---

## Frontend Best Practices

### Type-Safe Components
```tsx
// ✅ DO: Full TypeScript support with interfaces
interface MedicineFormProps {
  onSubmit: (data: MedicineCreateRequest) => Promise<void>;
  isLoading?: boolean;
}

const MedicineForm: React.FC<MedicineFormProps> = ({ onSubmit, isLoading = false }) => {
  const [formData, setFormData] = useState<MedicineCreateRequest>({...});
  const [errors, setErrors] = useState<ValidationResult>({...});
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validation = validateMedicineForm(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }
    await onSubmit(formData);
  };
  
  return <form onSubmit={handleSubmit}>{...}</form>;
};

// ❌ DON'T: Any types and weak typing
const MedicineForm = ({ onSubmit, isLoading }: any) => {
  const [formData, setFormData] = useState({});
  const handleSubmit = (e) => onSubmit(formData);
  return <form onSubmit={handleSubmit}>{...}</form>;
};
```

### API Error Handling
```tsx
// ✅ DO: Proper error handling with user-friendly messages
try {
  const response = await apiClient.getMedicines();
  setMedicines(response.data);
} catch (error) {
  const apiError = parseApiError(error);
  const userMessage = getUserErrorMessage(apiError);
  setError(userMessage);
  logError('getMedicines', apiError);
}

// ❌ DON'T: Silent failures
const response = await apiClient.getMedicines();
setMedicines(response.data);
```

### Form Validation
```tsx
// ✅ DO: Comprehensive validation before submission
const handleSubmit = (data: FormData) => {
  const validation = validateMedicineForm(data);
  if (!validation.isValid) {
    setErrors(validation.errors);
    return;
  }
  // Submit
};

// ❌ DON'T: Submit without validation
const handleSubmit = (data: FormData) => {
  apiClient.createMedicine(data);
};
```

### Loading States
```tsx
// ✅ DO: Show loading states for better UX
{isLoading ? (
  <div className="space-y-3">
    <div className="h-10 bg-gray-200 rounded animate-pulse" />
    <div className="h-10 bg-gray-200 rounded animate-pulse" />
  </div>
) : (
  /* Content */
)}

// ❌ DON'T: No loading state
{/* Content always showing */}
```

---

## Code Standards

### Naming Conventions
```
Backend:
- Functions: snake_case (get_medicines, create_medicine)
- Classes: PascalCase (Medicine, MedicineSchema)
- Constants: UPPER_SNAKE_CASE (API_BASE_URL)
- Variables: snake_case (medicine_id, total_price)

Frontend:
- Components: PascalCase (MedicineList, MedicineForm)
- Hooks: camelCase (useMedicines, useAuth)
- Utils: camelCase (validateEmail, parseError)
- Constants: UPPER_SNAKE_CASE (API_BASE_URL)
- Variables: camelCase (medicineId, totalPrice)
```

### Comment Standards
```python
# ✅ DO: Meaningful comments
def get_expiring_medicines(days: int = 30) -> List[Medicine]:
    """
    Get medicines expiring within specified days.
    
    Args:
        days: Number of days to look ahead
        
    Returns:
        List of expiring medicines sorted by expiry date
    """
```

### Import Organization
```python
# ✅ DO: Organized imports
# StandardLibrary
from typing import Optional, List
from datetime import datetime

# Third-party
from fastapi import APIRouter
from sqlalchemy.orm import Session

# Local
from ..models.medicine import Medicine
from ..schemas.medicine import MedicineResponse
```

---

## Testing Standards

### Backend Tests
```python
def test_create_medicine_with_valid_data():
    """Test medicine creation with valid input."""
    data = {
        "name": "Aspirin",
        "batch_no": "BATCH001",
        "price": 9.99,
        "stock_qty": 100
    }
    response = client.post("/medicine", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Aspirin"

def test_create_medicine_with_invalid_price():
    """Test medicine creation rejects negative price."""
    data = {
        "name": "Aspirin",
        "batch_no": "BATCH001",
        "price": -9.99,
        "stock_qty": 100
    }
    response = client.post("/medicine", json=data)
    assert response.status_code == 422
```

### Frontend Tests
```typescript
describe("MedicineForm", () => {
  it("should show validation errors for invalid input", () => {
    const { getByText } = render(<MedicineForm onSubmit={jest.fn()} />);
    
    fireEvent.click(getByText("Submit"));
    
    expect(getByText("Name is required")).toBeInTheDocument();
  });

  it("should call onSubmit with valid data", async () => {
    const mockSubmit = jest.fn();
    const { getByLabelText, getByText } = render(
      <MedicineForm onSubmit={mockSubmit} />
    );
    
    fireEvent.change(getByLabelText("Name"), { target: { value: "Aspirin" } });
    fireEvent.click(getByText("Submit"));
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalled();
    });
  });
});
```

---

## Security Checklist

- [ ] All inputs validated before use
- [ ] SQL injection prevented with parameterized queries
- [ ] XSS prevention with input sanitization
- [ ] CSRF tokens on state-changing operations
- [ ] Authentication on protected endpoints
- [ ] Authorization checks on resources
- [ ] Sensitive data not logged
- [ ] Secrets in environment variables
- [ ] HTTPS in production
- [ ] Rate limiting enabled

---

## Performance Checklist

- [ ] Database queries optimized with indexes
- [ ] Pagination implemented for large lists
- [ ] Caching strategy for frequently accessed data
- [ ] API responses compressed with gzip
- [ ] Frontend lazy loading implemented
- [ ] Code splitting for large bundles
- [ ] Image optimization
- [ ] Database connection pooling

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Health checks passing
- [ ] Backups configured
- [ ] Monitoring alerts set up
- [ ] Logs aggregation configured
- [ ] Error tracking enabled

---

## Maintenance Standards

### Code Review Process
1. Ensure all functions have type hints
2. Verify error handling is comprehensive
3. Check input validation
4. Verify logging statements
5. Ensure documentation is clear
6. Test both happy path and error cases
7. Check for security issues
8. Verify performance implications

### Release Process
1. Run full test suite
2. Update version numbers
3. Update CHANGELOG
4. Create release notes
5. Tag git commit
6. Deploy to staging
7. Run smoke tests
8. Deploy to production

---

## Monitoring & Observability

### Logging Strategy
- Errors: Always log with full context
- Warnings: Log potentially problematic situations
- Info: Log important business events
- Debug: Log detailed information for troubleshooting

### Metrics to Track
- API response times
- Error rates
- Database query performance
- Cache hit rates
- User engagement
- System resource usage

---

## Quick Reference

### When Adding a New Feature
1. Create types/interfaces
2. Add input validation
3. Add error handling
4. Add logging
5. Add tests
6. Add documentation
7. Code review

### When Fixing a Bug
1. Write failing test
2. Fix the bug
3. Verify test passes
4. Check for similar issues
5. Update documentation if needed

---

This guide ensures all team members maintain the god-tier code quality standards.
