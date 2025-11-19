# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Jupyter notebooks for various courses hosted on https://jovian.com. The notebooks are organized by course name, with each course containing multiple lessons and assignments.

**Course Categories:**
- Data Analysis & Visualization (pandas, numpy, matplotlib, seaborn, plotly)
- Machine Learning (scikit-learn, XGBoost, unsupervised learning)
- Deep Learning (PyTorch, GANs, CNNs, RNNs)
- Data Structures & Algorithms
- Natural Language Processing
- Web Development (JavaScript, Node.js, Flask, HTML/CSS)
- SQL & Business Intelligence
- Statistics for Data Science
- Career Readiness Training

## Development Environment

### Setup Commands

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run Jupyter notebook (if needed)
jupyter notebook
```

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Node.js (for JavaScript courses)
- Git

## Key Scripts

The `scripts/` directory contains utilities for managing notebooks:

### download-notebook.py

Downloads individual Jovian notebooks using the Jovian API.

```bash
python scripts/download-notebook.py <notebook_url> [destination_dir] [--token-env AUTH_TOKEN] [--verbose]
```

**Requirements:**
- `AUTH_TOKEN` must be set in `.env` file or environment variables
- The token is used to authenticate with the Jovian API at `https://api.jovian.com`

**Example:**
```bash
python scripts/download-notebook.py https://jovian.com/aakashns/first-steps-with-python .
```

### download-lesson.py

Downloads all notebooks from a Jovian lesson page by scraping for notebook links.

```bash
python scripts/download-lesson.py <lesson_url> [destination_dir] [--token-env AUTH_TOKEN] [--verbose]
```

**How it works:**
- Fetches HTML from the lesson page
- Parses "Open in new tab" links to find notebook URLs
- Calls `download-notebook.py` for each notebook found
- Creates a folder named after the lesson slug

### capture_tag.py

Extracts Google Colab badge HTML from GitHub notebook URLs using Selenium.

```bash
python scripts/capture_tag.py <github_notebook_url>
```

**Requirements:**
- Selenium WebDriver with Firefox
- Uses https://openincolab.com to generate Colab badges
- Modifies notebook JSON by inserting the badge into the first cell

### recursive_tag.py

Recursively processes all notebooks in a course directory to add Colab badges.

```bash
python scripts/recursive_tag.py <course_name>
```

**How it works:**
- Iterates through course folders
- Constructs GitHub URLs for each notebook
- Calls `capture_tag.py` for each notebook

## Repository Structure

```
notebooks/
├── scripts/                                    # Utility scripts
├── src/notebooks/                              # Minimal Python package
├── <course-name>/                              # Course directories
│   ├── lesson-1-<topic>/                       # Lesson folders
│   │   └── *.ipynb                             # Jupyter notebooks
│   ├── assignment-1-<topic>/
│   └── ...
├── .env                                        # Contains AUTH_TOKEN
├── pyproject.toml                              # Project metadata
└── uv.lock                                     # Dependency lock file
```

## Authentication

All download scripts require a Jovian API token:

1. Token must be stored in `.env` file as `AUTH_TOKEN`
2. The `.env` file is git-ignored for security
3. Scripts search for `.env` starting from current directory upward
4. Token format: JWT Bearer token for https://api.jovian.com

## Working with Notebooks

### Notebook Structure

- Each notebook typically has a Colab badge in the first cell
- Notebooks follow Jovian's structure with course content, exercises, and solutions
- Most notebooks are self-contained with inline explanations

### Modifying Notebooks

When editing notebooks:
- Notebooks are JSON files - use `json.load()` and `json.dump()` for programmatic edits
- Cell structure: `notebook["cells"][index]["source"]` contains cell content as a list of strings
- Preserve formatting by using `indent=4` when saving JSON

## Git Workflow

Current branch: `scripts_notebook_fix`
Main branch: `main`

Always create feature branches for changes and submit PRs to `main`.

## Common Tasks

### Download a single notebook
```bash
python scripts/download-notebook.py https://jovian.com/user/notebook-slug ./destination
```

### Download entire lesson
```bash
python scripts/download-lesson.py https://jovian.com/learn/course-name/lesson/lesson-slug ./destination
```

### Add Colab badges to course notebooks
```bash
python scripts/recursive_tag.py data-analysis-with-python-zero-to-pandas
```

### Test a script with verbose logging
```bash
python scripts/download-notebook.py <url> . --verbose
```

## Notes

- The repository uses `uv` for dependency management (not pip or poetry)
- Virtual environment is stored in `.venv/`
- Notebooks are primarily educational content, not production code
- The `src/notebooks/` package is minimal and currently just contains a hello function
