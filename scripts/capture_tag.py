import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


def fix_notebook(path: Path, tag: str):
    with open(path) as f:
        notebook_as_json = json.load(f)
        notebook_as_json["cells"][0]["source"].insert(2, tag)
        notebook_as_json["cells"][0]["source"].insert(3, "\n")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook_as_json, f, indent=4)


def main() -> None:
    options = Options()
    options.add_argument("--headless")
    parser = argparse.ArgumentParser(description="Download a Jovian notebook (.ipynb)")
    parser.add_argument("notebook_url", help="Public Jovian notebook URL")
    args = parser.parse_args()
    parsed = urlparse(args.notebook_url)
    # print(parsed)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        raise ValueError("Wrong URL")

    parts = [part for part in parsed.path.strip("/").split("/") if part][4:]
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = str(BASE_DIR) + "/" + "/".join(parts)
    # print(f"file_path: {file_path}")
    # print(parts)
    # print("Starting the Web Driver...")
    driver = webdriver.Firefox(options=options)
    driver.get("https://openincolab.com")
    input_el = driver.find_element(By.ID, "repo")
    input_el.clear()
    # print("Processing elements and sending keys")
    input_el.send_keys(args.notebook_url)
    print("Input element found:")
    # print("Retrieving elements")
    input_el.send_keys(Keys.ENTER)
    a_tag = driver.find_element(By.TAG_NAME, "textarea")
    fix_notebook(Path(file_path), a_tag.text)
    print("Extracted HTML")
    print(a_tag.text)
    driver.quit()


if __name__ == "__main__":
    main()
