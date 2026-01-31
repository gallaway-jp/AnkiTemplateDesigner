# Plan 26: Legacy Python Code Removal

## Objective
Safely remove all legacy Python code after verifying the new implementation is complete and functional.

---

## Prerequisites
- [ ] Plans 01-25 completed and tested
- [ ] All features implemented and tested
- [ ] Full backup of codebase (git commit)

---

## Critical Warning

⚠️ **This step is IRREVERSIBLE without git recovery.**

Before proceeding:
1. Ensure all tests pass
2. Verify addon works in Anki
3. Create a git tag: `git tag pre-cleanup-backup`
4. Push the tag: `git push origin pre-cleanup-backup`

---

## Step 26.1: Audit Legacy Code Usage

### Task
Verify no legacy code is still being used.

### Checklist

#### Python Modules to Remove

Review each module and verify no imports remain:

| Module | Path | New Location | Verified |
|--------|------|--------------|----------|
| Old __init__.py | `/__init__.py` | `anki_template_designer/__init__.py` | [ ] |
| Old core | `/core/` | `anki_template_designer/core/` | [ ] |
| Old gui | `/gui/` | `anki_template_designer/gui/` | [ ] |
| Old services | `/services/` | `anki_template_designer/services/` | [ ] |
| Old hooks | `/hooks/` | Integrated or removed | [ ] |
| Old utils | `/utils/` | `anki_template_designer/utils/` | [ ] |
| Old renderers | `/renderers/` | Integrated or removed | [ ] |
| Old tests | `/tests/` | `anki_template_designer/tests/` | [ ] |
| Old testsuite | `/testsuite/` | `anki_template_designer/tests/` | [ ] |

### Quality Checks

#### Security
- [ ] No hardcoded credentials left
- [ ] No sensitive data in removed files

#### Performance
- [ ] N/A (removal step)

#### Best Practices
- [ ] All removed code is version controlled
- [ ] Git history preserved

#### Maintainability
- [ ] Clean directory structure after removal

#### Documentation
- [ ] Document what was removed

#### Testing
- [ ] All tests still pass after removal

#### Accessibility
- [ ] N/A

#### Scalability
- [ ] N/A

#### Compatibility
- [ ] Addon still works after removal

#### Error Handling
- [ ] N/A

#### Complexity
- [ ] Reduced by removal

#### Architecture
- [ ] Cleaner after removal

#### License
- [ ] N/A

#### Specification
- [ ] N/A

---

## Step 26.2: Remove Legacy Python Files

### Task
Execute the removal of legacy Python code.

### Pre-Removal Script

Run this script to verify what will be removed:

```powershell
# List all files to be removed
$filesToRemove = @(
    # Root Python files
    "template_designer.py",
    "install_addon.py",
    "launch_and_test.py",
    "setup.py",
    "run_ui_tests.py",
    "validate_phase5_integration.py",
    "validate_qt_fixes.py",
    
    # Root directories
    "core",
    "gui", 
    "hooks",
    "renderers",
    "services",
    "utils",
    "tests",
    "testsuite"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "Will remove: $file"
    } else {
        Write-Host "Not found: $file" -ForegroundColor Yellow
    }
}
```

### Removal Commands

```powershell
# Create backup branch
git checkout -b pre-cleanup-backup-branch
git push origin pre-cleanup-backup-branch
git checkout main

# Remove legacy Python directories
Remove-Item -Recurse -Force core -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force gui -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force hooks -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force renderers -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force services -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force utils -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force tests -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force testsuite -ErrorAction SilentlyContinue

# Remove legacy Python files at root
Remove-Item template_designer.py -ErrorAction SilentlyContinue
Remove-Item install_addon.py -ErrorAction SilentlyContinue
Remove-Item launch_and_test.py -ErrorAction SilentlyContinue
Remove-Item setup.py -ErrorAction SilentlyContinue
Remove-Item run_ui_tests.py -ErrorAction SilentlyContinue
Remove-Item validate_phase5_integration.py -ErrorAction SilentlyContinue
Remove-Item validate_qt_fixes.py -ErrorAction SilentlyContinue

# Remove old root __init__.py (if different from new)
# BE CAREFUL - verify this is the old one
# Remove-Item __init__.py -ErrorAction SilentlyContinue
```

### Post-Removal Verification

```powershell
# Verify new addon still exists
Test-Path anki_template_designer

# List remaining Python files
Get-ChildItem -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "anki_template_designer|\.venv|__pycache__|node_modules" }
```

---

## Step 26.3: Update Root Files

### Task
Update root configuration files to point to new addon.

### Files to Update

**pyproject.toml** (if present):
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "anki-template-designer"
version = "2.0.0"
description = "Visual template designer for Anki flashcards"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "[Your Name]", email = "[your@email.com]"}
]

[project.urls]
Homepage = "https://github.com/yourusername/AnkiTemplateDesigner"
Issues = "https://github.com/yourusername/AnkiTemplateDesigner/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["anki_template_designer*"]
```

**requirements.txt**:
```txt
# Production dependencies are bundled with Anki
# These are for development/testing only
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-qt>=4.2.0
```

---

## Step 26.4: Verify and Commit

### Verification Checklist

1. [ ] Run all tests:
   ```bash
   python -m pytest anki_template_designer/tests/ -v
   ```

2. [ ] Install in Anki:
   - Copy `anki_template_designer/` to Anki addons folder
   - Restart Anki
   - Open Template Designer from Tools menu
   - Verify all features work

3. [ ] Check for import errors:
   ```powershell
   python -c "from anki_template_designer import *"
   ```

4. [ ] Verify no broken references:
   ```powershell
   # Search for imports of removed modules
   Get-ChildItem -Recurse -Filter "*.py" -Path anki_template_designer | 
       Select-String -Pattern "from (core|gui|hooks|renderers|services|utils|tests) import" |
       Select-String -NotMatch "from \.core|from \.gui|from \.services|from \.utils"
   ```

### Git Commit

```bash
git add -A
git status

# Review changes carefully
git diff --cached --stat

# Commit
git commit -m "chore: Remove legacy Python code

- Removed old core/, gui/, hooks/, renderers/, services/, utils/ directories
- Removed old test directories (tests/, testsuite/)
- Removed old root-level Python scripts
- All functionality now in anki_template_designer/ package
- Preserved git history via backup branch

BREAKING CHANGE: All imports must now use anki_template_designer package"

git push origin main
```

---

## User Testing Checklist

### Post-Removal Testing

1. [ ] All unit tests pass
2. [ ] Addon loads in Anki without errors
3. [ ] Template Designer opens
4. [ ] Can create new template
5. [ ] Can save template
6. [ ] Can load template
7. [ ] All toolbar buttons functional
8. [ ] Properties panel works
9. [ ] Drag and drop works
10. [ ] No console errors

### Rollback Procedure (if needed)

If issues are discovered:

```bash
# Restore from backup branch
git checkout pre-cleanup-backup-branch
git checkout -b main-fixed
git push origin main-fixed

# Or restore from tag
git checkout pre-cleanup-backup
```

---

## Success Criteria

- [ ] All legacy Python code removed
- [ ] New addon fully functional
- [ ] All tests pass
- [ ] Git history preserved
- [ ] Documentation updated

---

## Next Step

After successful completion, proceed to [27-LEGACY-REMOVAL-WEB.md](27-LEGACY-REMOVAL-WEB.md).

---

## Notes/Issues

| Issue | Resolution | Date |
|-------|------------|------|
| | | |
