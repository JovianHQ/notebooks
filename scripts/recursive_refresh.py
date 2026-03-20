import argparse
import os
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Colab tags for all notebooks in a course")
    parser.add_argument("course_name", help="Course directory name")
    args = parser.parse_args()
    scripts_dir = Path(__file__).resolve().parent
    file_path = str(scripts_dir.parent) + "/" + args.course_name
    print(f"Script_path : {scripts_dir}/recursive_refresh.py")
    for assgn_courses in os.listdir(file_path):
        sec_path = file_path + "/" + assgn_courses
        for notebook in os.listdir(sec_path):
            notebook_url = f"https://github.com/JovianHQ/notebooks/blob/main/{args.course_name}/{assgn_courses}/{notebook}"
            print(notebook_url)
            result = subprocess.run(
                ["python", f"{scripts_dir}/refresh_tag.py", notebook_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy(),  # important for Firefox/Selenium
            )
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.returncode != 0:
                print(
                    f"ERROR: refresh_tag.py failed with return code {result.returncode}"
                )
            print(f"Done for {notebook_url}")


if __name__ == "__main__":
    main()
