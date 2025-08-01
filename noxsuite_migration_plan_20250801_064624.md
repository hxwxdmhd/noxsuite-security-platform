# NoxSuite Workspace Migration Plan

**Generated:** 20250801_064624

## 🎯 Objective
Consolidate NoxSuite files into unified workspace structure for better organization and maintainability.

## 📁 Current Issues
- 3 misplaced files
- 478 duplicate files  
- 4412 conflict files

## 🏗️ Target Structure
```
noxsuite/
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── database/
│   └── tests/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/
├── tests/
├── docs/
└── config/
```

## 🔧 Migration Steps

### Phase 1: Backup and Preparation
```bash
# Create backup
cp -r . ../noxsuite_backup_20250801_064624

# Create new structure
mkdir -p noxsuite/{backend,frontend,docker,tests,docs,config}
mkdir -p noxsuite/backend/{api,models,services,database,tests}
mkdir -p noxsuite/frontend/{src,public}
```

### Phase 2: File Migration
# Create unified NoxSuite structure
mkdir -p noxsuite/{backend/{api,models,services,database,tests},frontend/{src,public},docker,tests,docs,config}

# Move backend files
mv backend/api/* noxsuite/backend/api/
mv backend/models/* noxsuite/backend/models/ 2>/dev/null || true
mv backend/services/* noxsuite/backend/services/ 2>/dev/null || true

# Move frontend files
mv frontend/src/* noxsuite/frontend/src/
mv frontend/package.json noxsuite/frontend/

# Move configuration files
mv requirements.txt noxsuite/config/
cp pyproject.toml noxsuite/config/

# Clean up conflict files
find . -name '*.conflict.*' -delete

# Update import paths (manual review required)
echo 'Review and update import paths in Python files'

### Phase 3: Configuration Updates
- Update import paths in Python files
- Update package.json paths
- Update Docker compose file paths
- Update CI/CD configuration

### Phase 4: Validation
- Run TestSprite validation
- Verify all imports work
- Test Docker builds
- Validate API endpoints

## ⚠️ Risks & Mitigation
- **Import path breaks:** Test thoroughly, update systematically
- **Docker build failures:** Update Dockerfile paths
- **Lost files:** Complete backup before migration

## ✅ Success Criteria
- All files in correct locations
- No import errors
- All tests passing
- Docker builds successful
