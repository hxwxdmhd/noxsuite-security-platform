# 🚀 NoxSuite Development Quick Start Guide

## 🎯 Overview
This guide helps you get started with the enhanced NoxSuite Security Platform repository in minutes, not hours.

## ⚡ Quick Start (5 minutes)

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/hxwxdmhd/noxsuite-security-platform.git
cd noxsuite-security-platform

# Run automated setup
python scripts/setup-dev.py

# Install pre-commit hooks
pre-commit install
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.template .env

# Edit configuration (required)
nano .env  # or your preferred editor
```

### 3. Start Development
```bash
# Run tests
pytest

# Check code quality
pre-commit run --all-files

# Start development server
python run.py
```

## 🛠️ Development Workflow

### Daily Development
```bash
# Before coding
git pull origin main
pre-commit run --all-files

# During coding - automatic formatting on commit
git add .
git commit -m "Your commit message"  # Pre-commit hooks run automatically

# Before pushing
pytest  # Run tests
git push
```

### Code Quality Tools
```bash
# Format code
black .

# Sort imports  
isort .

# Lint code
flake8 .

# Type checking
mypy src/

# Security scan
bandit -r .
```

## 🔧 Enhanced Features

### Automated CI/CD
- ✅ **GitHub Actions**: Automated testing on every push
- ✅ **Multi-environment**: Testing with Python 3.11 & 3.12
- ✅ **Security scanning**: Automated vulnerability detection
- ✅ **Docker integration**: Automated container builds
- ✅ **Performance testing**: Automated benchmarks

### Code Quality
- ✅ **Pre-commit hooks**: Automatic formatting and linting
- ✅ **Black formatting**: Consistent code style
- ✅ **Import sorting**: Organized imports with isort
- ✅ **Type checking**: MyPy integration
- ✅ **Security linting**: Bandit security scanning

### Project Structure
```
noxsuite-security-platform/
├── src/noxsuite/          # Main package code
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   └── development/      # Developer docs
├── scripts/               # Development scripts
│   └── automation/       # Automation tools
├── config/                # Configuration
│   └── environments/     # Environment configs
└── .github/workflows/     # CI/CD pipelines
```

## 🐳 Docker Development

### Quick Docker Setup
```bash
# Build development image
docker build -t noxsuite-dev .

# Run with docker-compose
docker-compose up -d

# Development with hot reload
docker-compose -f docker-compose.dev.yml up
```

### Database Setup
```bash
# Start MariaDB
docker-compose -f docker-compose.mariadb.yml up -d

# Initialize database
python setup_database.py

# Create admin user
python create_admin_user.py
```

## 🧪 Testing

### Test Categories
```bash
# Unit tests
pytest tests/unit/

# Integration tests  
pytest tests/integration/

# Security tests
pytest -m security

# Performance tests
pytest -m performance
```

### Test Coverage
```bash
# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🔒 Security Development

### Security Checks
```bash
# Dependency vulnerabilities
safety check

# Code security scan
bandit -r .

# Secrets detection
detect-secrets scan
```

### Security Best Practices
- ✅ Use environment variables for secrets
- ✅ Never commit credentials
- ✅ Run security scans before commits
- ✅ Follow OWASP guidelines
- ✅ Use MFA for production access

## 📊 Monitoring & Debugging

### Development Monitoring
```bash
# Check application health
curl http://localhost:8000/health

# View logs
docker-compose logs -f

# Monitor performance
python -m cProfile your_script.py
```

### Debugging Tools
- **FastAPI docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics (if enabled)

## 🚀 Deployment

### Staging Deployment
```bash
# Deploy to staging (automatic via GitHub Actions)
git push origin develop
```

### Production Deployment  
```bash
# Deploy to production (automatic via GitHub Actions)
git push origin main
```

### Manual Deployment
```bash
# Build production image
docker build -f Dockerfile.production -t noxsuite-prod .

# Deploy with docker-compose
docker-compose -f docker-compose.production.yml up -d
```

## 🛟 Troubleshooting

### Common Issues

#### Environment Setup
```bash
# Python version issues
pyenv install 3.12.0
pyenv global 3.12.0

# Dependency conflicts
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Database Connection
```bash
# Check MariaDB status
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
python setup_database.py
```

#### Pre-commit Issues
```bash
# Update pre-commit
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall hooks
pre-commit install --install-hooks
```

## 📚 Additional Resources

### Documentation
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Security Guidelines](SECURITY.md)
- [Contributing Guide](CONTRIBUTING.md)

### Tools & Links
- **GitHub Actions**: [Repository Actions](https://github.com/hxwxdmhd/noxsuite-security-platform/actions)
- **Code Quality**: [Pre-commit](https://pre-commit.com/)
- **Testing**: [pytest](https://pytest.org/)
- **Docker**: [Docker Compose](https://docs.docker.com/compose/)

## 🎯 Getting Help

### Support Channels
- **Issues**: [GitHub Issues](https://github.com/hxwxdmhd/noxsuite-security-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hxwxdmhd/noxsuite-security-platform/discussions)
- **Security**: security@noxsuite.local

### Development Team
- **Lead**: @hxwxdmhd
- **AI Assistant**: @copilot
- **Community**: [Contributors](https://github.com/hxwxdmhd/noxsuite-security-platform/contributors)

---

**🚀 Happy Coding with NoxSuite Security Platform!**

*This guide is automatically updated with repository enhancements.*