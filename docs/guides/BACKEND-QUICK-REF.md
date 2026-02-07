# Evident Backend - Quick Reference Card

## 🚀 Quick Start (3 Steps)

### 1. Initialize Configuration

```python
from config_manager import ConfigManager
config_mgr = ConfigManager()
app.config.update(config_mgr.get_sqlalchemy_config())
```

### 2. Optimize Database

```python
from config_manager import DatabaseOptimizer
optimizer = DatabaseOptimizer(db)
optimizer.create_indexes()  # Creates 11 indexes
```

### 3. Use Services

```python
from unified_evidence_service import UnifiedEvidenceProcessor
processor = UnifiedEvidenceProcessor()
results = processor.process_evidence(file, type, context)
```

--

## 📦 Key Components

### Unified Evidence Service

```python
from unified_evidence_service import UnifiedEvidenceProcessor, EvidenceReportGenerator

# Process evidence
processor = UnifiedEvidenceProcessor()
results = processor.process_evidence(
    evidence_file=Path("video.mp4"),
    evidence_type="video",
    context={'case_number': 'CR-2024-001'}
)

# Generate report
report_gen = EvidenceReportGenerator()
markdown = report_gen.generate_report(results, format='markdown')
html = report_gen.generate_report(results, format='html')
```

### API Middleware

```python
from api_middleware import api_endpoint, rate_limit, require_tier

# Simple rate limiting
@app.route('/api/endpoint')
@rate_limit()
def endpoint():
    pass

# All-in-one protection
@app.route('/api/endpoint', methods=['POST'])
@api_endpoint(
    db,
    require_auth=True,
    min_tier='professional',
    validation_schema={'required': ['file']}
)
def protected():
    user = g.user
    data = request.validated_data
    return success_response("Success", data)
```

### Configuration Manager

```python
from config_manager import ConfigManager, DatabaseOptimizer, DatabaseBackup

# Configuration
config = ConfigManager()
db_uri = config.get_database_uri()

# Optimization
optimizer = DatabaseOptimizer(db)
optimizer.create_indexes()
optimizer.analyze_tables()

# Backup
backup = DatabaseBackup(db)
backup_file = backup.backup()
backup.cleanup_old_backups(keep_days=30)
```

--

## 🔐 Security

### Rate Limits

- **Free:** 10 req/min
- **Professional:** 60 req/min
- **Enterprise:** 300 req/min
- **Admin:** 1000 req/min

### Authentication

```python
# API key
@require_api_key(db)

# Tier requirement
@require_tier('professional')

# Combined
@api_endpoint(db, require_auth=True, min_tier='professional')
```

### Validation

```python
@validate_request({
    'required': ['field1', 'field2'],
    'types': {'field1': str, 'field2': int}
})
def endpoint():
    data = request.validated_data  # Validated data
```

--

## 📊 Performance

### Database Indexes (11 total)

- `idx_users_email`, `idx_users_username`, `idx_users_tier`
- `idx_analyses_user_id`, `idx_analyses_created_at`, `idx_analyses_status`,
  `idx_analyses_case_number`
- `idx_api_keys_user_id`, `idx_api_keys_key`
- `idx_usage_user_id`, `idx_usage_date`

### Connection Pooling

```python
# Automatic configuration
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,        # 10 persistent
    'max_overflow': 20,     # 20 additional
    'pool_timeout': 30,     # 30 second wait
    'pool_recycle': 3600,   # 1 hour recycle
    'pool_pre_ping': True   # Verify before use
}
```

### Caching

```python
# Automatic for transcription & OCR (1 hour TTL)
# Manual caching:
from backend_integration import cached

@cached(ttl=3600, key_prefix="my_operation")
def expensive_operation(param):
    pass
```

--

## 🔄 Integration

### Add to app.py

```python
# 1. Imports (top of file)
from config_manager import ConfigManager, DatabaseOptimizer
from unified_evidence_service import UnifiedEvidenceProcessor
from api_middleware import api_endpoint

# 2. Configuration (after app creation)
config_mgr = ConfigManager()
app.config.update(config_mgr.get_sqlalchemy_config())

# 3. Initialize (after db creation)
with app.app_context():
    optimizer = DatabaseOptimizer(db)
    optimizer.create_indexes()

processor = UnifiedEvidenceProcessor()

# 4. Use in routes
@app.route('/api/evidence/process', methods=['POST'])
@api_endpoint(db, require_auth=True, min_tier='professional')
def process_evidence():
    results = processor.process_evidence(...)
    return success_response("Complete", results)
```

--

## 🌍 Environment Variables

### Development (defaults work)

```bash
FLASK_ENV=development
DEBUG=true
```

### Production (required)

```bash
FLASK_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/Evident
STRIPE_SECRET_KEY=sk_live_...
OPENAI_API_KEY=sk-...
```

--

## 🔍 Monitoring

### Health Check

```bash
curl http://localhost:5000/health
```

### Performance Metrics

```python
from backend_integration import performance_monitor
stats = performance_monitor.get_stats()
print(f"Avg: {stats['operation']['avg_duration']:.2f}s")
```

### Slow Queries

```python
# Automatic logging to logs/slow_queries.log
# Queries > 1 second are logged
```

--

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "from app import db; db.engine.execute('SELECT 1')"
```

### Rate Limit Exceeded

```bash
# Check status
curl http://localhost:5000/api/rate-limit/status

# Response includes:
# - limit_per_minute
# - remaining
# - reset_in_seconds
```

### Import Error

```bash
# Install dependencies
pip install -r requirements.txt
```

--

## 📚 Documentation Files

1. **PLATFORM-DOCUMENTATION.md** - Complete technical docs
2. **BACKEND-INTEGRATION-SUMMARY.md** - Integration guide
3. **BACKEND-OPTIMIZATION-COMPLETE.md** - Architecture overview
4. **INTEGRATION-EXAMPLE.py** - Code examples for app.py
5. **BACKEND-COMPLETE-CHECKLIST.md** - Feature checklist

--

## ✅ Checklist

**Before Deployment:**

- [ ] Set production environment variables
- [ ] Run database optimizer: `optimizer.create_indexes()`
- [ ] Test health endpoint: `curl /health`
- [ ] Configure external services (Stripe, OpenAI, AWS)
- [ ] Setup database backups
- [ ] Configure logging

**After Deployment:**

- [ ] Monitor `/health` endpoint
- [ ] Check slow query logs
- [ ] Monitor rate limit usage
- [ ] Setup automated database backups
- [ ] Configure alerts for errors

--

## 🎯 Common Patterns

### Protected Endpoint

```python
@app.route('/api/endpoint', methods=['POST'])
@api_endpoint(db, require_auth=True, min_tier='professional')
def endpoint():
    return success_response("Success", {})
```

### Process Evidence

```python
results = processor.process_evidence(
    evidence_file=Path(file.filename),
    evidence_type="video",
    context={'case_number': 'CR-2024-001', 'user_id': g.user.id}
)
```

### Generate Report

```python
report = report_generator.generate_report(results, format='markdown')
```

### Event Subscription

```python
from backend_integration import event_bus

def on_processed(event):
    print(f"Processed: {event.data['evidence_id']}")

event_bus.subscribe('evidence.processed', on_processed)
```

--

**Evident Backend - Production Ready ✅**  
_Version 1.0 | January 26, 2026_
