import os
from github import Github

CSV_FILE_PATH = "test.csv"
csv_file = "Column1,Column2\ntest,Data2\n"

g = Github(os.getenv("GITHUB_APP_TOKEN"))
repo = g.get_repo(str(os.getenv("GITHUB_REPOSITORY")))

try:
    existing_file = repo.get_contents(CSV_FILE_PATH)
    if not isinstance(existing_file, list):
        repo.update_file(existing_file.path, "Update CSV file", csv_file, existing_file.sha)
        print(f"{CSV_FILE_PATH} updated successfully.")
except Exception as e:
    repo.create_file(CSV_FILE_PATH, "Add generated CSV file", csv_file)
    print(f"{CSV_FILE_PATH} created successfully.")
