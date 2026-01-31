# Debugging Guide - Anki Template Designer

## Log File Locations

### Python Logs
- **When debug logging is enabled**: `~/.anki_template_designer/template_designer.log` (with automatic rotation)
- **Add-on data folder**: Anki addon data directory → `addon_data/{addon_id}/logs/anki_template_designer.log`

### JavaScript Console
- Open browser DevTools in the webview: **Press F12**
- All console messages, errors, and unhandled rejections are logged

## Enabling Debug Logging

### Option 1: Via config.json
Edit `config.json` in the addon directory:
```json
{
  "debugLogging": true,
  "logLevel": "DEBUG"
}
```

**Options for logLevel**:
- `DEBUG` - Most verbose
- `INFO` - Important events
- `WARNING` - Issues and warnings
- `ERROR` - Only errors

### Option 2: Via Addon Settings (when UI is added)
In Anki, go to **Tools → Add-ons → Anki Template Designer → Config**

## What Gets Logged

### Python Side
- Bridge initialization and connection status
- Qt messages and warnings  
- All uncaught exceptions (with full traceback)
- Method calls from JavaScript (when `logClientEvent` is used)

### JavaScript Side
- Bridge initialization steps
- Window errors and unhandled promise rejections
- Bridge request/response timing
- All console.log/warn/error calls

## Troubleshooting Steps

### If app gets stuck at "Step 2: Initializing Python bridge..."

1. **Enable debug logging** in config.json
2. **Check the Python log** at `~/.anki_template_designer/template_designer.log`
3. **Look for error patterns**:
   - `QWebChannel not available` → Qt WebEngine not properly initialized
   - `Bridge object not found` → Python bridge not exposed to QWebChannel
   - Import errors → Missing dependencies

4. **Check browser console** (F12):
   - Look for network errors
   - Check for JavaScript parsing errors
   - Watch for promise rejections

### If you see "FATAL ERROR" in debug dialog

1. Take screenshot of the error
2. Check Python log for corresponding entries
3. Share both console logs when reporting issue

## Accessing Logs Programmatically

### Python
```python
from template_designer.utils import get_logger

logger = get_logger('my_module')
logger.info('This message will be logged')
logger.error('Error details', extra={'context': 'value'})
```

### JavaScript
```typescript
import { createLogger } from '@utils/logger';
import { bridge } from '@services/pythonBridge';

const logger = createLogger('MyModule');
logger.info('Message', { context: 'data' });

// Forward to Python file logging
bridge.logClientEvent('error', 'Something went wrong', { details: 'here' });
```

## Log File Structure

Each log entry contains:
- **Timestamp**: ISO format time when event occurred
- **Logger**: Module/component name
- **Level**: DEBUG, INFO, WARNING, ERROR
- **Message**: Human-readable description
- **Extra**: Additional context data when available

Example:
```
2026-01-24 10:30:45,123 - template_designer.bridge - INFO - Bridge initialized successfully
2026-01-24 10:30:46,456 - template_designer.js - ERROR - JS: Unhandled promise rejection with stack trace
```

## Performance Considerations

- Debug logging is **disabled by default** to avoid overhead
- When enabled, rotating file handler keeps logs under 50MB total
- Logs are automatically rotated when they exceed 10MB
- Old log files (template_designer.log.1, .log.2, etc.) are kept for 5 rotations

## Disabling Debug Logging

To improve performance or reduce disk usage:

```json
{
  "debugLogging": false,
  "logLevel": "INFO"
}
```

With `debugLogging: false`:
- No file logging occurs
- Console output still works (for warnings/errors only)
- Bridge still captures errors and forwards them
- Very minimal performance impact

## Common Issues & Solutions

| Issue | Check | Solution |
|-------|-------|----------|
| Empty log file | Time sync, permissions | Verify system time, check write permissions to log dir |
| "QWebChannel undefined" | Browser console (F12) | PyQt6 not installed or wrong version |
| Bridge timeout at Step 2 | Python log for connection status | Check if Python bridge is being properly exposed |
| JavaScript errors not logged | Browser console | Make sure error handler is installed (see main.tsx) |
| Disk space concerns | Log file size | Disable debug logging or manually delete old .log files |

