import json
import os

import github


with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
    event_data = json.load(f)
print(f"event_data:\n {event_data}")
pr_number = event_data.get("number") or event_data.get("inputs", {}).get("pr_number")
closed = event_data.get("action") == "closed"
pr_merged = event_data.get("pull_request", {}).get("merged")
print(f"pr_number: {pr_number}")
print(f"closed: {closed}")
print(f"pr_merged: {pr_merged}")


g = github.Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
pr = repo.get_pull(pr_number)

processed_files_path = "processed_files.json"
processed_files_branch = "processed_files"


try:
    branch = repo.get_branch(processed_files_branch)
except github.UnknownObjectException:
    repo.create_git_ref(
        ref=f"refs/heads/{processed_files_branch}",
        sha=repo.get_branch("main").commit.sha,
    )
    message = f"Initialize {processed_files_branch} with {processed_files_path}"
    repo.create_file(
        path=processed_files_path,
        message=message,
        content="{}",
        branch=processed_files_branch,
    )
    print(message)
    branch = repo.get_branch(processed_files_branch)

file_content = repo.get_contents(processed_files_path, ref=branch.commit.sha)
processed_files = file_content.decoded_content.decode()
with open(processed_files_path, "w") as f:
    f.write(processed_files)
print(f"processed_files:\n {processed_files}")

if os.path.exists(processed_files_path):
    with open(processed_files_path, "r") as file:
        file_data_json = json.load(file)
    file_data_json = {"test": "test"}
    with open(processed_files_path, "w") as file:
        json.dump(file_data_json, file)

with open(processed_files_path, "r") as file:
    file_data = file.read()

processed_files_content_file = repo.get_contents(
    processed_files_path, ref=processed_files_branch
)
message = f"Update {processed_files_path}"
repo.update_file(
    path=processed_files_path,
    message=message,
    content=file_data,
    sha=processed_files_content_file.sha,
    branch=processed_files_branch,
)
print(message)
print(file_data)
