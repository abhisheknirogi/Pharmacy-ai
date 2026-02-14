"""
SECURITY.md - Security Best Practices & Guidelines

This document outlines security considerations, best practices, 
and implementation guidelines for PharmaRec AI.
"""

# PharmaRec AI - Security Best Practices

## 🔒 Security Overview

This document covers security implementation across all layers:
- **Infrastructure Security** (Network, Firewall)
- **Application Security** (Input validation, Auth, Encryption)
- **Data Security** (Database, Backups, Encryption)
- **Operations Security** (Monitoring, Incident Response)

---

## 1. Authentication & Authorization

### Password Security

```python
# ✅ GOOD: Using bcrypt with cost factor of 12
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(password, rounds=12)  # Slow by design

# ✅ GOOD: Password requirements
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRES_SPECIAL = True
PASSWORD_REQUIRES_UPPERCASE = True
```

**Password Policy:**
- Minimum 12 characters
- Must include: uppercase, lowercase, number, special character
- Enforce password changes every 90 days (optional)
- No password reuse (last 5 passwords)

### JWT Token Security

```python
# ✅ GOOD: Short token lifetime
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

# ✅ GOOD: Secure token generation
import secrets
SECRET_KEY = secrets.token_urlsafe(32)  # Use in production

# ✅ GOOD: Token validation
from jose import JWTError, jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Token Practices:**
- Use HS256 or RS256 algorithm
- Never store tokens in localStorage (use httpOnly cookies if possible)
- Implement token refresh mechanism
- Validate token signature on every request
- Include token expiration check

### Session Management

```python
# ✅ GOOD: Session security headers
response.set_cookie(
    key="session_id",
    value=session_token,
    httponly=True,      # Prevent JavaScript access
    secure=True,        # HTTPS only
    samesite="strict",  # CSRF protection
    max_age=3600        # 1 hour expiry
)

# ✅ GOOD: Session timeout
SESSION_TIMEOUT_MINUTES = 60
INACTIVITY_TIMEOUT_MINUTES = 15
```

### Multi-Factor Authentication (Future)

```python
# TODO: Implement for sensitive operations
# - User registration (email verification)
# - Admin actions (3FA with email + SMS)
# - Payment processing (3FA)
```

---

## 2. Input Validation & Sanitization

### Pydantic Validation

```python
# ✅ GOOD: Strict input validation
from pydantic import BaseModel, Field, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(..., min_length=12, regex="^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).*$")
    full_name: str = Field(..., min_length=1, max_length=255)
    
    @validator('full_name')
    def validate_name(cls, v):
        # No special characters except space, dash, apostrophe
        if not all(c.isalpha() or c in " -'" for c in v):
            raise ValueError('Invalid characters in name')
        return v.strip()

# ✅ GOOD: SQLAlchemy ORM (prevents SQL injection)
# Using parameterized queries automatically
medicines = session.query(Medicine).filter(Medicine.name == user_input).all()
```

### File Upload Security

```python
# ✅ GOOD: Validate uploaded files
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file):
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("File too large")
    
    # Check file extension
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValidationError("Invalid file type")
    
    # Scan file for malware (optional, via VirusTotal API)
    
    return True
```

### XSS Prevention

```python
# ✅ GOOD: HTML escaping
from html import escape

@router.post("/comments")
def add_comment(text: str):
    safe_text = escape(text)  # Convert <, >, &, " to HTML entities
    db.save(safe_text)
```

---

## 3. Network Security

### HTTPS/TLS Configuration

```nginx
# ✅ GOOD: SSL/TLS configuration
server {
    listen 443 ssl http2;
    
    # Strong cipher suites only
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...';
    ssl_prefer_server_ciphers on;
    
    # Certificate configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # HSTS (force HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# ✅ GOOD: HTTP to HTTPS redirect
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### Security Headers

```nginx
# ✅ GOOD: Security headers in Nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Rate Limiting

```python
# ✅ GOOD: Rate limiting per IP
RATE_LIMIT = {
    "login": "5 requests per minute",
    "api": "100 requests per minute",
    "upload": "10 requests per minute"
}

# Implementation via middleware (see middleware.py)
```

### Firewall Rules

```bash
# ✅ GOOD: UFW Firewall configuration
sudo ufw enable
sudo ufw allow 22/tcp    # SSH (restricted to office IPs in production)
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw default deny incoming
sudo ufw default allow outgoing

# ✅ GOOD: Restrict SSH
echo "# Only allow SSH from office IP" >> /etc/ssh/sshd_config
echo "AllowUsers user@203.0.113.0" >> /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

## 4. Data Security

### Database Security

```python
# ✅ GOOD: Parameterized queries (via SQLAlchemy)
from sqlalchemy import text

# NEVER use string concatenation
# ❌ BAD: query = f"SELECT * FROM medicines WHERE id = {user_id}"

# ✅ GOOD: Parameterized
user = session.query(Medicine).filter(Medicine.id == user_id).first()

# ✅ GOOD: ORM prevents SQL injection
```

### Password Hashing in Database

```python
# ✅ GOOD: Bcrypt hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# When saving user
user.password_hash = pwd_context.hash(plain_password)

# When verifying
is_valid = pwd_context.verify(plain_password, user.password_hash)

# ❌ BAD: Storing plain text passwords
# ❌ BAD: Custom hashing algorithms
# ❌ BAD: MD5 or SHA1
```

### Encryption at Rest (Future)

```python
# TODO: Implement for sensitive data
# Option 1: Database-level encryption (PostgreSQL TDE)
# Option 2: Column-level encryption
# Option 3: Field-level encryption

from cryptography.fernet import Fernet

cipher = Fernet(encryption_key)
encrypted_ssn = cipher.encrypt(ssn.encode())
decrypted_ssn = cipher.decrypt(encrypted_ssn).decode()
```

### Backup Security

```bash
# ✅ GOOD: Encrypted backups
pg_dump pharmarec_prod | gzip | gpg --encrypt -r backup@pharmarec.ai > backup_$(date +%s).sql.gz.gpg

# ✅ GOOD: Backup encryption
encrypt_backup() {
    gpg --symmetric --cipher-algo AES256 backup.sql.gz
}

# ✅ GOOD: Off-site backup storage
aws s3 cp backup.sql.gz.gpg s3://pharmarec-backups/$(date +%s)/

# ✅ GOOD: Backup retention policy
find /backups -name "*.sql.gz" -mtime +30 -delete  # Delete after 30 days
```

---

## 5. API Security

### CORS Configuration

```python
# ✅ GOOD: Strict CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pharmarec.ai",
        "https://www.pharmarec.ai",
        "https://app.pharmarec.ai"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# ❌ BAD: allow_origins=["*"]  # Never use in production
```

### API Key Management

```python
# ✅ GOOD: API keys from environment variables
API_KEYS = {
    "email_service": os.getenv("EMAIL_API_KEY"),
    "aws_s3": os.getenv("AWS_SECRET_KEY"),
}

# ✅ GOOD: API key validation
@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key not in os.getenv("VALID_API_KEYS", "").split(","):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return await call_next(request)
```

### Request Logging (without sensitive data)

```python
# ✅ GOOD: Log requests safely
def log_request(request: Request):
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "ip": request.client.host,
        "timestamp": datetime.utcnow(),
        # ❌ Never log: "body", "password", "token", etc.
    }
    logger.info(json.dumps(log_data))

# ✅ GOOD: Redact sensitive fields
REDACTED_FIELDS = {"password", "token", "api_key", "secret"}

def sanitize_log(data: dict) -> dict:
    return {k: "***REDACTED***" if k in REDACTED_FIELDS else v 
            for k, v in data.items()}
```

---

## 6. Secrets Management

### Environment Variables (Current Approach)

```bash
# ✅ GOOD: .env file (never commit)
DATABASE_PASSWORD=super_secure_password_123!@#
SECRET_KEY=generated_with_secrets.token_urlsafe_32
AWS_SECRET_KEY=xxxxx

# ✅ GOOD: File permissions
chmod 600 .env

# ✅ GOOD: .gitignore
echo ".env*" >> .gitignore
```

### Production Secrets Management (Recommended)

```python
# Option 1: AWS Secrets Manager
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Option 2: HashiCorp Vault
import hvac

client = hvac.Client(url='https://vault.example.com:8200')
secret = client.secrets.kv.read_secret_version(path='pharmarec/db')

# Option 3: GitHub Actions Secrets (for CD/CD)
# Use ${{ secrets.DATABASE_PASSWORD }} in workflows
```

---

## 7. Logging & Monitoring

### Secure Logging

```python
# ✅ GOOD: Structured logging
import json
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

logger.info({
    "event": "user_login",
    "user_id": user.id,
    "ip": request.client.host,
    "timestamp": datetime.utcnow()
})

# ❌ BAD: Logging passwords, tokens, or user data
```

### Audit Logging (Future)

```python
# TODO: Implement for compliance
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # CREATE, UPDATE, DELETE
    entity_type = Column(String)  # Medicine, Sale, User
    entity_id = Column(Integer)
    before_state = Column(JSON)  # Previous values
    after_state = Column(JSON)   # New values
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
```

### Security Monitoring

```python
# ✅ GOOD: Monitor security events
SECURITY_EVENTS = {
    "failed_login": Alert.MEDIUM,
    "invalid_token": Alert.HIGH,
    "sql_injection_attempt": Alert.CRITICAL,
    "rate_limit_exceeded": Alert.LOW,
    "unusual_activity": Alert.HIGH,
}

def trigger_security_alert(event_type: str, details: dict):
    alert = SECURITY_EVENTS.get(event_type)
    logger.warning(f"SECURITY ALERT [{alert}]: {event_type}", extra=details)
    # Send to monitoring system
```

---

## 8. Dependency Security

### Vulnerability Scanning

```bash
# ✅ GOOD: Check Python dependencies
pip install safety
safety check

# ✅ GOOD: Check Node dependencies
npm audit

# ✅ GOOD: Docker image scanning
docker scout cves pharmarec-backend:latest

# ✅ GOOD: Software Composition Analysis (SCA)
# Use tools like: Snyk, GitHub Dependabot, WhiteSource
```

### Dependency Updates

```bash
# Update strategy:
# 1. Weekly: Check for security updates
# 2. Monthly: Update non-major versions
# 3. Quarterly: Evaluate major version updates
# 4. Always: Update critical security patches immediately

# Check for outdated packages
pip list --outdated
npm outdated

# Update with testing
pip install --upgrade <package>
pytest tests/  # Run full test suite
```

---

## 9. Incident Response

### Incident Response Plan

```
1. DETECTION
   └─ Automated alerts from monitoring
   └─ User reports
   └─ Security scanning tools

2. CONTAINMENT
   └─ Isolate affected systems
   └─ Revoke compromised credentials
   └─ Block malicious IP addresses
   └─ Disable affected accounts

3. INVESTIGATION
   └─ Review logs
   └─ Determine scope
   └─ Root cause analysis
   └─ Identify affected users

4. REMEDIATION
   └─ Patch vulnerabilities
   └─ Update security policies
   └─ Deploy fixes
   └─ Verify fix effectiveness

5. COMMUNICATION
   └─ Notify affected users (if data breach)
   └─ Update status page
   └─ Post-incident review
   └─ Document lessons learned
```

### Common Incidents

**Scenario 1: Database Breach**
- Immediately revoke all sessions
- Force password resets
- Audit database access logs
- Notify users of compromised data
- Monitor for identity theft

**Scenario 2: DDoS Attack**
- Enable DDoS protection (Cloudflare, AWS Shield)
- Rate limit aggressively
- Cache responses
- Failover to backup infrastructure
- Coordinate with ISP if needed

**Scenario 3: Malware**
- Scan all servers with antivirus
- Verify integrity of core files (checksums)
- Review process execution logs
- Identify lateral movement
- Re-image compromised systems

---

## 10. Compliance & Standards

### Data Protection Regulations

**GDPR (General Data Protection Regulation)**
```
- Data subject rights (access, deletion, portability)
- Privacy by design
- Data processing agreements
- Breach notification (72 hours)
- DPIA (Data Protection Impact Assessment)
```

**HIPAA (Health Insurance Portability & Accountability Act)**
```
- Protected Health Information (PHI) protection
- Business Associate Agreements (BAA)
- Audit controls and encryption
- Incident response procedures
```

### Security Standards

- **ISO 27001:** Information Security Management System
- **PCI DSS:** Payment Card Industry (if processing payments)
- **SOC 2:** Service Organization Control
- **OWASP Top 10:** Web application security

---

## Security Checklist

- [ ] All passwords hashed with bcrypt (cost 12+)
- [ ] JWT tokens with <1 hour expiration
- [ ] HTTPS/TLS 1.2+ only
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] CSRF protection (SameSite cookies)
- [ ] CORS restricted to known origins
- [ ] API keys from environment variables
- [ ] Secrets not logged or exposed
- [ ] Database backups encrypted
- [ ] Firewall rules configured
- [ ] SSH key-based access only
- [ ] Vulnerability scanning running
- [ ] Audit logging implemented
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Pentesting scheduled quarterly
- [ ] Compliance requirements documented

---

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## Contact for Security Issues

⚠️ **Report security vulnerabilities responsibly:**
- Email: security@pharmarec.ai
- Do NOT open public GitHub issues for security vulnerabilities
- Allow 48 hours for response
- Disclose responsibly (90-day disclosure window)

