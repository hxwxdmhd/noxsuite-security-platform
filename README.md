# 🔒 NoxSuite Security Platform

**Production-ready security suite with MariaDB, MFA/RBAC authentication, TestSprite integration, and comprehensive audit framework**

[![Security Status](https://img.shields.io/badge/Security-Production%20Ready-green)](https://github.com/hxwxdmhd/noxsuite-security-platform)
[![Database](https://img.shields.io/badge/Database-MariaDB-blue)](https://mariadb.org/)
[![Authentication](https://img.shields.io/badge/Auth-MFA%2FRBAC-orange)](https://github.com/hxwxdmhd/noxsuite-security-platform)
[![Testing](https://img.shields.io/badge/Testing-TestSprite-purple)](https://github.com/hxwxdmhd/noxsuite-security-platform)
[![AI/ML](https://img.shields.io/badge/AI%2FML-Integrated-brightgreen)](https://github.com/hxwxdmhd/noxsuite-security-platform)

## 🚀 Overview

NoxSuite is a comprehensive security platform designed for enterprise-grade applications with zero-compromise security standards. Built with production readiness in mind, it features advanced authentication, real-time monitoring, automated security enforcement, and **state-of-the-art AI/ML capabilities** for intelligent threat detection and risk assessment.

## ✨ Key Features

### 🔐 **Advanced Authentication**
- **Multi-Factor Authentication (MFA)** with TOTP support
- **Role-Based Access Control (RBAC)** with granular permissions
- **Argon2 password hashing** for maximum security
- **Session management** with automatic timeout enforcement
- **Backup codes** for account recovery

### 🗄️ **MariaDB-First Architecture**
- **Production-grade database** with full ACID compliance
- **Automated migration tools** from legacy SQLite systems
- **Connection pooling** and optimization
- **Backup and disaster recovery** capabilities

### 🧪 **TestSprite Integration**
- **Automated test generation** and execution
- **End-to-end testing** for authentication workflows
- **Load testing** capabilities
- **95% target test coverage** enforcement

### 🤖 **AI/ML Security Intelligence**
- **TensorFlow & PyTorch** integration for neural network-based threat detection
- **Scikit-learn** powered classical ML algorithms for behavior analysis
- **XGBoost & LightGBM** for high-performance anomaly scoring
- **NLTK** for natural language processing of security logs
- **Real-time anomaly detection** on login patterns and system metrics
- **Predictive risk scoring** for users, sessions, and IP addresses
- **Automated threat intelligence extraction** from log data
- **H2O.ai AutoML** for continuous model improvement

### 🛡️ **Security Enforcement**
- **Skeptical Development Auditor** with continuous monitoring
- **Real-time vulnerability detection**
- **Automated penetration testing**
- **Comprehensive audit logging**

## 🏗️ Architecture

```
NoxSuite Security Platform
├── 🔧 Backend (FastAPI)
│   ├── Authentication & MFA
│   ├── RBAC Management
│   ├── API Endpoints
│   └── Security Middleware
├── 🗄️ Database (MariaDB)
│   ├── User Management
│   ├── Role Definitions
│   ├── Session Storage
│   └── Audit Logs
├── 🧪 Testing (TestSprite)
│   ├── Authentication Tests
│   ├── Security Tests
│   ├── Load Tests
│   └── E2E Scenarios
└── 🔒 Security Tools
    ├── Migration Enforcer
    ├── Audit Framework
    ├── Monitoring Engine
    └── Compliance Validator
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12.10+
- MariaDB 10.6+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/hxwxdmhd/noxsuite-security-platform.git
   cd noxsuite-security-platform
   ```

2. **Set up MariaDB with Docker**
   ```bash
   docker-compose -f docker-compose.mariadb.yml up -d
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python setup_database.py
   python create_admin_user.py
   ```

6. **Start the server**
   ```bash
   uvicorn noxsuite_fastapi_server:app --host 0.0.0.0 --port 8000 --reload
   ```

### Default Credentials
- **Admin:** `admin@noxsuite.local` / `Admin123!`
- **User:** `user@noxsuite.local` / `User123!`
- **MFA Test:** `mfa_test@noxsuite.local` / `Mfa123!`

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://noxsuite_user:noxsuite_password_2025@localhost:3306/noxsuite_prod

# Security Settings
JWT_SECRET_KEY=your-super-secure-jwt-secret
MFA_ISSUER=NoxSuite
ARGON2_TIME_COST=2
ARGON2_MEMORY_COST=65536

# TestSprite Integration
TESTSPRITE_API_KEY=your-testsprite-api-key
TESTSPRITE_PROJECT_ID=your-project-id
```

## 🧪 Testing

### Run Authentication Tests
```bash
python testsprite_e2e.py --full
```

### Run Security Audit
```bash
python noxsuite_comprehensive_audit.py
```

### Run Migration Enforcer
```bash
python mariadb_migration_enforcer.py
```

## 📊 Security Features

### 🔐 **MFA Implementation**
- **TOTP (Time-based OTP)** with 30-second windows
- **Backup codes** with Argon2 hashing
- **QR code generation** for authenticator apps
- **Zero-tolerance verification** (no replay attacks)

### 🛡️ **RBAC System**
- **Granular permissions** (users, roles, audit, system)
- **Database-backed persistence** (no memory-only storage)
- **Role inheritance** and composition
- **Dynamic permission checking**

### 🔍 **Audit Framework**
- **Comprehensive event logging**
- **Real-time security monitoring**
- **Skeptical development auditor**
- **Automated compliance validation**

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login with MFA support
- `POST /auth/mfa/setup` - MFA setup
- `GET /auth/me` - Current user profile

### MFA Management
- `GET /mfa/status` - MFA status
- `POST /mfa/setup/complete` - Complete MFA setup
- `POST /mfa/verify` - Verify MFA code

### RBAC Management
- `GET /roles` - List roles
- `POST /roles` - Create role
- `PUT /roles/{id}` - Update role
- `DELETE /roles/{id}` - Delete role

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build production image
docker build -t noxsuite-security-platform .

# Run with Docker Compose
docker-compose up -d
```

### Security Checklist
- ✅ MariaDB-first database policy enforced
- ✅ MFA enabled for all admin accounts
- ✅ RBAC permissions properly configured
- ✅ Argon2 password hashing implemented
- ✅ Session timeouts configured
- ✅ Audit logging active
- ✅ TestSprite 95% pass rate achieved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow **Skeptical Development** principles
- Maintain **95% test coverage** minimum
- Enforce **MariaDB-first** database policy
- Implement **zero-compromise security** standards

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

For security issues, please email: security@noxsuite.local

**Do not create public GitHub issues for security vulnerabilities.**

## 📈 Roadmap

- [ ] Advanced threat detection
- [ ] SAML/OAuth2 integration
- [ ] Multi-tenant support
- [ ] Advanced audit analytics
- [ ] Mobile app authentication

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **MariaDB** for reliable database performance
- **TestSprite** for comprehensive testing capabilities
- **Argon2** for secure password hashing

---

**🔒 Built with zero-compromise security principles**
