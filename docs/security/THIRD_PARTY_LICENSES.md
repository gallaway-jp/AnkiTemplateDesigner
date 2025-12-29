# Third-Party Licenses

This document lists all third-party software used by Anki Template Designer and their respective licenses.

**Last Updated**: December 28, 2025

---

## Runtime Dependencies

These libraries are required to run the application.

### PyQt6
- **Version**: 6.10.1
- **License**: GPL v3 / Commercial Dual License
- **Copyright**: Copyright (c) Riverbank Computing Limited
- **Homepage**: https://www.riverbankcomputing.com/software/pyqt/
- **Purpose**: Qt bindings for Python - GUI framework
- **License Text**: https://www.gnu.org/licenses/gpl-3.0.html

**Note**: PyQt6 is dual-licensed. For open-source projects, GPL v3 applies. This is compatible with Anki's AGPL v3 license when used as an add-on.

### PyQt6-WebEngine
- **Version**: 6.10.0
- **License**: GPL v3 / Commercial Dual License
- **Copyright**: Copyright (c) Riverbank Computing Limited
- **Homepage**: https://www.riverbankcomputing.com/software/pyqt/
- **Purpose**: Web rendering engine for PyQt6
- **License Text**: https://www.gnu.org/licenses/gpl-3.0.html

### Anki
- **Version**: 2.x
- **License**: AGPL v3 or later
- **Copyright**: Copyright (c) Ankitects Pty Ltd and contributors
- **Homepage**: https://apps.ankiweb.net/
- **Repository**: https://github.com/ankitects/anki
- **Purpose**: Spaced repetition software platform
- **License Text**: https://www.gnu.org/licenses/agpl-3.0.html

**Note**: Anki is the host application for this add-on. AGPL v3 is a strong copyleft license that requires source code availability for network services.

---

## Development & Testing Dependencies

These libraries are only used during development and testing, not distributed with the application.

### Testing Framework

#### pytest
- **Version**: 9.0.2
- **License**: MIT License
- **Copyright**: Copyright (c) 2004 Holger Krekel and others
- **Homepage**: https://pytest.org/
- **Repository**: https://github.com/pytest-dev/pytest
- **Purpose**: Testing framework

**License Text**:
```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

#### pytest-qt
- **Version**: 4.5.0
- **License**: MIT License
- **Copyright**: Copyright (c) pytest-qt contributors
- **Repository**: https://github.com/pytest-dev/pytest-qt
- **Purpose**: pytest plugin for Qt/PyQt testing

#### pytest-cov
- **Version**: 7.0.0
- **License**: MIT License
- **Copyright**: Copyright (c) pytest-cov contributors
- **Repository**: https://github.com/pytest-dev/pytest-cov
- **Purpose**: Coverage plugin for pytest

#### pytest-mock
- **Version**: 3.15.1
- **License**: MIT License
- **Copyright**: Copyright (c) pytest-mock contributors
- **Repository**: https://github.com/pytest-dev/pytest-mock
- **Purpose**: Mocking/fixtures plugin for pytest

#### pytest-benchmark
- **Version**: 5.2.3
- **License**: BSD 2-Clause License
- **Copyright**: Copyright (c) Ionel Cristian Mărieș
- **Repository**: https://github.com/ionelmc/pytest-benchmark
- **Purpose**: Benchmarking plugin for pytest

**BSD 2-Clause License**:
```
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
```

#### hypothesis
- **Version**: 6.148.8
- **License**: Mozilla Public License 2.0 (MPL-2.0)
- **Copyright**: Copyright (c) David R. MacIver and Zac Hatfield-Dodds
- **Homepage**: https://hypothesis.readthedocs.io/
- **Repository**: https://github.com/HypothesisWorks/hypothesis
- **Purpose**: Property-based testing framework

### Code Coverage

#### coverage
- **Version**: 7.6.0
- **License**: Apache License 2.0
- **Copyright**: Copyright (c) Ned Batchelder
- **Homepage**: https://coverage.readthedocs.io/
- **Repository**: https://github.com/nedbat/coveragepy
- **Purpose**: Code coverage measurement

**Apache License 2.0**:
```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Code Quality Tools

#### pylint
- **Version**: 3.x
- **License**: GPL v2
- **Copyright**: Copyright (c) Logilab, PyCQA
- **Homepage**: https://pylint.pycqa.org/
- **Repository**: https://github.com/pylint-dev/pylint
- **Purpose**: Python code static analyzer

**Note**: GPL v2 for development tool only, not distributed with application.

#### black
- **Version**: 23.x
- **License**: MIT License
- **Copyright**: Copyright (c) 2018 Łukasz Langa
- **Homepage**: https://black.readthedocs.io/
- **Repository**: https://github.com/psf/black
- **Purpose**: Python code formatter

#### mypy
- **Version**: 1.x
- **License**: MIT License
- **Copyright**: Copyright (c) Jukka Lehtosalo and contributors
- **Homepage**: http://www.mypy-lang.org/
- **Repository**: https://github.com/python/mypy
- **Purpose**: Static type checker for Python

#### flake8
- **Version**: 6.x
- **License**: MIT License
- **Copyright**: Copyright (c) Tarek Ziade, Ian Stapleton Cordasco
- **Repository**: https://github.com/PyCQA/flake8
- **Purpose**: Python linting tool

### Security Tools

#### bandit
- **Version**: 1.7.x
- **License**: Apache License 2.0
- **Copyright**: Copyright (c) PyCQA
- **Homepage**: https://bandit.readthedocs.io/
- **Repository**: https://github.com/PyCQA/bandit
- **Purpose**: Security issue finder for Python

#### safety
- **Version**: 2.3.x
- **License**: MIT License
- **Copyright**: Copyright (c) Safety CLI developers
- **Homepage**: https://safetycli.com/
- **Repository**: https://github.com/pyupio/safety
- **Purpose**: Checks dependencies for known security vulnerabilities

#### pip-audit
- **Version**: 2.6.x
- **License**: Apache License 2.0
- **Copyright**: Copyright (c) Trail of Bits
- **Homepage**: https://pypi.org/project/pip-audit/
- **Repository**: https://github.com/pypa/pip-audit
- **Purpose**: Audits Python environments for known vulnerabilities

---

## Transitive Dependencies

The following are indirect dependencies pulled in by the packages listed above:

### From PyQt6
- **Qt6** (LGPL v3 / Commercial) - Core Qt framework
- **PyQt6-sip** (GPL v3 / Commercial) - SIP binding generator
- **PyQt6-Qt6** (LGPL v3 / Commercial) - Qt binaries

### From pytest and plugins
- **pluggy** (MIT) - Plugin management
- **iniconfig** (MIT) - INI file parser
- **packaging** (Apache 2.0 / BSD) - Package version handling
- **attrs** (MIT) - Classes without boilerplate
- **exceptiongroup** (MIT) - Exception groups backport

### From coverage
- **tomli** (MIT) - TOML parser

### From testing tools
- **sortedcontainers** (Apache 2.0) - Sorted collections
- **colorama** (BSD) - Cross-platform colored terminal text

---

## License Summary

| License | Count | Runtime | Dev Only | Compatible with MIT |
|---------|-------|---------|----------|---------------------|
| MIT | 15+ | Some | Most | ✅ Yes |
| GPL v3 | 2 | Yes | Some | ⚠️ As add-on only |
| AGPL v3 | 1 | Yes | No | ⚠️ As add-on only |
| Apache 2.0 | 5+ | No | Yes | ✅ Yes |
| BSD 2/3-Clause | 3+ | No | Yes | ✅ Yes |
| MPL-2.0 | 1 | No | Yes | ✅ Yes (file-level) |
| LGPL v3 | ~5 | Yes (transitive) | No | 🟡 With dynamic linking |

---

## License Compatibility Notes

### For Anki Add-on Distribution (Current Model)

✅ **COMPATIBLE**: All licenses are compatible when distributed as an Anki add-on:
- PyQt6 (GPL v3) ← Compatible with Anki's AGPL v3
- Anki (AGPL v3) ← Host application
- Development tools ← Not distributed, any license acceptable

### For Standalone Distribution (Not Current Model)

⚠️ **WOULD REQUIRE CHANGES**:
- PyQt6 GPL v3 would require entire project to be GPL
- Would conflict with MIT license
- Options: Purchase PyQt6 commercial license, or switch to PySide6 (LGPL)

---

## Attribution Requirements

When distributing this software, the following attributions must be included:

### Mandatory (GPL Requirements)

**PyQt6**:
```
This software uses PyQt6, which is licensed under the GNU General Public License v3.

PyQt6 is Copyright (c) Riverbank Computing Limited.
https://www.riverbankcomputing.com/software/pyqt/

The GPL v3 license text can be found at:
https://www.gnu.org/licenses/gpl-3.0.html
```

**Anki**:
```
This is an add-on for Anki, licensed under the GNU Affero General Public License v3.

Anki is Copyright (c) Ankitects Pty Ltd and contributors.
https://apps.ankiweb.net/

The AGPL v3 license text can be found at:
https://www.gnu.org/licenses/agpl-3.0.html
```

### Recommended (Good Practice)

Include a notice in your README.md and About dialog:

```markdown
## Third-Party Software

This software is built upon the following open-source projects:

- **Anki** (AGPL v3) - Spaced repetition software
- **PyQt6** (GPL v3) - Python bindings for Qt
- **pytest** (MIT) - Testing framework
- [See THIRD_PARTY_LICENSES.md for complete list]
```

---

## How to Update This Document

When adding new dependencies:

1. **Check the license**:
   ```powershell
   pip show <package-name>
   ```

2. **Verify compatibility** with MIT and GPL v3/AGPL v3

3. **Add to appropriate section** (Runtime vs Development)

4. **Include**:
   - Package name and version
   - License name and SPDX ID
   - Copyright holder
   - Homepage/repository URL
   - Purpose/what it's used for
   - License text or link

5. **Update summary table**

---

## Resources

### License Information
- **SPDX License List**: https://spdx.org/licenses/
- **Choose a License**: https://choosealicense.com/
- **OSI Approved Licenses**: https://opensource.org/licenses/

### Compatibility Guides
- **GPL Compatibility**: https://www.gnu.org/licenses/gpl-faq.html#AllCompatibility
- **MIT License**: https://opensource.org/licenses/MIT
- **AGPL v3**: https://www.gnu.org/licenses/agpl-3.0.html

### Tools
- **pip-licenses**: `pip install pip-licenses` - Generate license list
- **licensee**: GitHub's license detection tool
- **FOSSA**: Automated license compliance

---

## Contact

For questions about licensing:
- Review [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md)
- Check project LICENSE file
- Consult with legal counsel for commercial use

---

**Document Maintenance**:
- Update when adding/removing dependencies
- Review quarterly for license changes
- Verify before each release

**Version**: 1.0  
**Last Updated**: December 28, 2025
