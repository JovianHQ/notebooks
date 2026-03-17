---
name: remove-jovian-pythondsa
description: This skill should be used when the user asks to remove `jovian.pythondsa`, replace jovian test case functions, migrate DSA notebooks away from the jovian library, or process DSA lesson notebooks to remove jovian imports.
version: 1.0.0
---

# Remove `jovian.pythondsa` from DSA Lesson Notebooks

The `jovian` Python library is deprecated. DSA course notebooks (`data-structures-and-algorithms-in-python/`) use `evaluate_test_case` and `evaluate_test_cases` from `jovian.pythondsa`. These need to be replaced with an inline implementation.

## What to Change

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

## What NOT to Change

- `jovian.com` URLs in markdown cells that are reference/resource links (course pages, assignment pages, learning resources) — these are educational links, not library references
- "Jovian" as a company name in problem statements
- `JovianHQ` in GitHub/Colab badge URLs

## Reference

See the diff between `main` and `dsa-new` branches for `lesson-1` as the canonical example:
```bash
git diff main dsa-new -- data-structures-and-algorithms-in-python/lesson-1-binary-search-linked-lists-and-complexity/
```
