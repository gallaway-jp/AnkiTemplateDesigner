# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Anki Template Designer, please report it responsibly:

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email security reports to: [your-email@example.com]

Include in your report:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

We will acknowledge receipt within 48 hours and aim to provide a fix within 7 days for critical issues.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Features

### Input Validation
- All field names are validated (alphanumeric, underscore, hyphen, space only)
- Maximum field name length: 100 characters
- Maximum template size: 1MB
- Maximum CSS size: 500KB
- Maximum components per template: 1000

### XSS Protection
- HTML sanitization on all user inputs
- Dangerous HTML tags blocked: `<script>`, `<iframe>`, `<object>`, `<embed>`, etc.
- Event handlers (`onclick`, `onerror`, etc.) are stripped
- Field names are HTML-escaped before rendering
- Content Security Policy (CSP) enabled in preview

### CSS Injection Protection
- Dangerous CSS properties blocked: `expression()`, `behavior`, `-moz-binding`
- `@import` statements removed
- `javascript:` and `data:` URLs in CSS blocked
- CSS size limits enforced

### Content Security Policy
Preview windows have the following CSP settings:
- JavaScript disabled
- No remote content access
- No file system access
- No insecure content

### Security Logging
All security events are logged to help detect potential attacks:
- Template validation failures
- Dangerous HTML/CSS detection
- Size limit violations
- Invalid field names

## Security Best Practices

### For Users
1. **Don't import templates from untrusted sources**
2. **Review template HTML before importing**
3. **Keep the add-on updated**
4. **Report suspicious behavior**

### For Developers
1. **Always sanitize user inputs**
2. **Use HTML escaping for all dynamic content**
3. **Validate all data before processing**
4. **Keep dependencies updated**
5. **Run security tests before releases**

## Dependency Management

### Automated Scanning
```bash
# Install security tools
pip install safety pip-audit bandit

# Check for known vulnerabilities
safety check
pip-audit

# Run security linter
bandit -r ui/ utils/ -f json -o security_report.json
```

### Update Policy
- Dependencies are reviewed quarterly
- Critical security updates applied within 48 hours
- All dependencies pinned to specific versions

## Security Testing

### Before Each Release
1. Run full security test suite
2. Manual XSS testing with OWASP payloads
3. CSS injection testing
4. Resource exhaustion testing
5. Dependency vulnerability scan

### Test Commands
```bash
# Run security-focused tests
pytest tests/security/ -v

# Run with coverage
pytest tests/ --cov=ui --cov=utils --cov-report=html
```

## Incident Response

### In Case of Security Breach
1. Disable affected functionality immediately
2. Notify users via GitHub Security Advisory
3. Release patched version within 24-48 hours
4. Document incident in CHANGELOG
5. Review and improve security measures

## Security Changelog

### Version 0.1.0 (2025-01-XX)
- ✅ Implemented HTML sanitization
- ✅ Added input validation for field names
- ✅ Enabled Content Security Policy in preview
- ✅ Added CSS injection protection
- ✅ Implemented resource limits
- ✅ Added security logging
- ✅ Added debouncing to prevent DoS

## Contact

For security concerns: [your-email@example.com]
For general questions: [GitHub Issues](https://github.com/yourusername/anki-template-designer/issues)

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who help improve the security of this project.

---

**Last Updated:** December 28, 2025
