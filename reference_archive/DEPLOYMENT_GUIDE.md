# TariffAI Enterprise Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying TariffAI as an enterprise-grade production application with high availability, security, monitoring, and scalability.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Monitoring    │    │   Authentication│
│     (Nginx)     │    │   (Prometheus)  │    │    (Keycloak)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │    │   (FastAPI)     │    │  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cache         │    │   AI Service    │    │   Vector DB     │
│   (Redis)       │    │   (Ollama)      │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### System Requirements

- **CPU**: 8+ cores (16+ recommended)
- **RAM**: 16GB+ (32GB+ recommended)
- **Storage**: 100GB+ SSD
- **Network**: High-speed internet connection
- **OS**: Ubuntu 20.04+ or CentOS 8+

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Make
- SSL certificates (Let's Encrypt or commercial)

## Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/tariff-ai.git
cd tariff-ai

# Create production environment file
cp env.production.example .env.production

# Edit environment variables
nano .env.production
```

### 2. Configure Environment Variables

Edit `.env.production` with your production values:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://tariff_user:your_secure_password@postgres:5432/tariff_db
DB_PASSWORD=your_secure_db_password_here

# Redis Configuration
REDIS_URL=redis://:your_secure_redis_password@redis:6379/0
REDIS_PASSWORD=your_secure_redis_password_here

# Security
SECRET_KEY=your_very_long_and_secure_secret_key_here_change_in_production
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Configuration
API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
PROMETHEUS_MULTIPROC_DIR=/tmp

# Authentication
KEYCLOAK_ADMIN=admin
KEYCLOAK_PASSWORD=your_keycloak_admin_password
KEYCLOAK_DB_PASSWORD=your_keycloak_db_password

# Grafana
GRAFANA_PASSWORD=your_grafana_admin_password
```

### 3. SSL Certificate Setup

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# For production, use Let's Encrypt or commercial certificates
```

### 4. Build and Deploy

```bash
# Build all services
make build-production

# Start the application
make up-production

# Check status
make status
```

### 5. Initialize Database

```bash
# Run database migrations
make migrate

# Load initial data
make load-data

# Create admin user
make create-admin
```

## Production Configuration

### 1. Nginx Configuration

The production nginx configuration includes:
- SSL/TLS termination
- Load balancing
- Rate limiting
- Security headers
- Gzip compression
- Static file serving

### 2. Database Optimization

```sql
-- Create performance indexes
CREATE INDEX CONCURRENTLY idx_hts_codes_code ON hts_codes(hts_code);
CREATE INDEX CONCURRENTLY idx_hts_codes_description ON hts_codes USING gin(to_tsvector('english', description));
CREATE INDEX CONCURRENTLY idx_tariff_calculations_date ON tariff_calculations(calculated_at);

-- Configure PostgreSQL for production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### 3. Redis Configuration

```bash
# Redis production settings
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 4. Monitoring Setup

#### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

#### Grafana Dashboards

Import the provided Grafana dashboards for:
- System metrics
- Application performance
- Business metrics
- Error tracking

### 5. Logging Configuration

```bash
# Configure log rotation
sudo logrotate -f /etc/logrotate.d/tariff-ai

# Monitor logs
tail -f logs/app.log
tail -f logs/error.log
```

## Security Hardening

### 1. Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Application Security

- All passwords are hashed using bcrypt
- JWT tokens with short expiration
- Rate limiting on all endpoints
- Input validation and sanitization
- SQL injection prevention
- XSS protection headers

### 3. Container Security

```bash
# Run security scan
make security-scan

# Update base images regularly
make update-images

# Use non-root users in containers
# (Already configured in Dockerfiles)
```

## Backup and Recovery

### 1. Database Backup

```bash
# Automated daily backups
make backup-db

# Manual backup
make backup-db-manual

# Restore from backup
make restore-db BACKUP_FILE=backup_20231201_120000.sql
```

### 2. File Backup

```bash
# Backup uploaded files
make backup-files

# Backup configuration
make backup-config
```

### 3. Disaster Recovery

```bash
# Full system backup
make backup-full

# Restore system
make restore-full BACKUP_DIR=backup_20231201
```

## Monitoring and Alerting

### 1. Health Checks

```bash
# Check system health
make health-check

# Monitor specific services
make monitor-backend
make monitor-database
make monitor-redis
```

### 2. Alerting Rules

The system includes alerting for:
- High CPU/Memory usage
- Service downtime
- High error rates
- Database connection issues
- SSL certificate expiration

### 3. Performance Monitoring

```bash
# View performance metrics
make metrics

# Generate performance report
make performance-report
```

## Scaling

### 1. Horizontal Scaling

```bash
# Scale backend services
docker-compose -f docker-compose.production.yml up -d --scale backend=5

# Scale frontend services
docker-compose -f docker-compose.production.yml up -d --scale frontend=3
```

### 2. Database Scaling

```bash
# Add read replicas
# Configure connection pooling
# Implement database sharding if needed
```

### 3. Load Balancing

```bash
# Configure nginx load balancing
# Add health checks
# Implement sticky sessions if needed
```

## Maintenance

### 1. Regular Maintenance

```bash
# Weekly maintenance tasks
make maintenance-weekly

# Monthly maintenance tasks
make maintenance-monthly

# Quarterly maintenance tasks
make maintenance-quarterly
```

### 2. Updates and Patches

```bash
# Update application
make update-app

# Update dependencies
make update-deps

# Update system packages
make update-system
```

### 3. Performance Optimization

```bash
# Analyze performance
make performance-analyze

# Optimize database
make optimize-db

# Clear caches
make clear-cache
```

## Troubleshooting

### 1. Common Issues

```bash
# Check service status
make status

# View logs
make logs

# Restart services
make restart

# Check resource usage
make resources
```

### 2. Debug Mode

```bash
# Enable debug mode
make debug-on

# Disable debug mode
make debug-off
```

### 3. Emergency Procedures

```bash
# Emergency shutdown
make emergency-stop

# Emergency restart
make emergency-restart

# Rollback to previous version
make rollback
```

## Support and Documentation

### 1. Documentation

- API Documentation: `https://yourdomain.com/api/docs`
- System Documentation: `./docs/`
- User Guide: `./docs/user-guide.md`

### 2. Support Contacts

- Technical Support: support@yourdomain.com
- Emergency Contact: emergency@yourdomain.com
- Documentation: docs@yourdomain.com

### 3. Monitoring URLs

- Application: `https://yourdomain.com`
- API: `https://api.yourdomain.com`
- Monitoring: `https://monitoring.yourdomain.com`
- Authentication: `https://auth.yourdomain.com`

## Compliance and Auditing

### 1. Audit Logging

All actions are logged for compliance:
- User authentication
- Data access
- System changes
- API usage

### 2. Data Retention

- Logs: 30 days
- Backups: 90 days
- User data: As per privacy policy
- Audit trails: 7 years

### 3. Security Audits

```bash
# Run security audit
make security-audit

# Generate compliance report
make compliance-report
```

## Performance Benchmarks

### Expected Performance

- API Response Time: < 200ms (95th percentile)
- Database Queries: < 50ms
- AI Processing: < 5 seconds
- Concurrent Users: 1000+
- Throughput: 10,000+ requests/minute

### Load Testing

```bash
# Run load tests
make load-test

# Generate performance report
make performance-report
```

## Conclusion

This deployment guide provides a comprehensive approach to deploying TariffAI in an enterprise environment. Follow these steps carefully and ensure all security measures are in place before going live.

For additional support or questions, please refer to the documentation or contact the support team. 