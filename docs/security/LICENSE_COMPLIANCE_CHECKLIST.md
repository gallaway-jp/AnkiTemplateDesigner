# License Compliance Checklist

**Project**: Anki Template Designer  
**Last Updated**: December 28, 2025

Use this checklist to ensure ongoing license compliance.

---

## 📋 Core Requirements

### Project License
- [x] LICENSE file exists and is up to date
- [x] README.md mentions project license
- [x] License is appropriate for deployment model (MIT for Anki add-on)

### Documentation
- [x] THIRD_PARTY_LICENSES.md created
- [x] LICENSE_COMPLIANCE.md created
- [x] README.md includes third-party software section
- [x] Attribution requirements documented

### Dependencies
- [x] All runtime dependencies identified
- [x] All dev dependencies identified
- [x] License for each dependency documented
- [x] No conflicting licenses found

---

## ✅ Completed Items

### Documentation Files Created
- [x] `LICENSE` - MIT License (already existed)
- [x] `LICENSE_COMPLIANCE.md` - Comprehensive compliance analysis
- [x] `THIRD_PARTY_LICENSES.md` - Third-party attribution
- [x] `LICENSE_REVIEW_SUMMARY.md` - Executive summary
- [x] `LICENSE_COMPLIANCE_CHECKLIST.md` - This file

### README Updates
- [x] Third-Party Software section added
- [x] License section expanded
- [x] License compatibility note added
- [x] Attribution section added
- [x] Contributing guidelines with license policy

### Analysis Completed
- [x] All dependencies reviewed
- [x] License compatibility verified
- [x] GPL/AGPL implications understood
- [x] Deployment model documented
- [x] Attribution requirements identified

---

## 🔄 Ongoing Compliance

### When Adding New Dependencies

- [ ] Check the package license
  ```powershell
  pip show <package-name>
  ```

- [ ] Verify license compatibility
  - Is it compatible with MIT?
  - Is it compatible with GPL v3/AGPL v3?
  - Is it runtime or dev-only?

- [ ] Update THIRD_PARTY_LICENSES.md
  - Add package name, version, license
  - Include copyright holder
  - Add homepage/repository URL
  - Note purpose/usage

- [ ] Update summary table in THIRD_PARTY_LICENSES.md

- [ ] Update README.md if major dependency

### Before Each Release

- [ ] Verify all dependencies are current
- [ ] Update version numbers in documentation
- [ ] Review LICENSE_COMPLIANCE.md for any changes
- [ ] Ensure THIRD_PARTY_LICENSES.md is complete
- [ ] Check for deprecated or removed dependencies
- [ ] Run license checker tool:
  ```powershell
  pip-licenses --format=markdown
  ```

### Quarterly Review

- [ ] Review all dependency licenses for changes
- [ ] Check for new license requirements
- [ ] Update documentation as needed
- [ ] Verify compliance with current model
- [ ] Review for security vulnerabilities in licenses

---

## ⚠️ Red Flags to Watch For

### Problematic Licenses for Runtime

**Never use these in runtime dependencies**:
- [ ] No proprietary/closed-source licenses
- [ ] No "non-commercial use only" licenses
- [ ] No licenses with field-of-use restrictions
- [ ] No unlicensed code

**Requires careful consideration**:
- [ ] Additional GPL v2/v3 dependencies (already have PyQt6)
- [ ] AGPL v3 dependencies (already have Anki)
- [ ] Licenses with patent clauses that conflict
- [ ] "Commons Clause" or similar restrictions

### License Changes

**Be alert for**:
- [ ] Dependencies changing licenses
- [ ] New license terms in updates
- [ ] Dual-licensed packages changing options
- [ ] License added to previously unlicensed code

---

## 🎯 Best Practices

### Source Code Headers (Optional but Recommended)

Add to each Python file:
```python
# Anki Template Designer
# Copyright (c) 2025 Anki Template Designer Contributors
# Licensed under the MIT License
# See LICENSE file in the project root for full license information
```

### Distribution Checklist

When distributing (AnkiWeb, GitHub Release, etc.):
- [ ] Include LICENSE file
- [ ] Include THIRD_PARTY_LICENSES.md
- [ ] Include attribution in README
- [ ] Include license in any "About" dialog
- [ ] Ensure all required notices are present

### Documentation Checklist

- [ ] All documentation files are up to date
- [ ] License information is accurate
- [ ] Links to license texts are working
- [ ] Copyright years are current
- [ ] Contact information is correct

---

## 🚀 Advanced Compliance (Optional)

### Automated Checks

Consider adding to CI/CD pipeline:
```yaml
# Example GitHub Actions workflow
- name: License Check
  run: |
    pip install pip-licenses
    pip-licenses --fail-on="GPL-2.0;AGPL-3.0" --format=json
```

### Tools to Consider

- [ ] **pip-licenses**: Generate license reports
  ```powershell
  pip install pip-licenses
  pip-licenses --format=markdown > licenses.md
  ```

- [ ] **licensee**: Detect licenses automatically
  ```powershell
  # Install via gem (Ruby)
  gem install licensee
  licensee detect
  ```

- [ ] **FOSSA**: Automated license scanning
  - Commercial tool with free tier
  - GitHub integration available

- [ ] **Black Duck**: Enterprise license management
  - For commercial/enterprise use

### License Badges (Optional)

Add to README.md:
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## 📚 Reference Resources

### License Information
- **SPDX License List**: https://spdx.org/licenses/
- **Choose a License**: https://choosealicense.com/
- **OSI Approved Licenses**: https://opensource.org/licenses/
- **GNU License List**: https://www.gnu.org/licenses/license-list.html

### Compatibility Guides
- **GPL Compatibility**: https://www.gnu.org/licenses/gpl-faq.html
- **MIT License**: https://opensource.org/licenses/MIT
- **Apache 2.0**: https://www.apache.org/licenses/LICENSE-2.0

### Python Specific
- **PyPI Classifiers**: https://pypi.org/classifiers/
- **Python Packaging**: https://packaging.python.org/

---

## 🆘 When to Seek Legal Advice

Consult with legal counsel if:
- [ ] Planning commercial distribution
- [ ] Changing deployment model (e.g., Anki add-on → standalone)
- [ ] Receiving license violation claims
- [ ] Unsure about license compatibility
- [ ] Considering patent-related licenses
- [ ] Dealing with contributor agreements
- [ ] Preparing for acquisition or investment

---

## 📞 Contacts

### For License Questions
- Review [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)
- Check [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)
- Consult project maintainer
- Seek legal counsel for complex issues

### For Anki Add-on Specific
- **Anki Forums**: https://forums.ankiweb.net/
- **Anki Development**: https://github.com/ankitects/anki
- **AnkiWeb**: https://ankiweb.net/

---

## 🔄 Update Schedule

| Item | Frequency | Next Due |
|------|-----------|----------|
| Dependency review | On changes | As needed |
| Documentation update | Quarterly | March 2026 |
| Full compliance audit | Annually | December 2026 |
| License checklist review | On each release | Next release |

---

## ✅ Current Status

**Overall Compliance**: ✅ **EXCELLENT**

**Last Full Review**: December 28, 2025  
**Reviewed By**: License Compliance Analysis  
**Status**: All requirements met  
**Grade**: A- (Excellent)

**Next Actions**: None required - maintain current compliance

---

## 📝 Notes

### Project-Specific Considerations

1. **Anki Add-on Model**: This project is designed as an Anki add-on
   - ✅ Compatible with Anki AGPL v3
   - ✅ Compatible with PyQt6 GPL v3
   - ✅ MIT license is appropriate

2. **Development Dependencies**: All dev tools are properly licensed
   - Not distributed with application
   - Can use any license
   - No impact on project licensing

3. **Attribution**: All required attributions documented
   - PyQt6 (GPL v3)
   - Anki (AGPL v3)
   - Development tools (various)

### Important Reminders

- ✅ Keep documentation updated
- ✅ Review licenses when adding dependencies
- ✅ Maintain compliance checklist
- ✅ Update before each release
- ⚠️ Consult legal for commercial use

---

**Compliance Status**: ✅ **CURRENT**  
**Documentation Status**: ✅ **COMPLETE**  
**Next Review**: On dependency changes or next major release

