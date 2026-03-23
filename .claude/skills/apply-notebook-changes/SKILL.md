---
name: apply-notebook-changes
description: This skill should be used when the user asks to apply general notebook changes, clean up Jovian notebook cells, update "How to Run the Code" sections, remove "Part of" lesson mentions, remove bootcamp references, or add a Submission section to assignment notebooks.
version: 1.0.0
---

# Apply General Notebook Changes

Apply standard cleanup changes to Jovian course notebooks.

## Changes to Apply

### 1. Remove "Part of" Mentions

In markdown cells, remove any text that says this notebook is "Part of" some lesson, e.g.:
- _"Part of \"Data Structures and Algorithms in Python\""_
- _"Part of Lesson 3"_

If the cell contains only this text, remove the cell entirely. If the cell has other content, remove only that line.

### 2. Replace "How to Run the Code" Section

Find markdown cells containing a "How to Run the Code" heading/section. Replace the section content (not necessarily the whole cell) with:

```
This tutorial is an executable [Jupyter notebook](https://jupyter.org). Click the **Open in Colab** button at the top of this page to execute the code.

> **Jupyter Notebooks**: This notebook is made of _cells_. Each cell can contain code written in Python or explanations in plain English. You can execute code cells and view the results instantly within the notebook. Jupyter is a powerful platform for experimentation and analysis. Don't be afraid to mess around with the code & break things - you'll learn a lot by encountering and fixing errors. You can use the "Kernel > Restart & Clear Output" menu option to clear all outputs and start again from the top.
```

- If the cell contains **only** the "How to Run the Code" section, replace the entire cell source with the above content.
- If the cell contains **other content**, remove only the "How to Run the Code" section and replace it inline with the above content.

### 3. Remove Jovian Bootcamp Mentions

In markdown cells, remove any specific text saying this tutorial is part of a Jovian bootcamp, e.g.:
- _"This tutorial is part of [Zero to Data Analyst Bootcamp](https://jovian.com/...)"_
- _"as part of the Jovian bootcamp"_

If the cell contains only this text, remove the cell entirely. If the cell has other content, remove only the bootcamp-related line(s).

### 4. Add Submission Section to Assignment Notebooks

For notebooks whose filename starts with `assignment-`, add a new markdown cell at the very bottom of the notebook with the following content:

```markdown
## Submission

Congratulations on making it this far! You've completed the assignment. Here's what to do next:

1. Verify that all the cells in the notebook have been executed and the outputs are visible.
2. `jovian.commit` uploads the notebook to your Jovian profile. Run the cell below to save and upload your work.
```

Followed by a new code cell:

```python
import jovian
jovian.commit()
```

Only add this section if it doesn't already exist at the bottom of the notebook.

## Important Rules

- **Never remove a complete cell** if it contains content beyond what needs to be changed — only edit the relevant lines within it.
- These changes apply to markdown cells (and code cells only for the Submission section addition).
- Do not alter code logic, outputs, or unrelated cell content.
