"""DEPLOYMENT GUIDE

## Production Checklist

### Pre-Deployment
- [ ] All environment variables set
- [ ] Database backups configured
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] Email service set up
- [ ] Monitoring configured

### Security

1. **Secrets Management**
   - Use AWS Secrets Manager or HashiCorp Vault
   - Rotate keys regularly
   - Never commit .env files

2. **Database**
   - Enable SSL connections
   - Use strong passwords
   - Regular backups (daily minimum)
   - Read replicas for high availability

3. **API Security**
   - Enable rate limiting
   - Use HTTPS only
   - Implement request signing
   - Enable CORS restrictions

4. **Frontend**
   - Content Security Policy (CSP)
   - X-Frame-Options headers
   - Secure cookies

### Docker Compose Production

```bash
# Stop existing services
docker-compose down

# Pull latest images
docker-compose pull

# Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Verify
docker-compose exec backend alembic current
```

### Monitoring & Logging

1. **Backend Logs**
   ```bash
   docker-compose logs backend -f --tail 100
   ```

2. **Error Tracking**
   - Configure Sentry or similar
   - Set SENTRY_DSN in .env

3. **Health Checks**
   - Monitor: http://api.example.com/health
   - Alert on failures

### Scaling

**Horizontal Scaling:**
- Run multiple FastAPI workers
- Configure load balancer (nginx)
- Use managed PostgreSQL
- Use CDN for static assets

**Vertical Scaling:**
- Increase container resources
- Optimize queries
- Cache frequently accessed data

### Backup & Recovery

```bash
# Backup database
docker-compose exec postgres pg_dump -U retail_user retail_intelligence > backup.sql

# Restore database
docker-compose exec -T postgres psql -U retail_user retail_intelligence < backup.sql

# Backup uploaded files
tar -czf uploads-backup.tar.gz storage/uploads/
```

### SSL/HTTPS Setup

```bash
# Using Let's Encrypt with Certbot
certbot certonly --standalone -d api.example.com -d app.example.com

# Update docker-compose.yml with certificate paths
# Mount /etc/letsencrypt into containers
```

### Performance Optimization

1. **Database**
   - Add indexes on frequently queried columns
   - Use connection pooling
   - Enable query caching

2. **API**
   - Enable response caching
   - Use compression (gzip)
   - Implement pagination

3. **Frontend**
   - Build optimization
   - Image compression
   - CDN caching

### Update Procedure

1. Create backup
2. Pull latest code
3. Run migrations
4. Restart services
5. Verify health checks
6. Monitor error logs

### Troubleshooting Deployment Issues

**Container won't start:**
```bash
docker-compose logs <service> --tail 50
```

**Database connection fails:**
```bash
docker-compose exec postgres psql -U retail_user -c "SELECT 1"
```

**API returning 502:**
```bash
docker-compose restart backend
docker-compose logs backend -f
```

**Out of disk space:**
```bash
# Clean up old containers/images
docker system prune -a

# Check disk usage
docker system df
```

### High Availability Setup

1. **Database**: Master-Replica setup
2. **API**: Load balanced multiple instances
3. **Redis**: Sentinel for auto-failover
4. **Frontend**: CDN + S3 for static assets
5. **DNS**: Route53 or similar for failover

### Compliance & Auditing

- Enable database audit logging
- Track API access logs
- Implement request/response logging
- Store logs for compliance period
- Regular security audits

### Cost Optimization

- Use spot instances for non-critical workloads
- Set resource limits on containers
- Use auto-scaling for variable load
- Monitor and optimize expensive queries
- Use caching aggressively

---

For additional help, see README.md and SETUP.md
"""
