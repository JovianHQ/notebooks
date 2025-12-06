import argparse
import json
import logging
import subprocess
from pathlib import Path
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def remove_colab_tag(path: Path):
    """Remove the Colab tag from the notebook's first cell if present."""
    logger.info(f"Opening notebook: {path}")

    with open(path) as f:
        notebook_as_json = json.load(f)
        logger.info(f"Notebook loaded successfully. Total cells: {len(notebook_as_json['cells'])}")

        first_cell = notebook_as_json["cells"][0]
        source_lines = first_cell["source"]

        # Find and remove the <a> tag and associated empty lines
        modified = False
        lines_to_remove = []

        for i, line in enumerate(source_lines):
            # Check if this line contains the Colab tag opening
            if '<a target="_blank" href="' in line and 'colab.research.google.com' in line:
                logger.info(f"Found Colab tag at line {i}")
                # Mark this line and the next ones (img tag, closing a tag, and empty lines)
                j = i
                while j < len(source_lines):
                    lines_to_remove.append(j)
                    # Stop after finding the closing </a> tag
                    if '</a>' in source_lines[j]:
                        # Also remove trailing empty lines after the tag
                        k = j + 1
                        while k < len(source_lines) and source_lines[k].strip() == '':
                            lines_to_remove.append(k)
                            k += 1
                        break
                    j += 1
                modified = True
                break

        if modified:
            # Remove lines in reverse order to maintain correct indices
            for idx in sorted(lines_to_remove, reverse=True):
                source_lines.pop(idx)
            logger.info(f"Removed {len(lines_to_remove)} lines containing Colab tag")
        else:
            logger.info("No Colab tag found in first cell")

    if modified:
        logger.info(f"Writing modified notebook back to: {path}")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(notebook_as_json, f, indent=4)
        logger.info("Notebook updated successfully")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh the Colab tag in a notebook")
    parser.add_argument("notebook_url", help="Public GitHub notebook URL")
    args = parser.parse_args()

    logger.info(f"Processing notebook URL: {args.notebook_url}")

    parsed = urlparse(args.notebook_url)
    logger.info(f"Parsed URL - netloc: {parsed.netloc}, path: {parsed.path}")

    if parsed.netloc not in {"github.com", "www.github.com"}:
        logger.error(f"Invalid URL: Expected GitHub URL, got {parsed.netloc}")
        raise ValueError("Wrong URL: Must be a GitHub URL")

    # Extract the path parts after the repository name
    parts = [part for part in parsed.path.strip("/").split("/") if part][4:]
    logger.info(f"Extracted path parts: {parts}")

    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = str(BASE_DIR) + "/" + "/".join(parts)
    logger.info(f"Local notebook path: {file_path}")

    # Check if file exists
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Notebook not found at: {file_path}")

    # Remove existing tag
    remove_colab_tag(Path(file_path))

    # Call capture_tag.py to add the tag back
    logger.info("Calling capture_tag.py to regenerate the tag")
    capture_tag_script = Path(__file__).parent / "capture_tag.py"
    result = subprocess.run(
        ["python", str(capture_tag_script), args.notebook_url],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        logger.info("capture_tag.py executed successfully")
        logger.info(result.stdout)
    else:
        logger.error(f"capture_tag.py failed with error: {result.stderr}")
        raise RuntimeError("Failed to regenerate tag")

    logger.info("Process completed successfully!")


if __name__ == "__main__":
    main()
