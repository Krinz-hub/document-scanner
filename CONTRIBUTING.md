# Contribution & Git Conventions

## 1. Branch Naming Convention

All development branches must be created from `main` using the following prefixes:

- `feature/<step-number>-<short-name>`: New capabilities or phases (e.g. `feature/step-8-fastapi-app`).
- `fix/<short-name>`: Bug fixes or corrections to existing logic (e.g. `fix/mrz-checksum-mod10`).
- `test/<short-name>`: Test suites or dataset benchmarks (e.g. `test/ocr-held-out-set`).
- `chore/<short-name>`: Tooling, dependencies, or configuration updates (e.g. `chore/docker-compose-update`).

---

## 2. Commit Message Convention (Conventional Commits)

Commit messages must follow the format:

```text
<type>(<scope>): <short description in imperative mood>

[optional body explaining rationale]
```

### Allowed Types
- `feat`: A new feature or phase implementation.
- `fix`: A bug fix.
- `docs`: Documentation updates only.
- `style`: Formatting changes that do not affect code logic.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `perf`: Performance optimization.
- `test`: Adding or updating tests.
- `chore`: Tooling, Docker, dependencies, or repository housekeeping.

### Allowed Scopes
- `repo`, `infra`, `backend`, `frontend`, `orchestrator`, `quality`, `ocr`, `mrz`, `rules`, `tampering`, `face`, `external`, `audit`.

### Examples
- `feat(backend): create fastapi app and /api/v1/health endpoint`
- `test(mrz): add unit tests for ICAO 9303 check-digit calculation`
- `fix(rules): prevent false-positive expiry flag on leap years`

---

## 3. Quality Gate

No code may be committed without completing:
1. **Build:** Verified syntax and startup.
2. **Test:** Automated test pass (pytest or equivalent).
3. **Audit:** Zero secret leaks or unneeded dependencies.
