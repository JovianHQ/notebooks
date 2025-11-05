#!/usr/bin/env python3
"""
Download all notebooks associated with a Jovian lesson page.

The script scrapes the lesson page for notebook links (the "Open in new tab" menu
entries) and reuses download-notebook.py to fetch each notebook.

Example:
    python scripts/download-lesson.py \\
        https://jovian.com/learn/deep-learning-with-pytorch-zero-to-gans/lesson/lesson-5-data-augmentation-regularization-and-resnets
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Set
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("download-lesson")
DOWNLOAD_SCRIPT = Path(__file__).resolve().parent / "download-notebook.py"


def mask_token(token: str, visible: int = 4) -> str:
    """Return a partially masked token representation for logs."""
    if not token:
        return ""
    if len(token) <= visible * 2:
        return token[0] + "***" + token[-1]
    return f"{token[:visible]}...{token[-visible:]}"


def load_env_file(env_path: Path) -> dict:
    """Load key-value pairs from a .env file without external dependencies."""
    env_vars: dict = {}
    if not env_path.exists():
        LOGGER.debug("No .env file found at %s", env_path)
        return env_vars

    LOGGER.debug("Reading .env file from %s", env_path)
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            LOGGER.debug("Skipping malformed line in .env: %s", raw_line)
            continue
        key, value = line.split("=", maxsplit=1)
        env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


def resolve_env_token(env_var: str) -> str:
    """Retrieve the Jovian auth token from environment variables or nearby .env."""
    token = os.getenv(env_var)
    if token:
        LOGGER.debug(
            "Found %s in environment variables (value looks like %s)",
            env_var,
            mask_token(token),
        )
        return token

    current = Path.cwd()
    for candidate in [current, *current.parents]:
        env_file = candidate / ".env"
        env_vars = load_env_file(env_file)
        token = env_vars.get(env_var)
        if token:
            LOGGER.debug(
                "Found %s in %s (value looks like %s)",
                env_var,
                env_file,
                mask_token(token),
            )
            return token

    raise RuntimeError(
        f"Failed to locate {env_var}. Set it as an environment variable or define it inside a .env file."
    )


def configure_logging(verbose: bool = False) -> None:
    """Configure console logging with optional verbose mode."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


class LessonNotebookLinkParser(HTMLParser):
    """Parse lesson HTML and collect notebook links from 'Open in new tab' anchors."""

    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []
        self._current_href: str = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        self._current_href = attrs_dict.get("href", "")

    def handle_endtag(self, tag):
        if tag.lower() == "a":
            self._current_href = ""

    def handle_data(self, data):
        if not self._current_href:
            return
        if "open in new tab" in data.strip().lower():
            LOGGER.debug("Found notebook link candidate: %s", self._current_href)
            self.links.append(self._current_href)


def fetch_html(url: str, token: str, retries: int = 3) -> str:
    """Fetch HTML content from the lesson URL with basic retry logic."""
    headers = {
        # Use a simple user agent to avoid being blocked by basic bot filters.
        "User-Agent": "Mozilla/5.0 (compatible; JovianLessonDownloader/1.0)",
        "Authorization": f"Bearer {token}",
    }
    LOGGER.debug(
        "Lesson page request headers: %s",
        {"User-Agent": headers["User-Agent"], "Authorization": f"Bearer {mask_token(token)}"},
    )
    request = Request(url, headers=headers)

    attempt = 0
    while True:
        attempt += 1
        try:
            with urlopen(request, timeout=30) as response:
                content_bytes = response.read()
            return content_bytes.decode("utf-8", errors="replace")
        except HTTPError as http_err:
            raise RuntimeError(f"HTTP error while fetching lesson page: {http_err}") from http_err
        except URLError as url_err:
            if attempt >= retries:
                raise RuntimeError(
                    f"Network error while fetching lesson page after {retries} attempts: {url_err}"
                ) from url_err
            wait_seconds = 2 ** (attempt - 1)
            LOGGER.warning(
                "Network error while fetching lesson page (attempt %s/%s): %s. Retrying in %s seconds...",
                attempt,
                retries,
                url_err,
                wait_seconds,
            )
            time.sleep(wait_seconds)


def parse_notebook_links(lesson_url: str, html: str) -> List[str]:
    """Extract notebook URLs from the lesson HTML."""
    parser = LessonNotebookLinkParser()
    parser.feed(html)

    absolute_links: List[str] = []
    seen: Set[str] = set()
    for href in parser.links:
        absolute = urljoin(lesson_url, href)
        if absolute in seen:
            continue
        seen.add(absolute)
        absolute_links.append(absolute)
        LOGGER.debug("Normalized notebook URL: %s", absolute)

    return absolute_links


def lesson_slug_from_url(url: str) -> str:
    """Extract the final segment after the last slash as the lesson slug."""
    parsed = urlparse(url)
    slug = Path(parsed.path).name
    if not slug:
        raise ValueError("Lesson URL must end with a valid slug name.")
    return slug


def invoke_download_notebook(
    notebook_url: str,
    destination_dir: Path,
    token_env: str,
    verbose: bool,
) -> None:
    """Invoke download-notebook.py via subprocess to download the notebook."""
    command = [
        sys.executable,
        str(DOWNLOAD_SCRIPT),
        notebook_url,
        str(destination_dir),
        "--token-env",
        token_env,
    ]
    if verbose:
        command.append("--verbose")

    LOGGER.info("Downloading notebook via download-notebook.py: %s", notebook_url)
    print(f"[debug] Running download-notebook.py for: {notebook_url}")
    LOGGER.debug("Executing command: %s", " ".join(command))

    result = subprocess.run(command, check=False, capture_output=not verbose, text=True)
    if result.returncode != 0:
        if not verbose:
            LOGGER.error("download-notebook.py stderr: %s", result.stderr.strip())
        raise RuntimeError(
            f"Failed to download notebook {notebook_url}. Exit code: {result.returncode}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download all notebooks for a given Jovian lesson URL."
    )
    parser.add_argument("lesson_url", help="Jovian lesson URL")
    parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Root directory to store the lesson folder (defaults to current directory)",
    )
    parser.add_argument(
        "--token-env",
        default="AUTH_TOKEN",
        help="Environment variable key used for the Jovian API token",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    configure_logging(verbose=args.verbose)

    if not DOWNLOAD_SCRIPT.exists():
        LOGGER.error(
            "Required helper script download-notebook.py not found at %s",
            DOWNLOAD_SCRIPT,
        )
        raise SystemExit(1)

    try:
        token = resolve_env_token(args.token_env)
    except RuntimeError as err:
        LOGGER.error("%s", err)
        raise SystemExit(1) from err

    try:
        slug = lesson_slug_from_url(args.lesson_url)
    except ValueError as err:
        LOGGER.error("Invalid lesson URL: %s", err)
        raise SystemExit(1) from err

    lesson_root = Path(args.destination).expanduser().resolve()
    lesson_dir = lesson_root / slug

    if not lesson_dir.exists():
        LOGGER.info("Creating lesson destination folder %s", lesson_dir)
        lesson_dir.mkdir(parents=True, exist_ok=True)
        print(f"[debug] Created lesson folder: {lesson_dir}")

    try:
        html = fetch_html(args.lesson_url, token=token)
    except RuntimeError as err:
        LOGGER.error("%s", err)
        raise SystemExit(1) from err

    notebook_urls = parse_notebook_links(args.lesson_url, html)
    if not notebook_urls:
        LOGGER.error("No notebook links found on the lesson page.")
        raise SystemExit(1)

    LOGGER.info("Found %s notebook link(s) on the lesson page.", len(notebook_urls))
    print(f"[debug] Notebook links discovered: {len(notebook_urls)}")

    for index, notebook_url in enumerate(notebook_urls, start=1):
        LOGGER.info("Processing notebook %s/%s: %s", index, len(notebook_urls), notebook_url)
        print(f"[debug] Processing notebook {index}/{len(notebook_urls)}: {notebook_url}")
        try:
            invoke_download_notebook(
                notebook_url=notebook_url,
                destination_dir=lesson_dir,
                token_env=args.token_env,
                verbose=args.verbose,
            )
        except RuntimeError as err:
            LOGGER.error("%s", err)
            raise SystemExit(1) from err

    LOGGER.info("All notebooks downloaded successfully into %s", lesson_dir)
    print(f"[debug] Completed downloading all notebooks into: {lesson_dir}")


if __name__ == "__main__":
    main()
