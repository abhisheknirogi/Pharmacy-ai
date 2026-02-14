"""
OPERATIONS_RUNBOOK.md - Daily Operations Guide

Quick reference for common operational tasks and troubleshooting.
"""

# PharmaRec AI - Operations Runbook

## 🚀 Quick Reference

### Status & Health Checks

```bash
# Check all services running
docker-compose -f docker-compose.prod.yml ps

# Quick health check
curl https://pharmarec.ai/health

# Detailed diagnostics
curl https://api.pharmarec.ai/diagnostics

# Database connection status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U pharmarec
```

### Service Management

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Stop services gracefully
docker-compose -f docker-compose.prod.yml stop

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# View logs in real-time
docker-compose -f docker-compose.prod.yml logs -f backend

# Follow all logs
docker-compose -f docker-compose.prod.yml logs -f

# View last 100 lines of specific service
docker-compose -f docker-compose.prod.yml logs --tail 100 postgres
```

---

## 📊 Daily Operations

### Morning Checklist (05:00 UTC)

```bash
#!/bin/bash
# daily_check.sh - Run every morning

echo "🔍 PharmaRec AI Daily Health Check"
echo "================================"

# 1. Service availability
echo "[1/5] Checking service availability..."
curl -s https://pharmarec.ai/health > /dev/null && echo "✅ Frontend OK" || echo "❌ Frontend DOWN"
curl -s https://api.pharmarec.ai/health > /dev/null && echo "✅ Backend OK" || echo "❌ Backend DOWN"

# 2. Database status
echo "[2/5] Checking database..."
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U pharmarec > /dev/null && echo "✅ Database OK" || echo "❌ Database DOWN"

# 3. Disk space
echo "[3/5] Checking disk space..."
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%"
else
    echo "⚠️  WARNING: Disk usage: ${DISK_USAGE}%"
fi

# 4. Error rate (last 1 hour)
echo "[4/5] Checking error rate..."
ERROR_COUNT=$(docker-compose -f docker-compose.prod.yml logs --since 1h backend | grep -i "error" | wc -l)
if [ $ERROR_COUNT -lt 100 ]; then
    echo "✅ Errors in last hour: $ERROR_COUNT"
else
    echo "⚠️  WARNING: High error rate: $ERROR_COUNT errors"
fi

# 5. Backup status
echo "[5/5] Checking latest backup..."
LATEST_BACKUP=$(ls -t /backups/pharmarec_*.sql.gz 2>/dev/null | head -1)
BACKUP_AGE=$(($(date +%s) - $(stat -f%m "$LATEST_BACKUP" 2>/dev/null || stat -c%Y "$LATEST_BACKUP" 2>/dev/null)))
if [ $BACKUP_AGE -lt 86400 ]; then
    echo "✅ Latest backup: ${BACKUP_AGE}s ago"
else
    echo "⚠️  WARNING: No recent backup"
fi

echo ""
echo "Check https://pharmarec.ai:3000 (Grafana) for detailed metrics"
```

### Weekly Maintenance (Sunday 02:00 UTC)

```bash
# 1. Database maintenance
docker-compose -f docker-compose.prod.yml exec postgres VACUUM ANALYZE;

# 2. Log cleanup (keep last 7 days)
find /var/log/pharmarec -name "*.log" -mtime +7 -delete

# 3. Old backup cleanup (keep last 30 days)
find /backups -name "*.sql.gz" -mtime +30 -delete

# 4. Certificate renewal check
sudo certbot renew

# 5. Dependency checks
pip list --outdated | head -10  # Note any critical updates
npm outdated | head -10         # Check frontend updates
```

### Monthly Review (First Sunday of month)

```bash
# 1. Security patches
sudo apt update && apt list --upgradable

# 2. Performance analysis
# Review Grafana dashboards for:
#   - Request latency trends
#   - Database query performance
#   - Error rate trends
#   - Cache hit ratio

# 3. Capacity planning
# Check if scaling needed:
#   - CPU: currently ___%, target < 70%
#   - Memory: currently ___%, target < 80%
#   - Disk: currently ___%, target < 75%

# 4. Security review
# Check logs for:
#   - Failed login attempts
#   - Rate limit violations
#   - Malformed requests
#   - SQL injection attempts
```

---

## 🔧 Common Tasks

### Deploy New Version

```bash
# 1. Build images
docker-compose -f docker-compose.prod.yml build

# 2. Run tests in staging first
docker-compose -f docker-compose.staging.yml up
pytest tests/

# 3. Backup database (ALWAYS before deploy)
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U pharmarec pharmarec_prod | gzip > /backups/pre-deploy-$(date +%s).sql.gz

# 4. Stop services
docker-compose -f docker-compose.prod.yml stop

# 5. Update images
docker pull ghcr.io/your-org/pharmarec-ai/backend:latest
docker pull ghcr.io/your-org/pharmarec-ai/frontend:latest

# 6. Start with new images
docker-compose -f docker-compose.prod.yml up -d

# 7. Verify deployment
sleep 10
curl https://pharmarec.ai/health

# 8. Monitor for errors
docker-compose -f docker-compose.prod.yml logs -f backend --since 1m
```

### Scale Backend (Add Instances)

```bash
# 1. Update docker-compose.prod.yml
# Change: backend service replicas: 3

# 2. Create additional containers
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# 3. Update Nginx upstream configuration
# Edit infra/nginx/nginx.prod.conf to include new instances

# 4. Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# 5. Verify
docker-compose -f docker-compose.prod.yml ps
```

### Database Backup & Restore

```bash
# BACKUP
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U pharmarec pharmarec_prod | gzip > /backups/manual-$(date +%Y%m%d_%H%M%S).sql.gz

# RESTORE (⚠️ WARNING: Destructive!)
# Stop all connections
docker-compose -f docker-compose.prod.yml stop

# Restore from backup
zcat /backups/manual-20240214_150000.sql.gz | docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod

# Restart services
docker-compose -f docker-compose.prod.yml start
```

### Update Secrets/Environment

```bash
# 1. Edit .env file safely
# Use encrypted editor or vault
nano .env

# 2. Verify syntax
env -i bash -c 'source .env && env | sort'

# 3. Reload services without downtime
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml up -d backend

# 4. Verify change took effect
docker-compose -f docker-compose.prod.yml exec backend env | grep KEY_NAME
```

### SSL Certificate Renewal

```bash
# Manual renewal (or cron: 0 3 * * * certbot renew)
sudo certbot renew

# Copy to Docker volume
sudo cp /etc/letsencrypt/live/pharmarec.ai/fullchain.pem infra/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/pharmarec.ai/privkey.pem infra/nginx/ssl/key.pem

# Reload Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 🚨 Troubleshooting

### Backend Service Not Starting

```bash
# 1. Check logs
docker-compose -f docker-compose.prod.yml logs backend

# 2. Common causes:

# Cause A: Database not ready
# Solution: Wait or check postgres service
docker-compose -f docker-compose.prod.yml logs postgres
docker-compose -f docker-compose.prod.yml restart postgres

# Cause B: Port already in use
sudo lsof -i :8000
kill -9 <PID>

# Cause C: Permission denied on volumes
chmod 755 ./backend
chmod 755 ./logs

# Cause D: Import error
docker-compose -f docker-compose.prod.yml exec backend python -c "from backend.app.main import app; print('OK')"

# 3. Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### High Memory Usage

```bash
# 1. Check memory consumption
docker stats

# 2. Find memory leak
docker exec pharmarec-backend-prod python -c "
import tracemalloc
import sys
sys.path.insert(0, '/app')
tracemalloc.start()
from backend.app.main import app
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
"

# 3. Common causes:
# - Unbounded session cache
# - Large query results in memory
# - File handle leak

# 4. Solution options:
# - Reduce query result size (pagination)
# - Add caching layer (Redis)
# - Restart service
docker-compose -f docker-compose.prod.yml restart backend
```

### Database Performance Issues

```bash
# 1. Check active queries
docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod -c "
SELECT pid, user, query, query_start FROM pg_stat_activity WHERE state = 'active';
"

# 2. Find slow queries (slow query log)
docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod -c "
SELECT mean_time, calls, query FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
" 2>/dev/null || echo "pg_stat_statements not enabled"

# 3. Analyze query plan
docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod -c "
EXPLAIN ANALYZE SELECT * FROM sales WHERE sale_date > NOW() - INTERVAL '30 days';
"

# 4. Create missing indexes
docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod -c "
CREATE INDEX CONCURRENTLY idx_sales_date ON sales(sale_date);
CREATE INDEX CONCURRENTLY idx_medicine_expiry ON medicines(expiry_date);
"

# 5. Run maintenance
docker-compose -f docker-compose.prod.yml exec postgres psql -U pharmarec pharmarec_prod -c "
VACUUM ANALYZE;
"
```

### Network/Connectivity Issues

```bash
# 1. Test connectivity to services
curl -v https://pharmarec.ai/health
curl -v https://api.pharmarec.ai/health

# 2. Check Nginx status
docker-compose -f docker-compose.prod.yml logs nginx

# 3. Check DNS resolution
nslookup pharmarec.ai
dig pharmarec.ai

# 4. Test from inside container
docker-compose -f docker-compose.prod.yml exec backend curl http://nginx/health

# 5. Restart network services
docker-compose -f docker-compose.prod.yml restart nginx
docker network prune  # Remove unused networks
```

### Out of Disk Space

```bash
# 1. Check disk usage
df -h

# 2. Find large files/directories
du -sh /app/*
du -sh /backups/*
du -sh /var/log/*

# 3. Clean Docker
docker system prune -a  # ⚠️ Remove unused images/containers
docker volume prune     # Remove unused volumes

# 4. Rotate logs
docker-compose -f docker-compose.prod.yml logs > /dev/null

# 5. Archive old backups
tar czf /backups/archive-$(date +%Y%m).tar.gz /backups/pharmarec_*.sql.gz
rm /backups/pharmarec_*.sql.gz
```

---

## 📱 On-Call Procedures

### Critical Incident (P1 - System Down)

```
⏱ Max response time: 5 minutes

1. Acknowledge alert
   → Slack: "Investigating..."

2. Assess impact
   → For all services: docker-compose -f docker-compose.prod.yml ps
   → Check status page
   → Check recent deployments

3. Initial troubleshooting
   → Restart service: docker restart <service>
   → Check logs: docker logs -f <service>
   → Check disk/memory: docker stats

4. If not resolved (> 5 min)
   → Escalate to senior engineer
   → Prepare rollback plan
   → Document what happened

5. Communicate
   → Update status page to "Investigating"
   → Post in #incidents Slack channel
   → Email affected customers if needed
```

### High-Priority Incident (P2 - Degraded Performance)

```
⏱ Max response time: 15 minutes

1. Monitor trend
   → Watch Grafana dashboard
   → Check error rates
   → Verify impact scope

2. Begin investigation
   → Check recent code changes
   → Review db logs
   → Check for unusual traffic

3. Implement fix
   → Scale up if needed: docker-compose -f docker-compose.prod.yml up --scale backend=5
   → Clear cache if needed: redis-cli FLUSHALL (careful!)
   → Optimize queries
   → Or rollback if bad deploy

4. Verify resolution
   → Watch metrics return to normal
   → Test user flows
   → Confirm alert clears

5. Post-incident
   → Document root cause
   → Create action items
   → Schedule postmortem
```

---

## 📞 Escalation Matrix

| Severity | Response Time | On-Call? | Escalate if not resolved |
|----------|---------------|----------|-------------------------|
| P1 - Down | 5 min | Yes | Tech Lead (10 min) |
| P2 - Degraded | 15 min | No | Tech Lead (30 min) |
| P3 - Issue | 1 hour | No | Manager (next day) |
| P4 - Feature | 2 weeks | No | Product Manager |

---

## 🔗 Useful Links

- **Grafana Dashboards:** https://pharmarec.ai:3000
- **Prometheus Metrics:** https://pharmarec.ai:9090
- **Kibana Logs:** https://pharmarec.ai:5601
- **API Documentation:** https://api.pharmarec.ai/docs
- **Status Page:** https://status.pharmarec.ai

---

## 📚 Reference

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

