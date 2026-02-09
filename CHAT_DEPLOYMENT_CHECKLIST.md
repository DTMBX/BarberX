# Evident Chat - Deployment & Testing Checklist

## Pre-Deployment Verification

### Code Quality

- [ ] All Python files follow PEP 8 style guide
- [ ] No syntax errors in any file
- [ ] All imports are available
- [ ] No hardcoded keys or passwords
- [ ] All docstrings present for public methods
- [ ] Type hints on function signatures

### Security

- [ ] Master API key stored in environment variables
- [ ] Database passwords not in code
- [ ] CORS configured for production domain
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] SQL injection protection (SQLAlchemy parameterized)
- [ ] XSS protection (template escaping)
- [ ] Admin routes require authentication

### Database

- [ ] All migrations run successfully
- [ ] Chat tables created (5 new models)
- [ ] Indexes created for performance
- [ ] Foreign key constraints set up
- [ ] User existing data not affected
- [ ] Backup taken before migration

### Dependencies

- [ ] All requirements.txt packages pinned to versions
- [ ] New dependency (tiktoken) included
- [ ] No dependency version conflicts
- [ ] Virtual environment created
- [ ] All dependencies installed successfully

## Testing Checklist

### Unit Tests

- [ ] ChatService.create_conversation() works
- [ ] ChatService.add_message() stores correctly
- [ ] ChatService.get_conversation_history() returns correct format
- [ ] ChatService.count_tokens() accurate
- [ ] ChatService context management strategies work
- [ ] APIKeyManager encrypt/decrypt reversible
- [ ] APIKeyManager API validation works
- [ ] All prompt templates generate valid system prompts

### Integration Tests

- [ ] Database transactions commit/rollback properly
- [ ] Foreign key relationships work
- [ ] Cascade deletes work
- [ ] Indexes improve query performance
- [ ] No N+1 query problems

### API Tests

#### Conversation Endpoints

- [ ] POST /api/chat/conversations creates without error
- [ ] Response includes conversation ID
- [ ] Response includes session token
- [ ] GET /api/chat/conversations returns list
- [ ] GET /api/chat/conversations/<id> returns correct conversation
- [ ] DELETE /api/chat/conversations/<id> archives
- [ ] Cannot access other user's conversations

#### Message Endpoints

- [ ] POST /api/chat/messages sends and stores
- [ ] User must have API key configured
- [ ] Response includes AI message
- [ ] Tool calls parsing works
- [ ] GET /api/chat/conversations/<id>/messages returns history

#### Tool Endpoints

- [ ] GET /api/chat/tools returns all tools
- [ ] Tool descriptions present
- [ ] Tools have correct parameters
- [ ] Tools have correct access levels

#### Key Endpoints

- [ ] POST /api/chat/api-keys stores encrypted
- [ ] GET /api/chat/api-keys lists without exposing decrypted keys
- [ ] POST validate works with valid key
- [ ] POST validate fails gracefully with invalid key
- [ ] DELETE removes from active keys

#### Admin Endpoints

- [ ] Non-admin users get 403
- [ ] GET /admin/chat/statistics returns data
- [ ] GET /admin/chat/api-keys lists all keys
- [ ] DELETE /admin/chat/api-keys/<id> removes
- [ ] Maintenance endpoints work

### UI Tests

- [ ] Chat page loads without errors (/chat)
- [ ] Sidebar loads conversation list
- [ ] New Chat button works
- [ ] Message input enabled after API key
- [ ] Send button disabled until API key
- [ ] Messages display correctly (user blue, assistant gray)
- [ ] Message history scrolls properly
- [ ] Auto-expand textarea works
- [ ] Settings modal opens/closes
- [ ] Keyboard shortcuts work (Enter, Shift+Enter)
- [ ] Mobile responsive (test on iPhone, Android, tablet)

### OpenAI Integration Tests

- [ ] Valid API key accepted
- [ ] Invalid API key rejected
- [ ] API call successful with valid key
- [ ] Token counting accurate
- [ ] Response parsing correct
- [ ] Tool calls identified correctly
- [ ] Context window management prevents errors
- [ ] Rate limiting doesn't break flow

### Security Tests

- [ ] API keys encrypted in database
- [ ] Decryption works for authorized users
- [ ] Encrypted keys cannot be read directly from DB
- [ ] User can only see own data
- [ ] Admin can override access
- [ ] CSRF tokens work
- [ ] SQL injection attempts fail
- [ ] XSS attempts escape properly

### Performance Tests

- [ ] Chat page load time < 2 seconds
- [ ] API response time < 1 second (without OpenAI)
- [ ] OpenAI response time < 10 seconds (typical)
- [ ] Database queries use indexes
- [ ] No memory leaks on long conversations
- [ ] Can handle 1000+ messages in conversation
- [ ] Concurrent requests don't interfere
- [ ] Token counting doesn't cause latency

### Error Handling Tests

- [ ] No API key → graceful error message
- [ ] Invalid API key → clear error
- [ ] OpenAI rate limit → retry logic
- [ ] OpenAI error → user-friendly message
- [ ] Database error → logged and handled
- [ ] Tool execution error → logged and returned
- [ ] Token limit exceeded → auto-manage context
- [ ] Invalid request → 400 Bad Request

### Browser Compatibility

- [ ] Chrome latest version
- [ ] Firefox latest version
- [ ] Safari latest version
- [ ] Edge latest version
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Load Testing

### Concurrent Users

- [ ] 10 concurrent users → no errors
- [ ] 50 concurrent users → no slowdown
- [ ] 100 concurrent users → handles gracefully
- [ ] Rate limiting prevents abuse

### Message Volume

- [ ] 100 messages in conversation → renders
- [ ] 1000 messages → context managed
- [ ] Rapid messages (100/min) → queued properly

### Data Volume

- [ ] 1000 conversations per user → lists quickly
- [ ] 10,000 total messages → queries fast
- [ ] Large API keys list → admin panel responsive

## Deployment Steps

### Pre-Production

- [ ] Code review completed
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance baseline established
- [ ] Documentation reviewed
- [ ] Backup strategy verified

### Deployment

1. [ ] Stop current application
2. [ ] Backup database
3. [ ] Pull latest code
4. [ ] Install dependencies: `pip install -r requirements.txt`
5. [ ] Run migrations: `flask init-db`
6. [ ] Clear cache if applicable
7. [ ] Start application
8. [ ] Verify health checks
9. [ ] Run smoke tests
10. [ ] Monitor error logs

### Post-Deployment

- [ ] Monitor error rate for 1 hour
- [ ] Monitor performance metrics
- [ ] Test user workflows manually
- [ ] Check API response times
- [ ] Verify database backups
- [ ] Send deployment notification

### Rollback Plan

If issues occur:

1. [ ] Stop application
2. [ ] Restore from backup
3. [ ] Revert code to previous version
4. [ ] Start application with rollback
5. [ ] Notify team
6. [ ] Investigate issue
7. [ ] Re-deploy with fix

## Monitoring Setup

### Metrics to Track

- [ ] API response times (by endpoint)
- [ ] OpenAI API call success rate
- [ ] OpenAI API error rate
- [ ] Database query times
- [ ] Error rate by type
- [ ] User count and active sessions
- [ ] Message send rate
- [ ] API key validation failures
- [ ] Tool execution success rate
- [ ] Token usage patterns

### Alerts to Configure

- [ ] High error rate (>5%)
- [ ] Slow API response (>5s)
- [ ] Database connection failures
- [ ] OpenAI rate limit exceeded
- [ ] Disk space low
- [ ] Memory usage high
- [ ] Unhandled exceptions

### Logging

- [ ] All API requests logged
- [ ] API responses logged (no sensitive data)
- [ ] Database errors logged
- [ ] OpenAI errors logged
- [ ] Tool execution logged
- [ ] Security events logged
- [ ] Performance metrics logged
- [ ] Log rotation configured

## Documentation

- [ ] Installation guide complete
- [ ] Setup instructions clear
- [ ] API documentation accurate
- [ ] Architecture diagrams current
- [ ] Code comments present
- [ ] Examples provided
- [ ] Troubleshooting guide complete
- [ ] Quick start guide tested

## User Onboarding

- [ ] New user can log in
- [ ] New user redirect to chat
- [ ] Setup flow clear
- [ ] API key configuration documented
- [ ] First chat creation tested
- [ ] First message sent successfully
- [ ] Help/support accessible

## Post-Launch Support

- [ ] Support channel setup
- [ ] FAQ prepared
- [ ] Common issues documented
- [ ] Troubleshooting guide available
- [ ] Team trained on system
- [ ] Escalation process defined
- [ ] Update plan for issues
- [ ] User feedback collected

## Success Metrics

Measure success:

- [ ] Users creating conversations within first login
- [ ] Average conversation length > 5 messages
- [ ] API key configuration rate > 80%
- [ ] Tool usage across chats > 60%
- [ ] Error rate < 0.5%
- [ ] Average response time < 3 seconds
- [ ] User satisfaction rating > 4/5
- [ ] Daily active users > 50% of total
- [ ] No security incidents
- [ ] No data loss incidents

## Sign-Off

- [ ] Development team: ******\_\_\_\_****** Date: **\_**
- [ ] QA team: ******\_\_\_\_****** Date: **\_**
- [ ] Security team: ******\_\_\_\_****** Date: **\_**
- [ ] Operations team: ******\_\_\_\_****** Date: **\_**
- [ ] Product manager: ******\_\_\_\_****** Date: **\_**

---

## Testing Commands

### Run Unit Tests

```bash
pytest tests/test_chat_models.py -v
pytest tests/test_api_key_manager.py -v
pytest tests/test_chat_service.py -v
pytest tests/test_chat_routes.py -v
```

### Check Database

```bash
flask shell
>>> from auth.chat_models import Conversation, Message, UserAPIKey
>>> Conversation.query.count()  # Should be >= 0
>>> Message.query.count()       # Should be >= 0
>>> UserAPIKey.query.count()    # Should be >= 0
```

### Test API Manually

```bash
# Create conversation
curl -X POST http://localhost:5000/api/chat/conversations \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your-session" \
  -d '{}'

# List conversations
curl http://localhost:5000/api/chat/conversations \
  -H "Cookie: session=your-session"

# Get statistics (admin)
curl http://localhost:5000/admin/chat/statistics \
  -H "Cookie: session=admin-session"
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 50 http://localhost:5000/api/chat/tools

# Using wrk
wrk -t4 -c100 -d30s http://localhost:5000/api/chat/conversations
```

### Monitor Logs

```bash
# Follow Flask logs
tail -f logs/flask.log

# Check errors
grep ERROR logs/flask.log
```

---

## Go-Live Readiness

Final checklist before launch:

1. [ ] All tests passing
2. [ ] Code reviewed and approved
3. [ ] Security audit passed
4. [ ] Performance acceptable
5. [ ] Documentation complete
6. [ ] Team trained
7. [ ] Support process ready
8. [ ] Monitoring configured
9. [ ] Backup procedure verified
10. [ ] Rollback procedure tested

**Ready to launch when all items checked! ✅**
