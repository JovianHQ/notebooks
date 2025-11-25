import argparse
import json
import logging
from pathlib import Path
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_colab_tag(github_url: str) -> str:
    """Generate a 'Run on Colab' HTML tag from a GitHub notebook URL."""
    logger.info(f"Generating Colab tag for URL: {github_url}")

    # Convert GitHub URL to Colab URL
    colab_url = github_url.replace("github.com", "colab.research.google.com/github")

    # Generate the HTML tag
    tag = (
        f'<a target="_blank" href="{colab_url}">\n'
        f'  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>\n'
        f'</a>'
    )

    logger.info("Generated Colab tag successfully")
    return tag


def fix_notebook(path: Path, tag: str):
    """Insert the Colab tag into the notebook's first cell."""
    logger.info(f"Opening notebook: {path}")

    with open(path) as f:
        notebook_as_json = json.load(f)
        logger.info(f"Notebook loaded successfully. Total cells: {len(notebook_as_json['cells'])}")

        # Insert tag at the beginning of the first cell
        notebook_as_json["cells"][0]["source"].insert(2, tag)
        notebook_as_json["cells"][0]["source"].insert(3, "\n")
        notebook_as_json["cells"][0]["source"].insert(4, "\n")
        logger.info("Tag inserted into first cell")

    logger.info(f"Writing modified notebook back to: {path}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook_as_json, f, indent=4)

    logger.info("Notebook updated successfully")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a Jovian notebook (.ipynb)")
    parser.add_argument("notebook_url", help="Public Jovian notebook URL")
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

    # Generate the Colab tag
    colab_tag = generate_colab_tag(args.notebook_url)
    logger.info(f"Generated tag:\n{colab_tag}")

    # Insert tag into notebook
    fix_notebook(Path(file_path), colab_tag)

    logger.info("Process completed successfully!")


if __name__ == "__main__":
    main()
