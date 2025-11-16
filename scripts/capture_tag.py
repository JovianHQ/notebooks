import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


def main() -> None:
    options = Options()
    options.add_argument("--headless")
    parser = argparse.ArgumentParser(description="Download a Jovian notebook (.ipynb)")
    parser.add_argument("notebook_url", help="Public Jovian notebook URL")
    args = parser.parse_args()
    # print("Starting the Web Driver...")
    driver = webdriver.Firefox(options=options)

    driver.get("https://openincolab.com")
    input_el = driver.find_element(By.ID, "repo")
    input_el.clear()
    # print("Processing elements and sending keys")
    input_el.send_keys(args.notebook_url)
    # print("Retrieving elements")
    input_el.send_keys(Keys.ENTER)
    a_tag = driver.find_element(By.TAG_NAME, "textarea")
    print(a_tag.text)
    driver.quit()


if __name__ == "__main__":
    main()
