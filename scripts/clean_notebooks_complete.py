#!/usr/bin/env python3
"""
Complete script to remove all Jovian references from notebooks.
Removes: jovian.commit, forum links, import jovian, and pip install jovian.
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
        original_line = line

        # Remove jovian from pip install commands in markdown code blocks
        if 'pip install' in line and 'jovian' in line:
            line = re.sub(r'\s+jovian(?:[><=!]=?\S+)?(?=\s|$)', '', line)
            line = re.sub(r'jovian(?:[><=!]=?\S+)?\s+', '', line)
            line = re.sub(r'\s+', ' ', line)
            if line != original_line:
                modified = True

        # Remove lines with jovian clone or ?jovian commands
        if 'jovian clone' in line or '?jovian' in line:
            modified = True
            # Skip the entire instruction step if it's numbered
            if re.match(r'^\d+\.', line.strip()):
                skip_until_blank = True
            continue

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

def clean_code_cell(cell_source):
    """Clean a code cell by removing import jovian and pip install jovian."""
    if not cell_source:
        return cell_source, False, False

    modified = False
    should_delete = False
    lines = cell_source if isinstance(cell_source, list) else [cell_source]
    cleaned_lines = []

    for line in lines:
        line_stripped = line.strip()

        # Check if cell should be deleted (jovian.commit or ?jovian)
        if line_stripped == 'jovian.commit()' or line_stripped.startswith('jovian.commit(') or \
           line_stripped == '?jovian.commit' or line_stripped.startswith('?jovian'):
            should_delete = True
            return None, True, True

        # Remove 'import jovian' lines
        if line_stripped == 'import jovian' or line_stripped.startswith('import jovian '):
            modified = True
            continue  # Skip this line

        # Remove 'from jovian import ...' lines
        if line_stripped.startswith('from jovian import'):
            modified = True
            continue  # Skip this line

        # Handle pip install commands
        if 'pip install' in line and 'jovian' in line:
            # Remove jovian from the pip install list
            modified_line = line

            # Pattern to match: jovian with optional version specifiers
            # Handles: jovian, jovian==1.0, jovian>=1.0, jovian<=1.0, etc.
            modified_line = re.sub(r'\s+jovian(?:[><=!]=?\S+)?(?=\s|$)', '', modified_line)
            modified_line = re.sub(r'jovian(?:[><=!]=?\S+)?\s+', '', modified_line)

            # Clean up multiple spaces
            modified_line = re.sub(r'\s+', ' ', modified_line)

            # If pip install is now empty, skip the line
            if re.match(r'^!?\s*pip\s+install\s*(?:--\S+\s*)*$', modified_line.strip()):
                modified = True
                continue  # Skip empty pip install

            if modified_line != line:
                modified = True
                cleaned_lines.append(modified_line)
            else:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)

    # Check if the entire cell is now empty
    if all(line.strip() == '' for line in cleaned_lines):
        should_delete = True

    return cleaned_lines, modified, should_delete

def clean_notebook(notebook_path):
    """Remove all Jovian references from a notebook."""
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

        # Handle code cells
        if cell['cell_type'] == 'code':
            cleaned_source, was_modified, should_delete = clean_code_cell(cell_source)

            if should_delete:
                cells_to_remove.append(i)
                if 'jovian.commit' in cell_text:
                    print(f"  [DELETE] Code cell {i} with jovian.commit()")
                elif 'import jovian' in cell_text:
                    print(f"  [DELETE] Code cell {i} with import jovian")
                else:
                    print(f"  [DELETE] Empty code cell {i}")
            elif was_modified:
                cell['source'] = cleaned_source
                cells_modified += 1
                print(f"  [EDIT] Code cell {i} - removed jovian import/pip install")

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

            # Edit cells that contain ANY jovian references
            elif any(ref in cell_text for ref in ['jovian.commit', 'jovian clone', '?jovian', 'pip install']) or \
                 'forum' in lower_text or 'community' in lower_text:
                cleaned_source, was_modified = clean_markdown_cell(cell_source)
                if was_modified:
                    cell['source'] = cleaned_source
                    cells_modified += 1
                    print(f"  [EDIT] Markdown cell {i} - removed jovian references")

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
    import sys

    if len(sys.argv) < 2:
        print("Usage: python clean_notebooks_complete.py <course_folder>")
        print("Example: python clean_notebooks_complete.py introduction-to-programming-with-python")
        sys.exit(1)

    course_folder = sys.argv[1]
    base_path = Path("/home/ramayen/Documents/projects/JovianHQ/notebooks")
    course_path = base_path / course_folder

    if not course_path.exists():
        print(f"Error: Course folder not found: {course_path}")
        sys.exit(1)

    # Find all notebooks in the course folder
    notebooks = sorted(course_path.glob("**/*.ipynb"))

    if not notebooks:
        print(f"No notebooks found in {course_path}")
        sys.exit(1)

    total_removed = 0
    total_modified = 0
    processed_count = 0

    for notebook_path in notebooks:
        removed, modified = clean_notebook(notebook_path)
        total_removed += removed
        total_modified += modified
        processed_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Notebooks processed: {processed_count}")
    print(f"  Total cells deleted: {total_removed}")
    print(f"  Total cells edited: {total_modified}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
