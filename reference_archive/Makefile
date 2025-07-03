# TariffAI Enterprise Makefile
# Comprehensive build, test, and deployment automation

.PHONY: help build test deploy clean docker-build docker-up docker-down
.PHONY: production development staging backup restore monitor logs
.PHONY: security audit performance health database migrate
.PHONY: setup install update maintenance

# Default target
help: ## Show this help message
	@echo "TariffAI Enterprise Management Commands"
	@echo "======================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

setup: ## Initial project setup
	@echo "🚀 Setting up TariffAI Enterprise..."
	mkdir -p data logs backups uploads static
	cp env.production.example .env.production
	@echo "✅ Setup complete. Please edit .env.production with your configuration."

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	cd backend && pip install -r requirements.production.txt
	cd frontend && npm ci --production
	@echo "✅ Dependencies installed."

update: ## Update all dependencies
	@echo "🔄 Updating dependencies..."
	cd backend && pip install -r requirements.production.txt --upgrade
	cd frontend && npm update
	@echo "✅ Dependencies updated."

# =============================================================================
# BUILD & COMPILATION
# =============================================================================

build: ## Build all components
	@echo "🔨 Building TariffAI..."
	$(MAKE) build-backend
	$(MAKE) build-frontend
	@echo "✅ Build complete."

build-backend: ## Build backend application
	@echo "🔨 Building backend..."
	cd backend && python -m compileall .
	@echo "✅ Backend built."

build-frontend: ## Build frontend application
	@echo "🔨 Building frontend..."
	cd frontend && npm run build
	@echo "✅ Frontend built."

build-production: ## Build for production
	@echo "🏭 Building for production..."
	$(MAKE) build-backend
	$(MAKE) build-frontend
	docker-compose -f docker-compose.production.yml build
	@echo "✅ Production build complete."

# =============================================================================
# TESTING
# =============================================================================

test: ## Run all tests
	@echo "🧪 Running tests..."
	$(MAKE) test-backend
	$(MAKE) test-frontend
	@echo "✅ All tests completed."

test-backend: ## Run backend tests
	@echo "🧪 Testing backend..."
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html
	@echo "✅ Backend tests completed."

test-frontend: ## Run frontend tests
	@echo "🧪 Testing frontend..."
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "✅ Frontend tests completed."

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit
	@echo "✅ Integration tests completed."

test-performance: ## Run performance tests
	@echo "⚡ Running performance tests..."
	cd backend && python -m pytest tests/test_performance.py -v
	@echo "✅ Performance tests completed."

test-security: ## Run security tests
	@echo "🔒 Running security tests..."
	cd backend && python -m pytest tests/test_security.py -v
	@echo "✅ Security tests completed."

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build
	@echo "✅ Docker images built."

docker-up: ## Start Docker services
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ Docker services started."

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down
	@echo "✅ Docker services stopped."

docker-clean: ## Clean Docker resources
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Docker resources cleaned."

# =============================================================================
# PRODUCTION DEPLOYMENT
# =============================================================================

production: ## Deploy to production
	@echo "🚀 Deploying to production..."
	$(MAKE) build-production
	$(MAKE) up-production
	$(MAKE) migrate
	$(MAKE) health-check
	@echo "✅ Production deployment complete."

up-production: ## Start production services
	@echo "🚀 Starting production services..."
	docker-compose -f docker-compose.production.yml up -d
	@echo "✅ Production services started."

down-production: ## Stop production services
	@echo "🛑 Stopping production services..."
	docker-compose -f docker-compose.production.yml down
	@echo "✅ Production services stopped."

restart-production: ## Restart production services
	@echo "🔄 Restarting production services..."
	$(MAKE) down-production
	$(MAKE) up-production
	@echo "✅ Production services restarted."

# =============================================================================
# DEVELOPMENT
# =============================================================================

development: ## Start development environment
	@echo "🛠️ Starting development environment..."
	docker-compose up -d
	@echo "✅ Development environment started."

dev-backend: ## Start backend in development mode
	@echo "🛠️ Starting backend development server..."
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend in development mode
	@echo "🛠️ Starting frontend development server..."
	cd frontend && npm start

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

database: ## Database operations menu
	@echo "🗄️ Database Operations:"
	@echo "  migrate     - Run database migrations"
	@echo "  backup      - Create database backup"
	@echo "  restore     - Restore from backup"
	@echo "  reset       - Reset database"
	@echo "  optimize    - Optimize database"

migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	cd backend && alembic upgrade head
	@echo "✅ Migrations completed."

backup: ## Create database backup
	@echo "💾 Creating database backup..."
	mkdir -p backups
	docker-compose exec postgres pg_dump -U tariff_user tariff_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created."

backup-db: ## Create database backup (production)
	@echo "💾 Creating production database backup..."
	mkdir -p backups
	docker-compose -f docker-compose.production.yml exec postgres pg_dump -U tariff_user tariff_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Production backup created."

restore: ## Restore database from backup
	@echo "🔄 Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	docker-compose exec postgres psql -U tariff_user tariff_db < backups/$$backup_file
	@echo "✅ Database restored."

reset-db: ## Reset database
	@echo "🔄 Resetting database..."
	docker-compose exec postgres psql -U tariff_user -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) migrate
	@echo "✅ Database reset."

optimize-db: ## Optimize database
	@echo "⚡ Optimizing database..."
	docker-compose exec postgres psql -U tariff_user tariff_db -c "VACUUM ANALYZE;"
	@echo "✅ Database optimized."

# =============================================================================
# MONITORING & HEALTH
# =============================================================================

monitor: ## Open monitoring dashboards
	@echo "📊 Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"
	@echo "Kibana: http://localhost:5601"

health-check: ## Check system health
	@echo "🏥 Checking system health..."
	curl -f http://localhost/health || echo "❌ Health check failed"
	@echo "✅ Health check completed."

status: ## Show service status
	@echo "📊 Service Status:"
	docker-compose ps

logs: ## Show application logs
	@echo "📋 Application logs:"
	docker-compose logs -f

logs-backend: ## Show backend logs
	@echo "📋 Backend logs:"
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	@echo "📋 Frontend logs:"
	docker-compose logs -f frontend

logs-production: ## Show production logs
	@echo "📋 Production logs:"
	docker-compose -f docker-compose.production.yml logs -f

# =============================================================================
# SECURITY & AUDIT
# =============================================================================

security: ## Security operations menu
	@echo "🔒 Security Operations:"
	@echo "  audit       - Run security audit"
	@echo "  scan        - Security vulnerability scan"
	@echo "  update      - Update security patches"

audit: ## Run security audit
	@echo "🔒 Running security audit..."
	cd backend && bandit -r app/
	cd frontend && npm audit
	@echo "✅ Security audit completed."

security-scan: ## Run security vulnerability scan
	@echo "🔒 Running security vulnerability scan..."
	docker run --rm -v $(PWD):/app owasp/zap2docker-stable zap-baseline.py -t http://localhost
	@echo "✅ Security scan completed."

update-security: ## Update security patches
	@echo "🔒 Updating security patches..."
	cd backend && pip install --upgrade pip
	cd frontend && npm audit fix
	@echo "✅ Security patches updated."

# =============================================================================
# PERFORMANCE & OPTIMIZATION
# =============================================================================

performance: ## Performance operations menu
	@echo "⚡ Performance Operations:"
	@echo "  analyze     - Analyze performance"
	@echo "  optimize    - Optimize system"
	@echo "  benchmark   - Run benchmarks"

analyze: ## Analyze performance
	@echo "⚡ Analyzing performance..."
	cd backend && python -m pytest tests/test_performance.py -v
	@echo "✅ Performance analysis completed."

optimize: ## Optimize system performance
	@echo "⚡ Optimizing system performance..."
	$(MAKE) optimize-db
	docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ System optimization completed."

benchmark: ## Run performance benchmarks
	@echo "⚡ Running performance benchmarks..."
	cd backend && python -m pytest tests/test_benchmark.py -v
	@echo "✅ Performance benchmarks completed."

# =============================================================================
# MAINTENANCE
# =============================================================================

maintenance: ## Maintenance operations menu
	@echo "🔧 Maintenance Operations:"
	@echo "  weekly      - Weekly maintenance"
	@echo "  monthly     - Monthly maintenance"
	@echo "  cleanup     - System cleanup"

maintenance-weekly: ## Weekly maintenance tasks
	@echo "🔧 Running weekly maintenance..."
	$(MAKE) backup
	$(MAKE) optimize-db
	$(MAKE) cleanup-logs
	@echo "✅ Weekly maintenance completed."

maintenance-monthly: ## Monthly maintenance tasks
	@echo "🔧 Running monthly maintenance..."
	$(MAKE) update
	$(MAKE) audit
	$(MAKE) performance-analyze
	@echo "✅ Monthly maintenance completed."

cleanup: ## System cleanup
	@echo "🧹 Running system cleanup..."
	$(MAKE) cleanup-logs
	$(MAKE) cleanup-cache
	$(MAKE) docker-clean
	@echo "✅ System cleanup completed."

cleanup-logs: ## Clean up old logs
	@echo "🧹 Cleaning up old logs..."
	find logs/ -name "*.log" -mtime +30 -delete
	@echo "✅ Log cleanup completed."

cleanup-cache: ## Clean up cache
	@echo "🧹 Cleaning up cache..."
	docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ Cache cleanup completed."

# =============================================================================
# UTILITIES
# =============================================================================

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf backend/__pycache__
	rm -rf frontend/build
	rm -rf frontend/node_modules
	@echo "✅ Cleanup completed."

reset: ## Reset entire system
	@echo "🔄 Resetting entire system..."
	$(MAKE) docker-down
	$(MAKE) docker-clean
	$(MAKE) clean
	@echo "✅ System reset completed."

debug-on: ## Enable debug mode
	@echo "🐛 Enabling debug mode..."
	sed -i 's/DEBUG=false/DEBUG=true/' .env.production
	@echo "✅ Debug mode enabled."

debug-off: ## Disable debug mode
	@echo "🐛 Disabling debug mode..."
	sed -i 's/DEBUG=true/DEBUG=false/' .env.production
	@echo "✅ Debug mode disabled."

# =============================================================================
# EMERGENCY OPERATIONS
# =============================================================================

emergency-stop: ## Emergency stop all services
	@echo "🚨 Emergency stop initiated..."
	docker-compose -f docker-compose.production.yml down
	@echo "✅ Emergency stop completed."

emergency-restart: ## Emergency restart all services
	@echo "🚨 Emergency restart initiated..."
	$(MAKE) emergency-stop
	$(MAKE) up-production
	@echo "✅ Emergency restart completed."

rollback: ## Rollback to previous version
	@echo "🔄 Rolling back to previous version..."
	git checkout HEAD~1
	$(MAKE) build-production
	$(MAKE) up-production
	@echo "✅ Rollback completed."

# =============================================================================
# REPORTING
# =============================================================================

report: ## Generate system report
	@echo "📊 Generating system report..."
	@echo "System Report - $(shell date)" > system_report.txt
	@echo "========================" >> system_report.txt
	$(MAKE) status >> system_report.txt
	@echo "✅ System report generated: system_report.txt"

performance-report: ## Generate performance report
	@echo "📊 Generating performance report..."
	cd backend && python -m pytest tests/test_performance.py --html=performance_report.html
	@echo "✅ Performance report generated: performance_report.html"

compliance-report: ## Generate compliance report
	@echo "📊 Generating compliance report..."
	cd backend && python -m pytest tests/test_compliance.py --html=compliance_report.html
	@echo "✅ Compliance report generated: compliance_report.html"

# =============================================================================
# HELPERS
# =============================================================================

version: ## Show version information
	@echo "TariffAI Enterprise v1.0.0"
	@echo "Build: $(shell git rev-parse --short HEAD)"
	@echo "Date: $(shell date)"

info: ## Show system information
	@echo "System Information:"
	@echo "OS: $(shell uname -s)"
	@echo "Architecture: $(shell uname -m)"
	@echo "Docker: $(shell docker --version)"
	@echo "Python: $(shell python --version)"
	@echo "Node: $(shell node --version)"

# =============================================================================
# DEVELOPMENT HELPERS
# =============================================================================

dev-setup: ## Setup development environment
	@echo "🛠️ Setting up development environment..."
	$(MAKE) setup
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✅ Development environment setup complete."

dev-test: ## Run tests in development
	@echo "🧪 Running development tests..."
	$(MAKE) test-backend
	$(MAKE) test-frontend
	@echo "✅ Development tests completed."

dev-lint: ## Run linting
	@echo "🔍 Running linting..."
	cd backend && black app/ && isort app/ && flake8 app/
	cd frontend && npm run lint
	@echo "✅ Linting completed."

dev-format: ## Format code
	@echo "🎨 Formatting code..."
	cd backend && black app/ && isort app/
	cd frontend && npm run format
	@echo "✅ Code formatting completed." 