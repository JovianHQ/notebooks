#!/usr/bin/env python3
"""
Smart script to remove jovian.commit() cells and forum references from notebooks.
This script intelligently edits cells rather than deleting them entirely.
"""
import json
import re
from pathlib import Path

def clean_markdown_cell(cell_source):
    """Clean a markdown cell by removing jovian.commit and forum references."""
    if not cell_source:
        return cell_source, False

    modified = False
    lines = cell_source if isinstance(cell_source, list) else [cell_source]
    cleaned_lines = []
    skip_until_blank = False

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Clean up headers that mention "Save Your Work"
        if line.startswith('#') and 'save your work' in line_lower:
            # Remove "and Save Your Work" from headers
            line = re.sub(r'\s+and\s+Save\s+Your\s+Work', '', line, flags=re.IGNORECASE)
            modified = True

        # Skip lines mentioning jovian.commit in instructions
        if 'jovian.commit' in line:
            modified = True
            # Check if this is part of a numbered list - skip the entire point
            if re.match(r'^\d+\.', line.strip()):
                skip_until_blank = True
                continue
            # Check if it's a paragraph about saving work
            elif any(phrase in line_lower for phrase in ['saving your work', 'save your work', 'save a snapshot']):
                skip_until_blank = True
                continue
            else:
                continue

        # Skip forum/community links and references
        if any(phrase in line_lower for phrase in [
            'community forum',
            'forum/c/',
            'ask questions, discuss ideas and get help',
            'jovian.com/forum'
        ]):
            modified = True
            # If it's a numbered list item, skip it
            if re.match(r'^\d+\.', line.strip()):
                skip_until_blank = True
                continue
            # If it's a link in Important Links, skip the entire line
            elif 'forum' in line_lower:
                continue

        # Skip blank lines after removed content
        if skip_until_blank:
            if line.strip() == '':
                skip_until_blank = False
            continue

        cleaned_lines.append(line)

    # Renumber list items if needed
    cleaned_text = cleaned_lines
    if modified:
        # Try to renumber any lists
        result = []
        current_num = 1
        in_list = False

        for line in cleaned_text:
            # Check if this is a numbered list item
            match = re.match(r'^(\d+)\.\s+(.*)$', line.lstrip())
            if match:
                # Calculate indentation
                indent = len(line) - len(line.lstrip())
                result.append(' ' * indent + f"{current_num}. {match.group(2)}")
                current_num += 1
                in_list = True
            else:
                # Reset numbering when we exit the list
                if in_list and line.strip() and not line.strip().startswith('-'):
                    in_list = False
                    current_num = 1
                result.append(line)

        cleaned_text = result

    return cleaned_text, modified

def clean_notebook(notebook_path):
    """Remove jovian.commit cells and clean forum references from a notebook."""
    print(f"\nProcessing: {notebook_path.name}")

    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    original_cell_count = len(notebook['cells'])
    cells_to_remove = []
    cells_modified = 0

    # Process each cell
    for i, cell in enumerate(notebook['cells']):
        cell_source = cell.get('source', [])

        if not cell_source:
            continue

        cell_text = ''.join(cell_source) if isinstance(cell_source, list) else cell_source

        # Remove code cells with jovian.commit()
        if cell['cell_type'] == 'code' and 'jovian.commit' in cell_text:
            cells_to_remove.append(i)
            print(f"  [DELETE] Code cell {i} with jovian.commit()")

        # Handle markdown cells
        elif cell['cell_type'] == 'markdown':
            lower_text = cell_text.lower()

            # Delete cells that ONLY say "Let's save our work before continuing"
            if cell_text.strip() in [
                "Let's save our work before continuing.",
                "Let's save our work before continuing"
            ]:
                cells_to_remove.append(i)
                print(f"  [DELETE] Markdown cell {i} - save work message")

            # Edit cells that contain jovian.commit or forum references but have other content
            elif 'jovian.commit' in cell_text or 'forum' in lower_text or 'community' in lower_text:
                cleaned_source, was_modified = clean_markdown_cell(cell_source)
                if was_modified:
                    cell['source'] = cleaned_source
                    cells_modified += 1
                    print(f"  [EDIT] Markdown cell {i} - removed jovian.commit/forum references")

    # Remove cells in reverse order
    for i in sorted(cells_to_remove, reverse=True):
        del notebook['cells'][i]

    removed_count = len(cells_to_remove)

    if removed_count > 0 or cells_modified > 0:
        # Save the cleaned notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"  ✓ Removed {removed_count} cells, edited {cells_modified} cells")
        print(f"    ({original_cell_count} → {len(notebook['cells'])} total cells)")
    else:
        print(f"  ✓ No changes needed")

    return removed_count, cells_modified

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
        "decision-trees-and-hyperparameters/sklearn-decision-trees-random-forests.ipynb",
    ]

    base_path = Path("/home/ramayen/Documents/projects/JovianHQ/notebooks/machine-learning-with-python-zero-to-gbms")

    total_removed = 0
    total_modified = 0
    processed_count = 0

    for notebook_rel_path in notebooks:
        notebook_path = base_path / notebook_rel_path
        if notebook_path.exists():
            removed, modified = clean_notebook(notebook_path)
            total_removed += removed
            total_modified += modified
            processed_count += 1
        else:
            print(f"\n⚠ Notebook not found: {notebook_path}")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Notebooks processed: {processed_count}")
    print(f"  Total cells deleted: {total_removed}")
    print(f"  Total cells edited: {total_modified}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
