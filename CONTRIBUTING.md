# Contributing to TechGap

Welcome to the TechGap codebase! This document outlines our repository structure, Git branching workflow, commit standards, and Pull Request (PR) review processes to ensure clean, consistent, and traceable development across all contributors.

---

## Table of Contents
1. [Core Principles & Ownership](#1-core-principles--ownership)
2. [Branching Strategy](#2-branching-strategy)
3. [Branch Naming Conventions](#3-branch-naming-conventions)
4. [Commit Message Guidelines](#4-commit-message-guidelines)
5. [Pull Request (PR) Workflow & Guidelines](#5-pull-request-pr-workflow--guidelines)
6. [Daily Developer Cheatsheet](#6-daily-developer-cheatsheet)

---

## 1. Core Principles & Ownership

- **Code Quality First:** Every feature, fix, or pipeline modification must be verifiable and covered by automated tests where applicable.
- **Strict `main` Ownership:** The `main` branch is strictly owned and maintained by the project lead. Direct pushes to `main` are prohibited.
- **No Unreviewed Code:** All changes enter `dev` through reviewed Pull Requests.

---

## 2. Branching Strategy

We follow a 3-tier branch model:

```text
feature/*, fix/*, docs/*
         │
         ▼  (PR & Review)
       dev   [Active integration & testing]
         │
         ▼  (Verified & Approved by Project Lead)
       main  [Stable, production-ready releases only]
```

### The Branches:
1. **`main` (Production / Stable Release)**
   - Contains only stable, verified milestones and releases.
   - **Only touched by the repository owner/lead.**
   - Changes are merged into `main` exclusively from `dev` after thorough verification.
   - Never commit directly to `main` and never open a feature PR directly against `main`.

2. **`dev` (Integration / Active Development)**
   - The primary integration branch where completed features, bug fixes, and documentation updates accumulate.
   - All feature and fix branches are branched off `dev` and must target `dev` in their PRs.
   - Acts as the staging environment where integrated functionality is tested prior to a `main` release.

3. **`feature/*`, `fix/*`, `docs/*`, `test/*` (Working Branches)**
   - Short-lived branches created off the latest `dev`.
   - All actual development work takes place in these branches.
   - Deleted locally and remotely after merging into `dev`.

---

## 3. Branch Naming Conventions

Use clear, descriptive branch names prefixed with the category of change:

| Prefix | Purpose | Example |
| :--- | :--- | :--- |
| `feature/` | New functionality, models, scrapers, endpoints, or UI | `feature/syllabus-parser`, `feature/student-alignment-view` |
| `fix/` | Bug fixes, pipeline errors, or data issues | `fix/csv-delimiter-parser`, `fix/null-skill-weight` |
| `docs/` | Documentation additions or updates | `docs/contributing-guide`, `docs/api-contracts` |
| `test/` | Adding, refactoring, or updating test suites | `test/syllabus-extraction`, `test/topsi-ranking` |
| `refactor/`| Code improvements without functional changes | `refactor/modularize-pipeline` |

*Rule: Use lowercase letters and hyphens (`-`) for separators. Avoid generic names like `patch-1` or `update`.*

---

## 4. Commit Message Guidelines

We follow the **[Conventional Commits](https://www.conventionalcommits.org/)** specification. Clear commit messages make repository history readable, ease troubleshooting, and simplify changelog generation.

### Format
```text
<type>(<scope>): <short imperative summary>

[optional body explaining why the change was made and additional context]

[optional footer: issue references or breaking change notes]
```

### Commit Types
- `feat`: A new feature or capability (e.g., `feat(syllabus): add automated PDF text extraction`)
- `fix`: A bug fix (e.g., `fix(parser): handle missing elective course credits in CSV`)
- `docs`: Documentation changes only (e.g., `docs(setup): document local virtualenv instructions`)
- `test`: Adding or correcting tests (e.g., `test(pipeline): add mock tests for Apify job ingest`)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `style`: Formatting, whitespace, or linting fixes (no code logic changes)
- `chore`: Tooling, build scripts, dependency updates (e.g., `chore(deps): update pdfplumber`)

### Rules
1. **Imperative mood:** Use "add", "fix", "update", not "added", "fixes", "updating".
2. **Short subject:** Limit the first line to 72 characters or fewer.
3. **No trailing period:** Do not put a period at the end of the subject line.
4. **Body for context:** If the change is non-trivial, use the commit body to explain *why* the change was made.

---

## 5. Pull Request (PR) Workflow & Guidelines

### Before Creating a PR
1. **Pull Latest `dev`:** Make sure your branch has the latest commits from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout feature/your-feature-name
   git merge dev
   ```
2. **Run Tests:** Ensure all existing and new unit tests pass locally:
   ```bash
   pytest
   ```
3. **Clean Up Artifacts:** Verify no untracked cache files (`__pycache__`, `.pytest_cache`), environment files (`.env`), or secrets are being committed.

### Creating the PR
1. **Target Branch:** Verify the base branch is **`dev`** (never `main`).
2. **Title:** Use the Conventional Commit style for the PR title:
   - Example: `feat(syllabus): implement syllabus collection and extraction pipeline`
3. **PR Description:** Complete all sections of the [Pull Request Template](.github/pull_request_template.md):
   - **Summary:** Concise description of the changes and motivation.
   - **Type of Change:** Select the applicable tags.
   - **Related Issues / Docs:** Link tickets, PRD sections, or requirement IDs.
   - **Verification:** Outline test steps and paste test outputs or screenshots.
   - **Checklist:** Confirm adherence to branch target, commit standards, and cleanliness.

### Review & Merge
- All PRs require review before merging into `dev`.
- Resolve all review comments and address requested changes.
- Once approved, the branch is merged into `dev` using squash-and-merge or rebase (preserving clean commit history).
- Releases from `dev` into `main` will be performed solely by the project lead following full validation.

---

## 6. Daily Developer Cheatsheet

### 1. Starting a New Task
```bash
# Ensure dev is clean and updated
git checkout dev
git pull origin dev

# Create your feature branch off dev
git checkout -b feature/syllabus-parser
```

### 2. Saving & Committing Work
```bash
# Check status and staged files
git status

# Stage relevant files
git add scripts/extract_syllabi.py tests/test_syllabus_collection.py

# Commit using conventional format
git commit -m "feat(syllabus): implement PDF section extractor with regex fallback"
```

### 3. Syncing with `dev` Before Submitting
```bash
# Pull any changes from dev into your working branch
git fetch origin dev
git merge origin/dev

# Run tests to confirm integration
pytest
```

### 4. Pushing and Opening a PR
```bash
# Push branch to remote
git push -u origin feature/syllabus-parser

# Now navigate to GitHub and open a PR targeting the 'dev' branch!
```

### 5. Cleaning Up After Merge
```bash
# Once merged on GitHub, return to dev and delete your feature branch
git checkout dev
git pull origin dev
git branch -d feature/syllabus-parser
```
