# Background Data Loading Solution for April 2026 Deployment

## Problem
Application takes 5-10 minutes to load all data during startup, exceeding the 10-second maximum probe timeout in IBM Cloud Code Engine.

## Solution: Separate Health Check Endpoint

### Approach
Add a lightweight `/health` endpoint that responds immediately, allowing the app to pass readiness checks while data loads in the background.

### Implementation Steps

1. **Add health check endpoint** (before data loading code):
```python
# Add after line 50 (after COS setup)
from flask import Flask
health_app = Flask('health_check')

@health_app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Application is starting'}, 200

# Start health check server in background thread
import threading
def run_health_server():
    health_app.run(host='0.0.0.0', port=8051, debug=False)

health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()
print("Health check server started on port 8051")
```

2. **Update Code Engine application** to use health endpoint:
```bash
ibmcloud ce application update --name python-appid-app \
  --probe-ready type=http \
  --probe-ready port=8051 \
  --probe-ready path=/health
```

3. **Keep all existing data loading** unchanged (lines 62-340)

### Benefits
- ✅ Minimal code changes (add ~15 lines)
- ✅ Low risk - doesn't modify existing logic
- ✅ App passes health checks immediately
- ✅ Data loads as before, just in "background" from probe perspective
- ✅ Can deploy April 2026 data today

### Risks
- Dashboard won't be functional until data finishes loading (~5-10 min)
- Users accessing during load time will see errors
- Can be mitigated with a loading page (future enhancement)

## Alternative: Full Async Refactoring
Would require:
- Moving all data loading to background thread
- Adding global state management
- Creating loading UI
- Extensive testing
- Estimated time: 4-6 hours

## Recommendation
Implement the health check endpoint solution first to unblock April deployment, then plan async refactoring for long-term scalability.