import os
from github import Github

CSV_FILE_PATH = "test.csv"

with open(CSV_FILE_PATH, "w") as f:
    f.write("Column1,Column2\n")
    f.write("Data1,Data2\n")

g = Github(os.getenv("GITHUB_APP_TOKEN"))

repo = g.get_repo(str(os.getenv("GITHUB_REPOSITORY")))

with open(CSV_FILE_PATH, "r") as f:
    content = f.read()

try:
    existing_files = repo.get_contents(CSV_FILE_PATH)
    existing_file = existing_files[0] if isinstance(existing_files, list) else existing_files
    repo.update_file(existing_file.path, "Update CSV file", content, existing_file.sha)
    print("File updated successfully.")
except Exception as e:
    repo.create_file(CSV_FILE_PATH, "Add generated CSV file", content)
    print("File created successfully.")
