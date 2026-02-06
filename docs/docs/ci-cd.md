---
sidebar_position: 2
sidebar_label: 'CI/CD Pipeline'
---

# CI/CD Pipeline

RansomStat CTI uses GitHub Actions for continuous integration, security scanning, and documentation deployment. All workflows run automatically on push and pull requests to the `main` branch.

## Workflows Overview

### 1. Python Code Integrity

**Workflow:** `.github/workflows/ci.yml`

Ensures code quality and correctness through automated linting and testing.

#### What It Does

- **Linting with Ruff**: Checks Python code for style violations, common errors, and anti-patterns
- **Auto-fix**: Automatically fixes safe violations (formatting, imports)
- **Testing with Pytest**: Runs the full test suite to verify functionality

#### Configuration

```yaml
Language: Python 3.13
Linter: Ruff (follows PEP 8, with 120-char line length)
Test Framework: Pytest
```

#### Ruff Rules

The project enforces:
- **E**: PEP 8 style errors
- **F**: Pyflakes errors (undefined names, unused imports)
- **B**: flake8-bugbear (common bugs and design issues)
- **I**: isort import sorting

Line length limit: **120 characters**

#### Run Locally

```bash
# Check for linting errors
ruff check .

# Auto-fix safe violations
ruff check . --fix

# Run tests
pytest
```

---

### 2. Security Pipeline

**Workflow:** `.github/workflows/security.yml`

Performs static analysis and dependency vulnerability scanning.

#### What It Does

1. **Static Analysis (Bandit)**
   - Scans for common security issues (SQL injection, hardcoded passwords, etc.)
   - Severity threshold: Medium/High only (`-ll` flag)
   - Excludes test files (`-x tests/`)

2. **Dependency Scanning (pip-audit)**
   - Checks installed packages against CVE databases
   - Identifies known vulnerabilities in dependencies
   - Fails build if critical vulnerabilities found

3. **Streamlit Secrets Check**
   - Verifies `.streamlit/secrets.toml` is not committed
   - Prevents accidental exposure of API keys and credentials

#### Run Locally

```bash
# Install security tools
pip install bandit pip-audit

# Run Bandit SAST
bandit -r . -ll -x tests/

# Check dependencies for vulnerabilities
pip-audit

# Verify secrets not tracked
git ls-files | grep -E "secrets\.toml"  # Should return empty
```

#### Common Issues

**Issue:** pip vulnerability detected (e.g., CVE-2026-1703)
```bash
# Solution: Upgrade pip
python -m pip install --upgrade "pip>=26.0"
```

**Issue:** Bandit flags datetime.now()
```bash
# Severity: Low (informational)
# Action: Review context - if used for logging/display, safe to ignore
```

---

### 3. Documentation Deployment

**Workflow:** `.github/workflows/deploy-docs.yml`

Builds and deploys the Docusaurus documentation site to GitHub Pages.

#### What It Does

- **Build**: Compiles Docusaurus site from `docs/` directory
- **Validate**: Checks for broken links (strict mode)
- **Deploy**: Publishes to GitHub Pages via GitHub Actions artifact upload
- **URL**: https://qepting91.github.io/streamlitransomware/

#### Trigger Conditions

- **Automatic**: Pushes to `main` that modify files in `docs/**`
- **Manual**: Via "Run workflow" button in GitHub Actions

#### Build Locally

```bash
cd docs

# Install dependencies
npm install

# Start development server (with hot reload)
npm run start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

#### Configuration

```yaml
Node Version: 20
Framework: Docusaurus 3.9.2
Build Output: docs/build/
Deployment: GitHub Pages (Actions)
```

---

## Workflow Status

You can monitor workflow runs at:
- **All workflows**: https://github.com/qepting91/streamlitransomware/actions
- **CI runs**: https://github.com/qepting91/streamlitransomware/actions/workflows/ci.yml
- **Security scans**: https://github.com/qepting91/streamlitransomware/actions/workflows/security.yml
- **Docs deployment**: https://github.com/qepting91/streamlitransomware/actions/workflows/deploy-docs.yml

### Status Badges

Add these to your README to show workflow status:

```markdown
![CI](https://github.com/qepting91/streamlitransomware/workflows/Python%20Code%20Integrity/badge.svg)
![Security](https://github.com/qepting91/streamlitransomware/workflows/Security%20Pipeline/badge.svg)
![Docs](https://github.com/qepting91/streamlitransomware/workflows/Deploy%20Documentation/badge.svg)
```

---

## CI/CD Best Practices

### Before Committing

Run these checks locally to catch issues early:

```bash
# 1. Format and lint
ruff check . --fix
ruff check .

# 2. Run tests
pytest

# 3. Security scan (optional, but recommended)
bandit -r . -ll -x tests/
```

### Pre-commit Hooks (Optional)

Install pre-commit hooks to automatically run checks:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Enable:
```bash
pre-commit install
```

---

## Troubleshooting

### CI Failing on Linting

**Symptom:** Ruff reports violations in CI but passes locally

**Cause:** You have uncommitted changes with fixes

**Solution:**
```bash
git add .
git commit -m "fix: resolve linting violations"
git push
```

---

### CI Failing on Import Order

**Symptom:** E402 errors about module imports

**Cause:** Imports aren't at the top of the file (after Streamlit `st.set_page_config()`)

**Solution:**
```python
import streamlit as st

st.set_page_config(...)  # Must come first for Streamlit

import other_module  # Other imports after config
```

---

### Security Pipeline Failing

**Symptom:** pip-audit reports vulnerabilities

**Cause:** Outdated dependencies with known CVEs

**Solution:**
```bash
# Update specific package
pip install --upgrade <package-name>

# Or update all dependencies
pip install --upgrade -r requirements.txt

# Update requirements.txt
pip freeze > requirements.txt
```

---

### Docs Build Failing

**Symptom:** "Broken links found" error

**Cause:** Links to non-existent pages in navbar/footer

**Solution:**
- Remove links to pages that don't exist yet
- Or create placeholder pages for linked sections
- Check `docs/docusaurus.config.js` navbar and footer configuration

---

## Configuration Files

### pyproject.toml

Ruff configuration:

```toml
[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "B", "I"]
ignore = []
```

### pytest Configuration

Tests are located in `tests/` directory:
- `tests/test_etl.py` - ETL engine tests
- `tests/test_ui.py` - UI/app tests
- `tests/conftest.py` - Shared fixtures

Run specific tests:
```bash
pytest tests/test_etl.py
pytest tests/test_ui.py::test_app_load
pytest -v  # Verbose output
```

---

## GitHub Actions Permissions

The workflows require these permissions:

### Python Code Integrity
- `contents: read` - Read repository code

### Security Pipeline
- `contents: read` - Read repository code

### Documentation Deployment
- `contents: read` - Read repository code
- `pages: write` - Write to GitHub Pages
- `id-token: write` - OIDC authentication for Pages deployment

These are configured in each workflow file and don't require manual setup.

---

## Continuous Improvement

### Adding New Checks

To add a new linting rule:

1. Update `pyproject.toml`:
   ```toml
   [tool.ruff.lint]
   select = ["E", "F", "B", "I", "N"]  # Add N for naming conventions
   ```

2. Test locally:
   ```bash
   ruff check .
   ```

3. Fix violations and commit

### Adding New Tests

1. Create test file in `tests/`:
   ```python
   def test_new_feature():
       assert new_function() == expected_result
   ```

2. Run locally:
   ```bash
   pytest tests/test_new_feature.py
   ```

3. CI will automatically run new tests

---

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [Docusaurus Documentation](https://docusaurus.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
