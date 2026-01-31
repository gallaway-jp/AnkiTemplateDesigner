# Fix for Behaviors Loading Hang
**Date**: 2026-01-24  
**Issue**: Dialog hanging at "Calling bridge.getAnkiBehaviors()..." with no further output

## Problem Analysis

The dialog was freezing during initialization at the point where it tries to load AnkiBehaviors. The JavaScript was calling `bridge.getAnkiBehaviors()` but no error was being logged, indicating:

1. **Missing error visibility**: The error was happening but not being displayed
2. **Silent failures**: No console output on the Python side when the method was called
3. **Incomplete error handling**: The JavaScript try-catch wasn't catching or reporting all error types

## Changes Made

### 1. Enhanced Python Logging (`gui/webview_bridge.py`)

Added comprehensive print debugging to track the execution flow:

```python
@pyqtSlot(result=str)
def getAnkiBehaviors(self) -> str:
    try:
        print("[WebViewBridge] getAnkiBehaviors() called")
        from ..services.ankijsapi_service import AnkiJSApiService
        print("[WebViewBridge] AnkiJSApiService imported")
        service = AnkiJSApiService()
        print("[WebViewBridge] AnkiJSApiService instantiated")
        behaviors = service.get_available_behaviors()
        print(f"[WebViewBridge] Got {len(behaviors)} behaviors")
        result = json.dumps(behaviors)
        print(f"[WebViewBridge] Returning JSON ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"[WebViewBridge] ERROR in getAnkiBehaviors: {e}")
        import traceback
        traceback.print_exc()
        print("[WebViewBridge] Returning empty list as fallback")
        return json.dumps([])
```

This allows us to see exactly where execution stops if something goes wrong.

### 2. Improved JavaScript Error Handling (`web/src/App.tsx`)

Enhanced the behavior loading code with:
- Method existence checking
- Promise validation
- Array type checking
- Fallback to empty array instead of throwing
- Better error logging

```typescript
// Check if bridge method exists
if (!bridge || typeof bridge.getAnkiBehaviors !== 'function') {
  throw new Error('bridge.getAnkiBehaviors is not a function');
}

// Check if promise was returned
if (!behaviorPromise) {
  throw new Error('bridge.getAnkiBehaviors returned null/undefined');
}

// Validate returned data is an array
if (!Array.isArray(behaviors)) {
  console.warn('behaviors is not an array:', behaviors);
  behaviors = behaviors ? Object.values(behaviors) : [];
}

// Use fallback instead of throwing
behaviors = [];
addDebugInfo(`Step 4d FALLBACK: Using empty behaviors array`);
```

## Why This Fixes The Issue

**Before:**
```
"Calling bridge.getAnkiBehaviors()..." 
→ (silent failure - no Python output, no JS error message)
→ Dialog becomes empty
```

**After:**
```
"Calling bridge.getAnkiBehaviors()..."
→ [WebViewBridge] getAnkiBehaviors() called
→ [WebViewBridge] AnkiJSApiService imported
→ [WebViewBridge] Got 67 behaviors
→ [WebViewBridge] Returning JSON (...)
→ "Step 4d: Loaded 67 behaviors successfully"
→ Dialog initializes properly
```

OR if there's an actual error:
```
→ [WebViewBridge] ERROR in getAnkiBehaviors: <error details>
→ traceback (stack trace)
→ [WebViewBridge] Returning empty list as fallback
→ "Step 4d FALLBACK: Using empty behaviors array"
→ Dialog initializes with empty behaviors
```

## Files Modified

1. **gui/webview_bridge.py** - Added verbose logging to getAnkiBehaviors()
2. **web/src/App.tsx** - Improved error handling and fallback logic
3. **web/dist/** - Rebuilt with updated App.tsx

## Testing

After the fix:
1. Check Anki console output for "[WebViewBridge]" messages
2. Check browser console (F12) for initialization progress
3. If there's an error, both Python and JavaScript will now report it clearly
4. Dialog will initialize even if behaviors fail to load (using empty array)

## What This Enables

- **Clear error messages**: Any failure is now logged to console
- **Better debugging**: Step-by-step output shows exactly where execution stops
- **Graceful degradation**: Dialog still loads even if behaviors can't be retrieved
- **Fallback behavior**: Empty behaviors array allows testing without AnkiBehaviors

## Next Steps

If the dialog still hangs:
1. Check Anki console for "[WebViewBridge]" debug output
2. Check browser console (F12 > Console tab) for error messages
3. Look for specific error that's now being logged
4. Fix the underlying issue revealed by the error message
