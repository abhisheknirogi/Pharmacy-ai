# 🚀 PharmaRec AI - Production Deployment Guide

**Status:** Enterprise-Ready | **Version:** 1.0.0

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Local Development Setup](#local-development-setup)
4. [Production Environment Setup](#production-environment-setup)
5. [Docker Deployment](#docker-deployment)
6. [Database Migrations](#database-migrations)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Observability](#monitoring--observability)
9. [Scaling & Performance](#scaling--performance)
10. [Disaster Recovery](#disaster-recovery)
11. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────────────────────────┐
│   Client Applications               │
│   (Web, Mobile, Desktop Agent)      │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│   Nginx Reverse Proxy                │
│   (SSL/TLS, Rate Limiting, Caching) │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌─────────────────┐   ┌──────────────┐
│ FastAPI Backend │   │ Next.js      │
│ (Port 8000)     │   │ Frontend     │
└────────┬────────┘   │ (Port 3000)  │
         │            └──────────────┘
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
┌──────────────────┐   ┌───────────────┐
│ PostgreSQL DB    │   │ Redis Cache   │
│ (Primary DB)     │   │ (Sessions,    │
└──────────────────┘   │  Queue)       │
                       └───────────────┘

┌─────────────────────────────────────┐
│ Monitoring & Logging Stack          │
│ ┌──────────────────────────────────┐│
│ │ Prometheus → Grafana (Metrics)   ││
│ │ ElasticSearch → Kibana (Logs)    ││
│ │ Sentry (Error Tracking)          ││
│ └──────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Version | Environment |
|-----------|-----------|---------|-------------|
| **Backend** | FastAPI | 0.104.1 | Python 3.11 |
| **Frontend** | Next.js | 14.0 | Node 18+ |
| **Database** | PostgreSQL | 15 | Production |
| **Cache** | Redis | 7 | Production |
| **Proxy** | Nginx | Alpine | Production |
| **Monitoring** | Prometheus/Grafana | Latest | Production |
| **Logging** | ELK Stack | 8.10 | Production |
| **Containerization** | Docker & Compose | Latest | All |

---

## ✅ Pre-Deployment Checklist

### Security
- [ ] SSL/TLS certificates generated and validated
- [ ] SECRET_KEY changed from default
- [ ] Database password strong and unique (min 16 chars)
- [ ] Redis password configured
- [ ] All environment variables reviewed and set
- [ ] API keys for external services (email, AWS, etc.) configured
- [ ] Firewall rules configured for ports 80, 443 only
- [ ] VPN/SSH key-based access configured

### Infrastructure
- [ ] Server specs verified (min: 4GB RAM, 2 CPU, 50GB disk)
- [ ] Docker and Docker Compose installed
- [ ] Database backups scheduled
- [ ] Log rotation configured
- [ ] Monitoring alerts configured
- [ ] Load balancer configured (if multi-instance)
- [ ] CDN configured for static assets (optional)

### Application
- [ ] All tests passing (`make test`)
- [ ] Code review completed
- [ ] Dependencies up-to-date and checked for vulnerabilities
- [ ] Database migrations tested
- [ ] Configuration validated
- [ ] API documentation generated
- [ ] Deployment scripts tested

### Monitoring
- [ ] Prometheus targets configured
- [ ] Grafana dashboards created
- [ ] Alert rules defined
- [ ] Log aggregation tested
- [ ] Error tracking (Sentry) configured
- [ ] Health checks verified

---

## 🔧 Local Development Setup

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/your-org/pharmarec-ai.git
cd pharmarec-ai

# 2. Create environment
cp .env.example .env

# 3. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. Initialize database
python scripts/seed_db.py

# 5. Run development servers (2 terminals)
# Terminal 1:
make run

# Terminal 2:
cd frontend && npm run dev
```

### Development Tools

```bash
# Run tests
make test

# Format code
make format

# Lint code
make lint

# Type checking
mypy backend --ignore-missing-imports

# Run specific test
pytest tests/test_backend.py::test_register_user -v
```

---

## 🏢 Production Environment Setup

### 1. Server Preparation

```bash
# SSH into production server
ssh -i your-key.pem ubuntu@your-domain.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y \
  docker.io \
  docker-compose \
  curl \
  wget \
  git \
  htop \
  fail2ban \
  certbot \
  python3-certbot-nginx

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installations
docker --version
docker-compose --version
```

### 2. Clone and Setup Repository

```bash
# Navigate to app directory
cd /app

# Clone repository
git clone https://github.com/your-org/pharmarec-ai.git
cd pharmarec-ai

# Create production environment
cp .env.production .env

# Edit configuration
nano .env  # Update all production values
```

### 3. Generate SSL Certificates

```bash
# Generate self-signed (development) or use Let's Encrypt (production)
mkdir -p infra/nginx/ssl

# Option A: Let's Encrypt (automatic)
sudo certbot certonly --standalone -d pharmarec.ai -d www.pharmarec.ai
sudo cp /etc/letsencrypt/live/pharmarec.ai/fullchain.pem infra/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/pharmarec.ai/privkey.pem infra/nginx/ssl/key.pem
sudo chmod 644 infra/nginx/ssl/*

# Option B: Self-signed (testing)
openssl req -x509 -newkey rsa:4096 -keyout infra/nginx/ssl/key.pem -out infra/nginx/ssl/cert.pem -days 365 -nodes
```

### 4. Configure Firewall

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verify rules
sudo ufw status
```

---

## 🐳 Docker Deployment

### Production Deploy

```bash
# 1. Build images
docker-compose -f docker-compose.prod.yml build

# 2. Start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Verify services
docker-compose -f docker-compose.prod.yml ps

# 4. Check logs
docker-compose -f docker-compose.prod.yml logs -f backend

# 5. Test endpoints
curl https://pharmarec.ai/health
curl https://api.pharmarec.ai/health
```

### Service Management

```bash
# Stop services
docker-compose -f docker-compose.prod.yml stop

# Restart services
docker-compose -f docker-compose.prod.yml restart backend

# Remove containers (WARNING)
docker-compose -f docker-compose.prod.yml down

# View logs for specific service
docker-compose -f docker-compose.prod.yml logs postgres -f

# Execute command in container
docker-compose -f docker-compose.prod.yml exec backend bash
```

### Container Monitoring

```bash
# Real-time resource usage
docker stats

# Container processes
docker top pharmarec-backend-prod

# Container logs with timestamps
docker-compose -f docker-compose.prod.yml logs --timestamps backend
```

---

## 🗄️ Database Migrations

### Initial Setup

```bash
# Create migration scripts directory
alembic init alembic

# Generate initial migration (on development box first)
alembic revision --autogenerate -m "Initial schema"

# Create migration file with your changes
alembic revision -m "Add new_column to medicines"
# Edit alembic/versions/xxxx_add_new_column.py

# Test migration locally
alembic upgrade head

# Downgrade for testing
alembic downgrade -1
```

### Production Migration

```bash
# SSH into production
ssh ubuntu@your-domain.com
cd /app/pharmarec-ai

# Create backup before migration
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U pharmarec pharmarec_prod > backup_$(date +%s).sql

# Run migration
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Verify schema
docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod -c "\dt"

# Rollback if needed
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

---

## 🔐 Security Hardening

### Environment Security

```bash
# Ensure .env is not committed
echo ".env" >> .gitignore
echo ".env.production" >> .gitignore

# Restrict file permissions
chmod 600 .env
chmod 600 .env.production

# Use secrets management for credentials
# Option 1: AWS Secrets Manager
# Option 2: HashiCorp Vault
# Option 3: GitHub Secrets (for CD/CD)
```

### Application Security

```bash
# Security headers (configured in nginx.prod.conf)
# - Strict-Transport-Security
# - X-Content-Type-Options
# - X-Frame-Options
# - Content-Security-Policy
# - Referrer-Policy

# SQL Injection protection: Using SQLAlchemy ORM (parameterized queries)

# CSRF protection: JWT tokens instead of cookies

# Rate limiting: 100 requests/minute per IP

# Input validation: Pydantic schemas with validation
```

### Infrastructure Security

```bash
# Fail2Ban configuration
sudo nano /etc/fail2ban/jail.conf

# Example: Protect SSH
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 5

# Enable Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

Metrics available at `http://localhost:9090`

**Key Metrics:**
- `pharmarec_requests_total` - Total requests by endpoint
- `pharmarec_request_duration_seconds` - Request latency
- `pharmarec_database_connections` - Active DB connections
- `pharmarec_cache_hits_total` - Cache hit rate
- `pharmarec_errors_total` - Error rate by type

### Grafana Dashboards

Access at `https://pharmarec.ai:3000` (prod) or `http://localhost:3001` (dev)

**Default Dashboards:**
1. **System Health** - CPU, memory, disk, network
2. **Application Performance** - Request rate, latency, errors
3. **Database Performance** - Connections, queries, cache
4. **API Usage** - Endpoints, responses, status codes
5. **Business Metrics** - Sales, inventory, reorders

### Log Aggregation (ELK Stack)

Access Kibana at `https://pharmarec.ai:5601`

**Useful Queries:**
```
# Errors in last hour
severity: ERROR AND @timestamp: [now-1h TO now]

# API latency > 1 second
response_time_ms > 1000

# Authentication failures
level: WARNING AND "AUTHENTICATION_ERROR"

# Specific service
service: "pharmarec-backend"
```

### Alerting

**Alert Configuration** (`infra/prometheus/alerts.yml`)

Examples:
- High error rate (> 1%)
- API latency > 2 seconds (95th percentile)
- Database connection pool exhausted
- Low disk space (< 10%)
- Service unavailable

---

## 📈 Scaling & Performance

### Horizontal Scaling

```bash
# Multiple backend instances
# Update docker-compose.prod.yml:

services:
  backend:
    replicas: 3  # Scale to 3 instances
```

### Load Balancing

```bash
# Nginx upstream configuration
upstream backend {
    least_conn;  # Least connections strategy
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}
```

### Caching Strategy

**Redis Cache Levels:**
1. Session storage (JWT, user data)
2. Database query results (medicine list, sales summary)
3. Computed data (reorder suggestions)
4. Static assets (via Nginx)

### Database Optimization

```bash
# Index critical columns
CREATE INDEX idx_medicine_expiry ON medicines(expiry_date);
CREATE INDEX idx_sale_date ON sales(sale_date);
CREATE INDEX idx_medicine_stock ON medicines(stock_qty);

# Analyze query plans
EXPLAIN ANALYZE SELECT * FROM sales WHERE sale_date > NOW() - INTERVAL 30;

# Vacuum and analyze
VACUUM ANALYZE;
```

### Connection Pooling

```python
# SQLAlchemy pool configuration
pool_size = 20  # Max connections
max_overflow = 10  # Additional connections
pool_recycle = 3600  # Recycle connections hourly
pool_pre_ping = True  # Verify connections before use
```

---

## 🔄 Disaster Recovery

### Backup Strategy

```bash
# Daily automated backups
# Cron job runs: 0 2 * * * /app/pharmarec-ai/scripts/backup.sh

# Backup script example:
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U pharmarec pharmarec_prod > $BACKUP_DIR/pharmarec_$TIMESTAMP.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "pharmarec_*.sql.gz" -mtime +30 -delete
```

### Backup Verification

```bash
# Test restore process monthly
psql -U pharmarec pharmarec_test < /backups/latest_backup.sql

# Verify data integrity
SELECT COUNT(*) FROM medicines;
SELECT COUNT(*) FROM sales;
```

### Disaster Recovery Runbook

1. **Database Failure:**
   ```bash
   # Restore from latest backup
   docker-compose -f docker-compose.prod.yml down postgres
   docker-compose -f docker-compose.prod.yml up postgres
   psql -U pharmarec pharmarec_prod < /backups/latest_backup.sql
   ```

2. **Complete System Failure:**
   ```bash
   # Re-provision server
   # Re-clone code
   # Restore database
   # Restore configuration (.env files)
   # Rebuild and restart
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Data Corruption:**
   ```bash
   # Restore point-in-time backup
   # Verify data integrity
   # Validate business logic
   # Update monitoring to detect similar issues
   ```

---

## 🐛 Troubleshooting

### Common Issues

#### Backend Not Starting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common causes:
# 1. Database not ready
#    Solution: Wait for postgres health check
docker-compose -f docker-compose.prod.yml up postgres
docker-compose -f docker-compose.prod.yml up backend

# 2. Configuration missing
#    Solution: Check .env file
env | grep -E "^[A-Z_]+="

# 3. Port already in use
#    Solution: Check existing services
sudo lsof -i :8000
```

#### Database Connection Issues

```bash
# Test database connectivity
docker-compose -f docker-compose.prod.yml exec backend python -c "from backend.app.database import engine; engine.connect()"

# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Restart database
docker-compose -f docker-compose.prod.yml restart postgres
```

#### High Memory Usage

```bash
# Profile memory
docker exec pharmarec-backend-prod python -m memory_profiler backend/app/main.py

# Check for memory leaks
docker stats pharmarec-backend-prod

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

#### SSL Certificate Issues

```bash
# Check certificate expiration
openssl x509 -in infra/nginx/ssl/cert.pem -text -noout | grep "Not"

# Renew certificate
sudo certbot renew

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## 📞 Support & Resources

- **Documentation:** https://pharmarec.ai/docs
- **API Reference:** https://api.pharmarec.ai/docs
- **Status Page:** https://status.pharmarec.ai
- **Email:** support@pharmarec.ai
- **Slack:** #pharmarec-support

---

## 📊 Performance Benchmarks

**Target Metrics:**
- API Response Time: < 200ms (p95)
- Database Query Time: < 50ms (p95)
- Page Load Time: < 2s (First Contentful Paint)
- Uptime: 99.9% (4:23 min/month max downtime)
- Cache Hit Rate: > 85%
- Error Rate: < 0.1%

**Load Testing (Apache ab):**
```bash
# Test 1000 requests with 10 concurrent
ab -n 1000 -c 10 https://api.pharmarec.ai/health

# Analyze results:
# Requests per second: desired > 500
# Failed requests: desired 0
# Response time: desired < 100ms
```

---

## ✨ Next Steps

1. ✅ Complete pre-deployment checklist
2. ✅ Run through deployment guide
3. ✅ Verify all services running
4. ✅ Test critical user flows
5. ✅ Enable monitoring and alerts
6. ✅ Schedule backup verification
7. ✅ Document deployment runbook

🚀 **System is now production-ready!**

