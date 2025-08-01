# NoxSuite Workspace Migration Plan

**Generated:** 2025-07-31 09:06

## Current Issues
- Misplaced files: 8
- Conflict files: 4866
- Missing files: 3

## Target Structure
```
noxsuite/
├── backend/
│   ├── api/           # API routes and services
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── tests/         # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API clients
│   └── public/
├── docker/            # Docker configurations
├── tests/             # Integration tests
└── config/            # Configuration files
```

## Migration Steps

### 1. Backup Current State
```bash
cp -r . ../noxsuite_backup_20250731_090611
```

### 2. Create Structure
```bash
mkdir -p noxsuite/{backend/{api,models,services,tests},frontend/{src,public},docker,tests,config}
```

### 3. Move Files
- Move testsprite_e2e.py to tests/testsprite_e2e.py
- Move auth_service.py to backend/services/auth_service.py
- Move api_routes.py to backend/api/api_routes.py
- Move user_service.py to backend/api/user_service.py
- Move Dashboard.css to frontend/src/components/Dashboard.css
- Move Dashboard.jsx to frontend/src/components/Dashboard.jsx
- Move Login.css to frontend/src/components/Login.css
- Move Login.jsx to frontend/src/components/Login.jsx


### 4. Clean Up
```bash
# Remove conflict files
find . -name "*.conflict.*" -delete

# Remove duplicates (manual review)
# Update import paths
```

### 5. Validation
- Run TestSprite validation
- Verify Docker builds
- Test API endpoints
