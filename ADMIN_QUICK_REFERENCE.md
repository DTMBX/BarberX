# Admin Observability Console - Quick Reference

## Quick Access

**For Owner Users:**
1. Look for the shield icon (🛡️) in the header
2. Click the shield icon to open Admin Console
3. Dashboard loads at `/#/admin-observability`

**Requirements:**
- Must be logged in as the Spark owner
- Detected via `spark.user().isOwner`

## Dashboard Tabs

### 1. Metrics
**Real-time operational metrics:**
- Ingestion Throughput: Documents processed per hour
- OCR Rate: Optical character recognition success percentage
- Parsing Errors: Failed parsing attempts in last hour
- Queue Depth: Pending items waiting for processing
- Search Latency: p95 latency in milliseconds
- Similarity Job Runtime: Average processing time in seconds

**Historical charts:**
- 24-hour view with 100 data points
- Anomaly detection (red/amber indicators)
- Hover for timestamp and exact value

### 2. Logs
**Structured application logs:**
- Filter by level: debug, info, warn, error, critical
- Filter by component: parser, search-engine, audit-logger, auth, api-gateway
- Click any log to see full details:
  - Correlation ID
  - Trace chain (parent-child relationships)
  - Metadata object
  - Stack trace (for errors)

**Use correlation IDs to trace user actions end-to-end across components**

### 3. Jobs
**Background job monitoring:**
- Status: queued, running, retrying, failed, completed
- Priority and retry count
- Progress bars for active jobs
- Error stacks for failures
- Estimated cost (future AI integration)

### 4. Health
**System health checks:**
- ✅ Green: Healthy
- ⚠️ Yellow: Degraded
- ❌ Red: Critical

**Checks performed:**
- Constitutional Parser Validation
- Search Index Consistency
- Citation Graph Integrity
- Database Connection Pool
- Network Latency

**Overall status determined by worst individual check**

### 5. Ledger
**Tamper-evident audit trail:**
- Total events in chain
- Verified events (valid hash links)
- Broken links detected
- Verification time
- ✓ VERIFIED or ⚠️ COMPROMISED status

**How it works:**
- Each event includes hash of previous event
- Verification recalculates all hashes
- Any tampering breaks the chain

### 6. Dependencies
**System Bill of Materials (SBOM):**
- Dependency name and version
- Type: parser, embedding-model, runtime, library
- Content hash for integrity verification
- Last updated date
- Security vulnerability status

**Export SBOM for compliance documentation**

## Controls

### Auto-Refresh
- Toggle button in top-right
- Refreshes metrics every 10 seconds when ON
- Manually refresh with "Refresh Now" button

### Filtering
- Logs: Click filter buttons to narrow results
- Historical charts: Hover over bars for details
- Jobs: Automatically sorted by creation time

## API Functions

### Get Metrics
```typescript
import { getObservabilityMetrics } from '@/lib/admin-api'
const metrics = await getObservabilityMetrics()
```

### Get Logs
```typescript
import { getStructuredLogs } from '@/lib/admin-api'
const logs = await getStructuredLogs(50, { level: 'error' })
```

### Run Health Checks
```typescript
import { runHealthChecks } from '@/lib/admin-api'
const suite = await runHealthChecks()
```

### Verify Ledger
```typescript
import { verifyLedgerIntegrity } from '@/lib/admin-api'
const verification = await verifyLedgerIntegrity()
```

### Generate SBOM
```typescript
import { generateSystemBOM } from '@/lib/admin-api'
const sbom = await generateSystemBOM()
```

## Data Storage

### Persistent (Spark KV)
- `admin:tamper-events` - Ledger events with hash chain
- `admin:policy-rules` - Policy enforcement rules

### Transient (Generated)
- Metrics: Regenerated on each request
- Logs: Last 50-100 entries in memory
- Health checks: Run on-demand
- SBOM: Generated from current dependencies

## Performance Tips

1. **Use auto-refresh** for live monitoring during deployments
2. **Filter logs** by component to reduce noise
3. **Check health first** when investigating issues
4. **Verify ledger** after any suspicious activity
5. **Export SBOM** before major version updates

## Troubleshooting

### Shield icon not visible
- ✅ Logged in as owner? Check `spark.user().isOwner`
- ✅ Page fully loaded? Wait for header to render
- ✅ Mobile view? Icon should still appear

### Dashboard not loading
- ✅ Check browser console for errors
- ✅ Verify route: should be `/#/admin-observability`
- ✅ Try manual refresh

### Metrics showing zero
- ✅ This is expected with mock data (random generation)
- ✅ Real integration will show actual system metrics

### Ledger showing COMPROMISED
- ✅ Check broken link event IDs
- ✅ Investigate events around that timestamp
- ✅ Review audit logs for tampering attempts

### Health checks failing
- ✅ Yellow is degraded but operational
- ✅ Red requires immediate attention
- ✅ Check error details in expanded view

## Next Steps After Implementation

1. **Connect Real Metrics**: Replace mock data with actual system metrics
2. **Set Up Alerting**: Configure thresholds for critical metrics
3. **Export Reports**: Generate compliance documentation for audits
4. **Add Retention Policies**: Implement log and artifact cleanup rules
5. **Build Policy Engine**: Define and enforce operational rules

## Related Documentation

- [ADMIN_OBSERVABILITY.md](./ADMIN_OBSERVABILITY.md) - Full technical architecture
- [ADMIN_IMPLEMENTATION_SUMMARY.md](./ADMIN_IMPLEMENTATION_SUMMARY.md) - Implementation details
- [COMPLIANCE.md](./COMPLIANCE.md) - Legal compliance documentation
- [PRD.md](./PRD.md) - Product requirements (includes admin features)

## Future Admin Tools (Type Definitions Ready)

- Provenance Diff Tool
- Policy Enforcement Engine
- Data Retention Manager
- Role Simulation Tool
- Configuration Versioning
- Security Hardening Dashboard
- Data Lineage Graph
- Sandbox Testing Harness
- Change Impact Analyzer
- Governance Documentation Generator
- Performance Tuning Advisor
- Incident Timeline Tool

**All type definitions exist in `/src/lib/admin-types.ts` and are ready for implementation**
