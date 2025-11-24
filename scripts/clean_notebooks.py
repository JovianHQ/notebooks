#!/usr/bin/env python3
"""
Script to remove jovian.commit() cells and related markdown cells from notebooks.
"""
import json
from pathlib import Path

def clean_notebook(notebook_path):
    """Remove jovian.commit cells and 'save work' markdown cells from a notebook."""
    print(f"\nProcessing: {notebook_path}")

    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    original_cell_count = len(notebook['cells'])
    cells_to_remove = []

    # Find cells to remove
    for i, cell in enumerate(notebook['cells']):
        cell_source = ''.join(cell.get('source', []))

        # Check for jovian.commit() in code cells
        if cell['cell_type'] == 'code' and 'jovian.commit' in cell_source:
            cells_to_remove.append(i)
            print(f"  Found jovian.commit in code cell {i}")

        # Check for "save our work" or jovian.commit instructions in markdown cells
        elif cell['cell_type'] == 'markdown':
            lower_source = cell_source.lower()
            if any(phrase in lower_source for phrase in [
                "let's save our work before continuing",
                "let's save our work",
                "save and upload",
                "saving your work",
                "save your work by running `jovian.commit`"
            ]) or 'jovian.commit' in cell_source:
                cells_to_remove.append(i)
                print(f"  Found 'save work' or jovian.commit reference in markdown cell {i}")

    # Remove cells in reverse order to maintain indices
    for i in sorted(cells_to_remove, reverse=True):
        del notebook['cells'][i]

    removed_count = len(cells_to_remove)

    if removed_count > 0:
        # Save the cleaned notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"  ✓ Removed {removed_count} cells ({original_cell_count} → {len(notebook['cells'])})")
    else:
        print(f"  ✓ No cells to remove")

    return removed_count

def main():
    # Notebooks to process
    notebooks = [
        "unsupervised-learning-and-recommendations/sklearn-unsupervised-learning.ipynb",
        "random-forests-and-regularization/sklearn-decision-trees-random-forests.ipynb",
        "logistic-regression-for-classification/python-sklearn-logistic-regression.ipynb",
        "linear-regression-with-scikit-learn/python-sklearn-linear-regression.ipynb",
        "gradient-boosting-with-xgboost/python-gradient-boosting-machines.ipynb",
        "assignment-1-train-your-first-ml-model/python-sklearn-assignment.ipynb",
        "assignment-2-decision-trees-and-random-forests/python-random-forests-assignment.ipynb",
    ]

    base_path = Path("/home/ramayen/Documents/projects/JovianHQ/notebooks/machine-learning-with-python-zero-to-gbms")

    total_removed = 0
    processed_count = 0

    for notebook_rel_path in notebooks:
        notebook_path = base_path / notebook_rel_path
        if notebook_path.exists():
            removed = clean_notebook(notebook_path)
            total_removed += removed
            processed_count += 1
        else:
            print(f"\n⚠ Notebook not found: {notebook_path}")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Notebooks processed: {processed_count}")
    print(f"  Total cells removed: {total_removed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
