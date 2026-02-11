# Scripts Directory

Automation and utility scripts for the Evident platform.

## National Archives Integration

### Core Scripts

- **`fetch_founding_documents.py`** - Retrieve founding documents from National Archives API
  ```bash
  python scripts/fetch_founding_documents.py --all
  ```

- **`nara_scheduler.py`** - Automated task scheduler for periodic updates
  ```bash
  python scripts/nara_scheduler.py --daemon
  ```

- **`test_nara_setup.py`** - Test National Archives API integration
  ```bash
  python scripts/test_nara_setup.py
  ```

### Quick Start

1. Get API key from National Archives (Catalog_API@nara.gov)
2. Add to `.env`:
   ```bash
   NARA_API_KEY=your-api-key
   ```
3. Run test:
   ```bash
   python scripts/test_nara_setup.py
   ```
4. Fetch documents:
   ```bash
   python scripts/fetch_founding_documents.py
   ```

### Automation Options

**Daily Updates (Windows)**:
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\fetch_founding_documents.py" -WorkingDirectory "C:\web-dev\github-repos\Evident"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "UpdateFoundingDocs"
```

**Daily Updates (Linux/Mac)**:
```bash
# Add to crontab
0 2 * * * cd /path/to/Evident && python scripts/fetch_founding_documents.py
```

**Background Daemon**:
```bash
python scripts/nara_scheduler.py --daemon --update-interval 24
```

## Documentation

- [National Archives API](../docs/NATIONAL_ARCHIVES_API.md) - Complete documentation
- [Quick Start Guide](../docs/NARA_QUICKSTART.md) - 5-minute setup
- [Services README](../services/README.md) - API client usage

## Other Scripts

Additional scripts will be documented here as they are added.
