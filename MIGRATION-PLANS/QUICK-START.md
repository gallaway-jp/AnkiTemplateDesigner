# Migration Quick Start Guide

## Getting Started

This guide will help you begin the migration process. Follow these steps in order.

---

## Before You Begin

### 1. Create a Backup

```bash
git add -A
git commit -m "Backup before migration"
git tag migration-backup
git push origin migration-backup
```

### 2. Understand the Goal

We are:
- Creating a new clean addon based on `test_addon_minimal`
- Implementing all features from ISSUE-54 through ISSUE-59
- Removing all legacy code when complete
- Ensuring each step is tested before proceeding

### 3. Time Estimate

| Phase | Estimated Time |
|-------|---------------|
| Phase A: Foundation (Plans 01-05) | 4-6 hours |
| Phase B: Core Services (Plans 06-12) | 8-12 hours |
| Phase C: Advanced Features (Plans 13-20) | 16-24 hours |
| Phase D: Integration & Testing (Plans 21-25) | 8-12 hours |
| Phase E: Cleanup & Finalization (Plans 26-30) | 4-6 hours |
| **Total** | **40-60 hours** |

---

## How to Use the Plan Files

### Step-by-Step Process

1. **Read the plan file completely** before starting
2. **Implement each step** in the order specified
3. **Run the quality checks** after each step
4. **Run the automated tests** 
5. **Test manually in Anki**
6. **Document any issues** in the Notes section
7. **Mark checkboxes** as you complete items
8. **Only proceed** when all tests pass

### Example Workflow

```
1. Open MIGRATION-PLANS/01-FOUNDATION-SETUP.md
2. Read entire document
3. Complete Step 1.1
4. Run tests for Step 1.1
5. Complete Step 1.2
6. Run tests for Step 1.2
... continue through all steps ...
7. Complete User Testing Checklist
8. Move to 02-CORE-ADDON-ENTRY.md
```

---

## Directory Structure

After migration, the project will have this structure:

```
AnkiTemplateDesigner/
├── anki_template_designer/        # New clean addon (this is the output)
│   ├── __init__.py
│   ├── manifest.json
│   ├── config.json
│   ├── meta.json
│   ├── core/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── designer_dialog.py
│   │   └── webview_bridge.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── template_service.py
│   │   ├── undo_redo_manager.py
│   │   ├── performance_optimizer.py
│   │   └── ...
│   ├── utils/
│   │   └── __init__.py
│   ├── web/
│   │   └── index.html
│   └── tests/
│       └── ...
├── MIGRATION-PLANS/               # These plan files
├── README.md
├── CHANGELOG.md
├── LICENSE
└── ... (other docs)
```

---

## Testing Protocol

### After Each Step

1. **Unit Tests**
   ```bash
   python -m pytest anki_template_designer/tests/ -v
   ```

2. **Import Check**
   ```bash
   python -c "from anki_template_designer import *"
   ```

3. **Manual Test in Anki**
   - Copy addon to Anki addons folder
   - Restart Anki
   - Test the feature you just implemented
   - Check console for errors

### If Tests Fail

1. Stop immediately
2. Read the error message carefully
3. Fix the issue
4. Re-run tests
5. Continue only when passing

---

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**: 
- Check `__init__.py` files exist
- Check relative import syntax (use `.` for same package)
- Verify directory structure

### Qt Import Errors

**Problem**: Qt imports fail outside Anki

**Solution**:
- Use try/except for Anki imports
- Provide PyQt6 fallback for testing

### Path Issues

**Problem**: File not found errors

**Solution**:
- Use `os.path.dirname(__file__)` for relative paths
- Avoid hardcoded paths
- Use forward slashes or `os.path.join`

---

## Rollback Procedure

If something goes wrong:

```bash
# Return to backup
git checkout migration-backup

# Or reset current changes
git reset --hard HEAD
git clean -fd
```

---

## Support

If you encounter issues:
1. Check the Notes/Issues section in the plan file
2. Review error messages carefully
3. Search existing issues
4. Create a new issue with:
   - Which plan step you're on
   - The error message
   - Steps to reproduce

---

## Begin Migration

**Start with: [01-FOUNDATION-SETUP.md](01-FOUNDATION-SETUP.md)**

Good luck! Take it one step at a time, test thoroughly, and you'll have a clean, maintainable codebase.
