# UI Behavior Issues - Detailed Quick Reference

**Total Issues**: 42 | **Critical**: 23 | **Medium**: 12 | **Low**: 7

---

## CRITICAL ISSUES - ACTION REQUIRED

### Analytics Dashboard (6 critical)

#### 1. Summary Cards Don't Update on Tab Switch
- **File**: [web/analytics_dashboard_ui.js](web/analytics_dashboard_ui.js#L71-L85)
- **Problem**: Overview tab summary cards show values only if `loadDashboardData()` called; switching back to Overview from another tab shows stale data
- **Current Code**: Card values set in `loadDashboardData()` but called only via refresh button
- **Fix**: Call `loadDashboardData()` in `switchTab()` when tabName === 'overview'
- **Priority**: P0 - User impact is immediate

#### 2. Export Button Does Nothing
- **File**: [web/analytics_dashboard_ui.js](web/analytics_dashboard_ui.js#L531)
- **Problem**: Export button shows alert instead of exporting data
- **Current Code**: `showExportMenu()` only shows alert with options
- **Fix**: Implement actual export methods (JSON, CSV, PDF) calling backend API
- **Priority**: P1 - Feature completely broken

#### 3. Sampling Rate Setting Not Saved
- **File**: [web/analytics_dashboard_ui.js](web/analytics_dashboard_ui.js#L523)
- **Problem**: Changing sampling rate updates UI but doesn't persist to backend
- **Current Code**: `updateSamplingRate()` is `console.log()` stub
- **Fix**: Call `window.bridge.updateAnalyticsSamplingRate(rate)`
- **Priority**: P1 - User settings lost

#### 4. Retention Days Setting Not Saved
- **File**: [web/analytics_dashboard_ui.js](web/analytics_dashboard_ui.js#L527)
- **Problem**: Same as above for retention
- **Current Code**: `updateRetentionDays()` is stub
- **Fix**: Call `window.bridge.updateAnalyticsRetention(days)`
- **Priority**: P1

#### 5. Cleanup Old Data Does Nothing
- **File**: [web/analytics_dashboard_ui.js](web/analytics_dashboard_ui.js#L535)
- **Problem**: Cleanup button confirmed but doesn't actually delete data
- **Current Code**: `cleanupOldData()` is stub
- **Fix**: Call `window.bridge.cleanupAnalyticsData()`
- **Priority**: P1

#### 6. Recent Insights Not Updated with Refresh
- **File**: [web/analytics_dashboard_ui.js](web/analytics_dashboard_ui.js#L387-L405)
- **Problem**: Insights section relies on `loadDashboardData()` but doesn't refresh independently
- **Current Code**: `updateRecentInsights()` called from `loadDashboardData()` only
- **Fix**: Ensure insights refresh when analytics data refreshes
- **Priority**: P1

---

### Collaboration UI (4 critical)

#### 7. Collaborators List Always Empty
- **File**: [web/collaboration_ui.js](web/collaboration_ui.js#L220-L235)
- **Problem**: Presence tab shows empty list; users never see who's editing
- **Current Code**: `renderPresence()` iterates over `this.collaborators` Map which is never populated
- **Fix**: Backend must emit collaborator updates calling `ui.updatePresence(collaboratorList)`
- **Priority**: P0 - Core collaboration feature broken

#### 8. Comments Submitted But Never Appear
- **File**: [web/collaboration_ui.js](web/collaboration_ui.js#L239-L275)
- **Problem**: User posts comment, gets cleared from UI, but comment never appears in list
- **Current Code**: `submitComment()` emits event but `renderComments()` never called with data
- **Fix**: Backend must send comment data back to frontend; frontend must call `updateComments(data)`
- **Priority**: P0 - User-facing feature broken

#### 9. Version History Tab Completely Empty
- **File**: [web/collaboration_ui.js](web/collaboration_ui.js)
- **Problem**: History tab has no data and no method to load it
- **Current Code**: No `loadHistory()` method defined
- **Fix**: Implement `loadHistory()` to fetch versions from backend
- **Priority**: P1 - Feature unavailable

#### 10. Sync Status Never Changes
- **File**: [web/collaboration_ui.js](web/collaboration_ui.js#L41-L43)
- **Problem**: Indicator shows "Ready" on init but never updates to reflect actual sync state
- **Current Code**: `updateSyncStatus()` method exists but never called from backend
- **Fix**: Backend must call `ui.updateSyncStatus('syncing'|'synced'|'error')` 
- **Priority**: P1 - User unaware of sync state

---

### Backup UI (2 critical)

#### 11. Backup Progress Never Shown
- **File**: [web/backup_ui.js](web/backup_ui.js#L115-L119)
- **Problem**: User clicks "Create Backup" button but sees no progress; doesn't know if it's working
- **Current Code**: Button emits event but no progress UI handling
- **Fix**: 
  1. Show progress indicator on button click
  2. Backend must emit progress updates
  3. Frontend must update progress bar in real-time
- **Priority**: P0 - Users think backup failed

#### 12. Recovery Points List Never Shows
- **File**: [web/backup_ui.js](web/backup_ui.js#L350-L372)
- **Problem**: Recovery tab opens but shows empty list with no restore options
- **Current Code**: `loadRecoveryPoints()` implemented but may not be called on tab switch
- **Fix**: Ensure `loadRecoveryPoints()` called when recovery tab switched to
- **Priority**: P0 - Users can't restore backups

---

### Cloud Sync UI (4 critical)

#### 13. Conflict Modal Never Populated
- **File**: [web/cloud_sync_ui.js](web/cloud_sync_ui.js#L178-L200)
- **Problem**: Conflict dialog shows but with no information about conflicting versions
- **Current Code**: Modal HTML exists but no method to fill in conflict details
- **Fix**: Implement `populateConflictModal(conflictData)` to show file names, timestamps, content preview
- **Priority**: P0 - Conflicts can't be resolved

#### 14. Offline Queue Never Shows Pending Operations
- **File**: [web/cloud_sync_ui.js](web/cloud_sync_ui.js#L215)
- **Problem**: Offline tab shows empty queue; users don't know what will sync
- **Current Code**: `updateOfflineQueue()` never called with data
- **Fix**: Populate queue when operations added in offline mode
- **Priority**: P1 - Users unsure what will happen on reconnect

#### 15. Sync Progress Bar Hidden
- **File**: [web/cloud_sync_ui.js](web/cloud_sync_ui.js#L127)
- **Problem**: During sync, user sees nothing happening
- **Current Code**: Progress bar has `style="display: none"` inline
- **Fix**: Remove display: none and show progress on sync
- **Priority**: P1 - Long syncs appear frozen

#### 16. Sync Statistics Never Update
- **File**: [web/cloud_sync_ui.js](web/cloud_sync_ui.js#L87-L103)
- **Problem**: Stats cards show "0 files uploaded" always
- **Current Code**: Stat values never populated from backend
- **Fix**: Backend must update `this.syncStats` on sync completion
- **Priority**: P1 - Users have no visibility into sync activity

---

### Designer Core UI (2 critical)

#### 17. Save State Feedback Unreliable
- **File**: [web/designer.js](web/designer.js#L30-L63)
- **Problem**: User clicks save but not certain if save succeeded
- **Current Code**: Callback functions exist but backend may not call them
- **Fix**: Ensure backend always calls `notifySaveSuccess()` or `notifySaveError()`
- **Priority**: P0 - Users lose work thinking it saved

#### 18. Loading Progress Bar Unreliable
- **File**: [web/designer.js](web/designer.js#L109-L118)
- **Problem**: Progress bar may complete before actual loading finishes or stay stuck
- **Current Code**: Progress manually updated but may not align with actual completion
- **Fix**: Track actual component initialization and only advance progress when truly done
- **Priority**: P1 - Users think load failed when it's still loading

---

### Plugin Manager UI (2 critical)

#### 19. Install Button Text Not Synced
- **File**: [web/plugin_manager_ui.js](web/plugin_manager_ui.js#L231-L240)
- **Problem**: Marketplace shows "Install" for already-installed plugins
- **Current Code**: Marketplace rendering doesn't check installed list
- **Fix**: In marketplace rendering, check if plugin exists in `this.plugins` before showing button text
- **Priority**: P1 - User confusion

#### 20. Marketplace Search Doesn't Filter Properly
- **File**: [web/plugin_manager_ui.js](web/plugin_manager_ui.js#L359-L400)
- **Problem**: Search in marketplace doesn't filter results correctly
- **Current Code**: `filterPlugins()` doesn't properly handle marketplace filtering
- **Fix**: Complete marketplace filtering logic in `filterPlugins()`
- **Priority**: P1 - Users can't find plugins

---

### Cloud Sync UI (2 more critical)

#### 21. Auto-Sync Toggle Doesn't Persist
- **File**: [web/cloud_sync_ui.js](web/cloud_sync_ui.js#L336-L341)
- **Problem**: User enables auto-sync but setting lost on reload
- **Current Code**: `toggleAutoSync()` updates button but doesn't save to backend
- **Fix**: Call `window.bridge.setAutoSync(enabled)` or save to localStorage
- **Priority**: P1 - User preferences lost

#### 22. Storage Quota Never Updates
- **File**: [web/cloud_sync_ui.js](web/cloud_sync_ui.js#L148-L158)
- **Problem**: Storage quota bar empty; users don't know utilization
- **Current Code**: Quota elements exist but `this.storageStats` never populated
- **Fix**: Backend must update storage stats on sync completion
- **Priority**: P2 - Information not available

---

### General UI (1 critical)

#### 23. Error Dialogs Not Shown
- **File**: [web/designer.js](web/designer.js#L144)
- **Problem**: Initialization errors logged to console but user not notified
- **Current Code**: `showError()` function referenced but may not display prominently
- **Fix**: Ensure `showError()` displays modal dialog
- **Priority**: P0 - Errors go unnoticed

---

## MEDIUM ISSUES (12)

| # | Component | Issue | File | Line | Fix |
|---|-----------|-------|------|------|-----|
| 24 | Analytics | Recent Insights Not Refreshed | analytics_dashboard_ui.js | 387 | Ensure insights refresh with refresh button |
| 25 | Collaboration | Tab Switch Not Loading Data | collaboration_ui.js | 179 | Add data loading in switchTab() |
| 26 | Collaboration | Tab Switch Not Loading Data | collaboration_ui.js | 179 | Add data loading in switchTab() |
| 27 | Backup | Stats Not Auto-Updated | backup_ui.js | 221 | Call updateStats() after backup |
| 28 | Backup | Restore Missing Progress | backup_ui.js | 387 | Show restore progress indicator |
| 29 | Cloud Sync | Progress Bar Style Issue | cloud_sync_ui.js | 127 | Remove inline display: none |
| 30 | Cloud Sync | Auto-Sync Not Saved | cloud_sync_ui.js | 336 | Persist setting to backend |
| 31 | Cloud Sync | Quota Never Updates | cloud_sync_ui.js | 148 | Update from backend data |
| 32 | Performance | Bottleneck List Empty | performance_dashboard_ui.js | 204 | Populate from optimizer data |
| 33 | Performance | Violations Not Shown | performance_dashboard_ui.js | 210 | Extract from healthStatus |
| 34 | Performance | Operations List Empty | performance_dashboard_ui.js | 216 | Load from operation logs |
| 35 | Project Browser | Action Feedback Missing | project-browser.js | 110 | Show toast on completion |

---

## LOW ISSUES (7)

| # | Component | Issue | Impact |
|----|-----------|-------|--------|
| 36 | Designer | Toast Notifications Overlap | Low - visual clutter |
| 37 | Designer | Error Not Prominent | Medium - users miss errors |
| 38 | Customization | Layout Changes Not Confirmed | Low - user unsure if saved |
| 39 | Customization | No Save Feedback | Low - no visual feedback |
| 40 | Validation | Errors Not User-Friendly | Low - technical messages |
| 41 | Validation | No Real-Time Feedback | Low - errors only on submit |
| 42 | Project Browser | Search Stales on Updates | Low - search doesn't refresh |

---

## Quick Fix Checklist

### This Week (Critical Only)
- [ ] Analytics: Fix summary cards update on tab switch
- [ ] Analytics: Implement export functionality  
- [ ] Analytics: Implement settings persistence
- [ ] Collaboration: Add backend collaborator list updates
- [ ] Collaboration: Add backend comment data updates
- [ ] Backup: Add progress indicator
- [ ] Backup: Ensure recovery points load on tab switch
- [ ] Cloud Sync: Implement conflict modal population
- [ ] Cloud Sync: Implement offline queue display
- [ ] Designer: Ensure save callbacks always called

### Next Week (High Priority Medium)
- [ ] Analytics: Fix recent insights refresh
- [ ] Collaboration: Implement history loading
- [ ] Backup: Add restore progress
- [ ] Cloud Sync: Fix progress bar visibility
- [ ] Cloud Sync: Persist auto-sync setting
- [ ] Cloud Sync: Update storage stats
- [ ] Performance: Populate bottleneck list
- [ ] Project Browser: Add action feedback

---

## Testing Each Fix

After implementing each fix:
1. Clear browser cache
2. Test the specific scenario
3. Test related features don't break
4. Verify error handling works
5. Check mobile responsiveness

---

**Last Updated**: January 18, 2026
**Audit Status**: Complete - All systems analyzed
