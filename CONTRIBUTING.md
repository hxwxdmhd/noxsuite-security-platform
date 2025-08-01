# Contributing to NoxSuite Security Platform

Thank you for your interest in contributing to NoxSuite! We welcome contributions from the community and are pleased to have you join us.

## 🔒 Security First

NoxSuite follows **zero-compromise security principles**. All contributions must maintain or enhance the security posture of the platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Security Guidelines](#security-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.12.10+
- MariaDB 10.6+
- Docker & Docker Compose
- Git
- Basic understanding of security principles

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/noxsuite-security-platform.git
   cd noxsuite-security-platform
   ```

2. **Create Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set Up MariaDB**
   ```bash
   docker-compose -f docker-compose.mariadb.yml up -d
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env.development
   # Edit .env.development with your settings
   ```

5. **Initialize Database**
   ```bash
   python setup_database.py
   python create_admin_user.py
   ```

6. **Run Tests**
   ```bash
   python -m pytest tests/
   python testsprite_e2e.py --full
   ```

## Development Process

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/feature-name` - Feature development
- `bugfix/bug-description` - Bug fixes
- `security/vuln-fix` - Security patches

### Workflow

1. **Create Issue** - Describe the problem or enhancement
2. **Create Branch** - From appropriate base branch
3. **Develop** - Write code following our standards
4. **Test** - Ensure all tests pass
5. **Security Review** - Run security audits
6. **Pull Request** - Submit for review
7. **Review & Merge** - Address feedback and merge

## Security Guidelines

### 🔐 Authentication & Authorization

- **Never** hardcode credentials or secrets
- **Always** use Argon2 for password hashing
- **Implement** proper session management
- **Validate** all inputs and outputs
- **Follow** principle of least privilege

### 🛡️ Secure Coding Practices

```python
# ✅ Good - Parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ Bad - SQL injection risk
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Good - Input validation
if not re.match(r'^[a-zA-Z0-9_]+$', username):
    raise ValueError("Invalid username format")

# ❌ Bad - No validation
user = User(username=request.form['username'])
```

### 🔍 Security Checklist

Before submitting any code:

- [ ] No hardcoded secrets or credentials
- [ ] All inputs properly validated and sanitized
- [ ] Database queries use parameterized statements
- [ ] Proper error handling (no sensitive info leakage)
- [ ] Authentication and authorization checks in place
- [ ] Audit logging for security-relevant actions
- [ ] Security tests included

## Testing Requirements

### Minimum Coverage

- **Unit Tests**: 90% code coverage minimum
- **Integration Tests**: All API endpoints
- **Security Tests**: Authentication, authorization, input validation
- **E2E Tests**: Critical user workflows

### TestSprite Integration

All new features must include TestSprite tests:

```python
# Example TestSprite test
def test_mfa_authentication():
    """Test MFA authentication flow"""
    # Register test with TestSprite
    test_id = testsprite.register_test(
        name="MFA Authentication",
        category="security",
        priority="high"
    )
    
    # Test implementation
    result = authenticate_with_mfa(user, totp_code)
    
    # Report results
    testsprite.report_result(test_id, result.success, result.details)
```

### Running Tests

```bash
# Unit tests
python -m pytest tests/ -v --cov=. --cov-report=html

# Security tests
python -m pytest tests/security/ -v

# Integration tests
python testsprite_e2e.py --full

# Security audit
python noxsuite_comprehensive_audit.py
```

## Pull Request Process

### Before Submitting

1. **Rebase** your branch on the latest target branch
2. **Run** all tests and ensure they pass
3. **Execute** security audit tools
4. **Update** documentation if needed
5. **Add** appropriate tests for new functionality

### PR Requirements

- **Clear title** describing the change
- **Detailed description** of what and why
- **Link** to related issues
- **Screenshots** for UI changes
- **Security impact** assessment
- **Breaking changes** documented

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Security enhancement
- [ ] Documentation update
- [ ] Refactoring

## Security Impact
Describe any security implications of this change.

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs tests
2. **Security Review** - Automated security scanning
3. **Code Review** - At least one maintainer review
4. **Security Approval** - For security-related changes
5. **Final Testing** - Manual verification if needed

## Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Security Email** - security@noxsuite.local (for vulnerabilities)

### Getting Help

- Check existing issues and documentation first
- Provide clear, detailed information when asking questions
- Include relevant code, error messages, and environment details
- Be patient and respectful with maintainers and other contributors

### Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Security advisories for security improvements

## Development Standards

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **Comments**: Clear, concise, explain the "why"
- **Naming**: Descriptive variable and function names
- **Imports**: Organized and minimal

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

Examples:
```
feat(auth): add TOTP-based MFA support
fix(api): resolve SQL injection in user search
security(rbac): implement role-based access control
docs(readme): update installation instructions
```

### Documentation

- **API changes** require documentation updates
- **New features** need user guides
- **Security features** require security documentation
- **Code comments** for complex business logic

## License

By contributing to NoxSuite Security Platform, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to NoxSuite Security Platform! Together, we're building a more secure future. 🔒
