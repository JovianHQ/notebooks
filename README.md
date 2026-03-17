# notebooks

Jupyter notebooks for courses hosted on <https://jovian.com>.

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
   [nvm](https://github.com/nvm-sh/nvm) as mentioned in the download page. Make sure node and npm is installed by checking their versions.
```
node -v
npm -v
```

3. **uv:**
   It is python's package and project manager which can be installed from
   [this](https://docs.astral.sh/uv/getting-started/installation/) page. For Linux and MacOS, it
   is simply by running the installation script with the command:
   
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

4. **Python:**
   Ensure that python is installed in your system by command `python --version`. Otherwise,
   install it from [here](https://www.python.org/downloads/) for your specific OS.

5. **Git:**
   Install git for your specific system from [here](https://git-scm.com/downloads).

### Setting Up

1. Fork this project in your github profile and clone it locally with command:
```
git clone git@github.com:your_username/notebooks.git
```
Don't forget to replace `your_username` with your github's username.

2. Next up, move into the project with and install python dependencies with:
```
cd notebooks
uv sync
```
3. Let's now install codex with command:
```
npm install -g @openai/codex
```
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

### How to remove `jovian.pythondsa` library from DSA lesson notebooks

The `jovian` Python library is deprecated. The DSA course notebooks (`data-structures-and-algorithms-in-python/`) use `evaluate_test_case` and `evaluate_test_cases` from `jovian.pythondsa`. These need to be replaced with an inline implementation.

#### What to change

For each notebook, look for and handle the following:

**1. Remove the install cell** — find and delete or replace:
```python
!pip install jovian --upgrade --quiet
```

**2. Remove import cells** — find and delete:
```python
from jovian.pythondsa import evaluate_test_cases
from jovian.pythondsa import evaluate_test_case
```
If a cell contains an import line *and* other code (e.g. a `results = ...` call), only remove the import line and keep the rest.

**3. Replace with the inline implementation** — in place of the install cell (or just before the first `evaluate_test_case`/`evaluate_test_cases` call), add a new code cell with:

```python
from timeit import default_timer as timer
from textwrap import dedent
import math

def _str_trunc(data, size=100):
    data_str = str(data)
    if len(data_str) > size + 3:
        return data_str[:size] + '...'
    return data_str


def _show_test_case(test_case):
    inputs = test_case['input']

    if 'outputs' in test_case:
        expected_text = "Outputs"
        expected = test_case.get('outputs')
    else:
        expected_text = "Output"
        expected = test_case.get('output')

    print(dedent("""
    Input:
    {}

    Expected {}:
    {}
    """.format(_str_trunc(inputs), expected_text, _str_trunc(expected))))


def _show_result(result):
    actual_output, passed, runtime = result
    message = "\033[92mPASSED\033[0m" if passed else "\033[91mFAILED\033[0m"
    print(dedent("""
    Actual Output:
    {}

    Execution Time:
    {} ms

    Test Result:
    {}
    """.format(_str_trunc(actual_output), runtime, message)))


def evaluate_test_case(function, test_case, display=True):
    """Check if `function` works as expected for `test_case`"""
    inputs = test_case['input']

    if display:
        _show_test_case(test_case)

    start = timer()
    actual_output = function(**inputs)
    end = timer()

    runtime = math.ceil((end - start)*1e6)/1000
    if 'outputs' in test_case:
        passed = actual_output in test_case.get('outputs')
    else:
        passed = actual_output == test_case.get('output')

    result = actual_output, passed, runtime

    if display:
        _show_result(result)

    return result


def evaluate_test_cases(function, test_cases, error_only=False, summary_only=False):
    results = []
    for i, test_case in enumerate(test_cases):
        if not error_only:
            print("\n\033[1mTEST CASE #{}\033[0m".format(i))
        result = evaluate_test_case(function, test_case, display=False)
        results.append(result)
        if error_only and not result[1]:
            print("\n\033[1mTEST CASE #{}\033[0m".format(i))
        if not error_only or not result[1]:
            _show_test_case(test_case)
            _show_result(result)

    total = len(results)
    num_passed = sum([r[1] for r in results])
    print("\n\033[1mSUMMARY\033[0m")
    print("\nTOTAL: {}, \033[92mPASSED\033[0m: {}, \033[91mFAILED\033[0m: {}".format(
        total, num_passed, total - num_passed))
    return results
```

**4. Update markdown cells** — find markdown cells that say things like:
- *"...helper function from the `jovian` library"* → remove "from the `jovian` library"
- *"...`evaluate_test_cases` function from `jovian`"* → remove "from `jovian`"

#### What NOT to change

- `jovian.com` URLs in markdown cells that are reference/resource links (course pages, assignment pages, learning resources) — these are educational links, not library references
- "Jovian" as a company name in problem statements
- `JovianHQ` in GitHub/Colab badge URLs

#### Reference

See the diff between `main` and `dsa-new` branches for `lesson-1` as the canonical example:
```bash
git diff main dsa-new -- data-structures-and-algorithms-in-python/lesson-1-binary-search-linked-lists-and-complexity/
```

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
