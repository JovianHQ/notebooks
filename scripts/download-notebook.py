#!/usr/bin/env python3
"""
Download a Jovian notebook (.ipynb) by providing the public notebook URL.

Example:
    python scripts/download-notebook.py https://jovian.com/aakashns/first-steps-with-python .
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("download-notebook")


def mask_token(token: str, visible: int = 4) -> str:
    """Return a partially masked representation of a token for logging."""
    if not token:
        return ""
    if len(token) <= visible * 2:
        return token[0] + "***" + token[-1]
    return f"{token[:visible]}...{token[-visible:]}"


def configure_logging(verbose: bool = False) -> None:
    """Configure console logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Load a minimal .env file into a dict (no external dependencies)."""
    env_vars: Dict[str, str] = {}
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


def resolve_env_token(env_var: str = "AUTH_TOKEN") -> str:
    """Locate the Jovian API token from environment variables or a .env file."""
    token = os.getenv(env_var)
    if token:
        LOGGER.debug(
            "Found %s in environment variables (value looks like %s)",
            env_var,
            mask_token(token),
        )
        return token

    # Search for a .env file starting from current working directory upwards.
    current = Path.cwd()
    for candidate in [current, *current.parents]:
        env_file = candidate / ".env"
        token = load_env_file(env_file).get(env_var)
        if token:
            LOGGER.debug(
                "Found %s in %s (value looks like %s)",
                env_var,
                env_file,
                mask_token(token),
            )
            return token

    raise RuntimeError(
        f"Failed to locate {env_var}. Set it as an environment variable "
        "or define it inside a .env file."
    )


def parse_notebook_url(url: str) -> Tuple[str, str]:
    """Extract the username and notebook slug from the Jovian notebook URL."""
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        raise ValueError("Notebook URL must start with http:// or https://")

    if parsed.netloc not in {"jovian.com", "www.jovian.com"}:
        raise ValueError("Notebook URL must point to jovian.com")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError("Notebook URL must follow the form https://jovian.com/<user>/<slug>")

    username, slug = parts[0], parts[1]
    LOGGER.debug("Parsed username=%s, slug=%s from %s", username, slug, url)
    return username, slug


def fetch_notebook_metadata(username: str, slug: str, token: str, retries: int = 3) -> Dict[str, str]:
    """Call the Jovian metadata API to retrieve notebook details."""
    api_url = f"https://api.jovian.com/user/{username}/gist/{slug}"
    LOGGER.info("Fetching notebook metadata from %s", api_url)

    headers = {"Authorization": f"Bearer {token}"}
    sanitized_headers = {
        key: "Bearer " + mask_token(token) if key == "Authorization" else value
        for key, value in headers.items()
    }
    LOGGER.debug("Request headers: %s", sanitized_headers)
    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(
            "cURL command: curl -H 'Authorization: Bearer %s' %s",
            token,
            api_url,
        )
    request = Request(api_url, headers=headers)

    attempt = 0
    while True:
        attempt += 1
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
            break
        except HTTPError as http_err:
            raise RuntimeError(f"HTTP error while fetching metadata: {http_err}") from http_err
        except URLError as url_err:
            if attempt >= retries:
                raise RuntimeError(f"Network error while fetching metadata after {retries} attempts: {url_err}") from url_err
            wait_seconds = 2 ** (attempt - 1)
            LOGGER.warning(
                "Network error while fetching metadata (attempt %s/%s): %s. Retrying in %s seconds...",
                attempt,
                retries,
                url_err,
                wait_seconds,
            )
            time.sleep(wait_seconds)

    try:
        metadata = json.loads(payload)
    except json.JSONDecodeError as decode_err:
        raise RuntimeError("Received invalid JSON from Jovian API") from decode_err

    LOGGER.debug("Metadata response keys: %s", ", ".join(metadata.keys()))
    return metadata


def download_file(raw_url: str, destination: Path, retries: int = 3) -> None:
    """Download the notebook content from raw_url to the destination path."""
    LOGGER.info("Downloading notebook content to %s", destination)
    request = Request(raw_url)
    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug("cURL command: curl -L %s -o %s", raw_url, destination)

    attempt = 0
    while True:
        attempt += 1
        try:
            with urlopen(request, timeout=60) as response:
                content = response.read()
            break
        except HTTPError as http_err:
            raise RuntimeError(f"HTTP error while downloading notebook: {http_err}") from http_err
        except URLError as url_err:
            if attempt >= retries:
                raise RuntimeError(
                    f"Network error while downloading notebook after {retries} attempts: {url_err}"
                ) from url_err
            wait_seconds = 2 ** (attempt - 1)
            LOGGER.warning(
                "Network error while downloading notebook (attempt %s/%s): %s. Retrying in %s seconds...",
                attempt,
                retries,
                url_err,
                wait_seconds,
            )
            time.sleep(wait_seconds)

    destination.write_bytes(content)
    LOGGER.info("Downloaded notebook saved at %s", destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a Jovian notebook (.ipynb)")
    parser.add_argument("notebook_url", help="Public Jovian notebook URL")
    parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Download directory (defaults to current directory)",
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

    try:
        username, slug = parse_notebook_url(args.notebook_url)
    except ValueError as err:
        LOGGER.error("Invalid notebook URL: %s", err)
        raise SystemExit(1) from err

    try:
        token = resolve_env_token(args.token_env)
    except RuntimeError as err:
        LOGGER.error("%s", err)
        raise SystemExit(1) from err

    try:
        metadata = fetch_notebook_metadata(username, slug, token)
    except RuntimeError as err:
        LOGGER.error("%s", err)
        raise SystemExit(1) from err

    data = metadata.get("data") if isinstance(metadata, dict) else None
    raw_url = None
    if isinstance(data, dict):
        raw_url = data.get("rawUrl")
    else:
        LOGGER.debug("Unexpected metadata format: %s", type(metadata).__name__)
    if not raw_url:
        LOGGER.error("Missing rawUrl in API response. Cannot download notebook.")
        raise SystemExit(1)

    destination_dir = Path(args.destination).expanduser().resolve()
    if not destination_dir.exists():
        LOGGER.info("Creating destination directory %s", destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{slug}.ipynb" if not slug.endswith(".ipynb") else slug
    destination_path = destination_dir / filename

    try:
        download_file(raw_url, destination_path)
    except RuntimeError as err:
        LOGGER.error("%s", err)
        raise SystemExit(1) from err

    LOGGER.info("Notebook download completed successfully.")


if __name__ == "__main__":
    main()
