# notebooks

Jupyter notebooks for courses hosted on <https://jovian.com>

## Development Setup

Follow the following instructions to setup your system in order to work with this repository.

### Prerequisites

It is expected that to contribute to this project you know git and basic
set of system commands. Start by installing following software:

1. **Vscode:**
   Install Vscode from [this](https://code.visualstudio.com/Download) page for your operating system.

   > If your distribution is not debian or fedora based, then search vscode in your distribution's package
   > registry or install from [flathub](https://flathub.org/en/apps/com.visualstudio.code).

2. **Node:**
   Install nodejs from [this](https://nodejs.org/en/download) page. The recommended way of installing node is by
   [nvm](https://github.com/nvm-sh/nvm) as mentioned in the download page. Make sure node and npm is installed
   by checking their versions through `node -v` and `npm -v` respectively.

3. **uv:**
   It is python's package and project manager which can be installed from
   [this](https://docs.astral.sh/uv/getting-started/installation/) page. For Linux and MacOS, it
   is simply by running the installation script with the command `curl -LsSf https://astral.sh/uv/install.sh | sh`

4. **Python:**
   Ensure that python is installed in your system by command `python --version`. Otherwise,
   install it from [here](https://www.python.org/downloads/) for your specific OS.

5. **Git:**
   Install git for your specific system from [here](https://git-scm.com/downloads).

### Setting Up

1. Fork this project in your github profile and clone it locally with command
   `git clone git@github.com:your_username/notebooks.git`. Don't forget to
   replace `your_username` with your github's username.
2. Next up, move into the project with `cd notebooks` and install python dependencies with
   `uv sync`.
3. Let's now install codex with command `npm install -g @openai/codex`.
4. Run `codex` in your present working directory( i.e. notebooks) to start the AI agent.
   Running the command for the first time will ask you to authenticate by signing into Chatgpt.
5. Once, the authentication is complete, you can start by asking codex about the overview of the
   repository in the terminal itself.
6. Open vscode in this directory by `code .` command, further install Codex and Python extensions from the
   extensions tab in Vscode.

### Making changes

1. Changes in this repository are accepted in PR format. So, create a new branch in your repository by opening
   the directory in terminal (or terminal pane in Vscode) and running `git branch -u branch_name`.
2. Activate python environment by `source .venv/bin/activate`.
3. Make your changes. Commit them in your branch and then pull a request in github to merge the changes.
   Always provide proper description of what you changed in commit messages and PR's description section.

### How to add "Open in Colab" tags

1. Install dependencies:

```bash
uv sync
```

2. Run `scripts/recursive_tag.py` with course slug:

```bash
uv run scripts/recursive_tag.py -- data-analysis-with-python-zero-to-pandas
```

This will invoke `scripts/capture_tag.py` recursively for each notebook within the course and add the "Open in Colab" tag.

3. Start Jupyter Lab to view the notebooks with "Open in Colab".

```bash
uv run jupyter lab
```

Navigate to any notebook in the modified course to see and test the tag.

### How to clean Jovian references from notebooks

The `clean_notebooks_complete.py` script removes all Jovian-related references from notebooks including:

- `jovian.commit()` function calls and cells
- `import jovian` statements
- `pip install jovian` commands
- Forum and community links
- "Save Your Work" instructions

1. Install dependencies:

```bash
uv sync
```

2. Run `scripts/clean_notebooks_complete.py` with course folder name:

```bash
uv run scripts/clean_notebooks_complete.py -- introduction-to-programming-with-python
```

This will process all notebooks in the specified course folder and remove Jovian references. The script provides detailed output showing which cells were deleted or edited.

3. Review changes with git:

```bash
git diff
```

This shows all modifications made to the notebooks. You can also open the notebooks in Jupyter Lab to verify the changes visually.

4. Check the summary output from the script to see:
   - Number of notebooks processed
   - Total cells deleted
   - Total cells edited

### How to refresh tags for all notebooks in a course

The `recursive_refresh.py` script refreshes "Open in Colab" tags for all notebooks within a course directory. This is useful when multiple notebooks need their tags updated.

1. Install dependencies:

```bash
uv sync
```

2. Run `scripts/recursive_refresh.py` with course name:

```bash
uv run scripts/recursive_refresh.py -- data-analysis-with-python-zero-to-pandas
```

This will:

- Iterate through all subdirectories in the course folder
- Call `refresh_tag.py` for each notebook found. It removes the existing "Open in Colab" tag from a notebook and regenerates it with the updated link. This is useful when notebook names change or tags need to be updated.
- Display progress and any errors encountered

3. Review changes across all notebooks:

```bash
git diff --stat
```

This shows a summary of all modified notebooks.

4. Open Jupyter Lab to spot-check several notebooks:

```bash
uv run jupyter lab
```

Navigate through different notebooks in the course to verify tags were refreshed properly.
