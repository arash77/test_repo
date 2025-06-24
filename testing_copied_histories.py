import csv
import io
import os
from datetime import datetime

import requests
from github import Github

starts_with = os.getenv("STARTS_WITH", "").strip()
given_history_id = os.getenv("HISTORY_ID", "").strip()
api_key = os.getenv("GALAXY_API_KEY", "").strip()

session = requests.Session()
session.headers.update({"x-api-key": api_key})


def get_request(url):
    try:
        resp = session.get("https://usegalaxy.eu/api/" + url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return {}


def get_username_slug(history_id):
    data = get_request(f"histories/{history_id}")
    return (
        data.get("username", ""),
        data.get("username_and_slug", ""),
        data.get("name", ""),
    )


def get_shared_histories():
    return get_request("histories/shared_with_me")


def get_dataset_collections(history_id, dataset_collection_id):
    data = get_request(
        f"histories/{history_id}/dataset_collections/{dataset_collection_id}"
    )
    datasets = {}
    for element in data.get("elements", []):
        if element.get("element_type") == "dataset_collection":
            nested_data = get_dataset_collections(history_id, element["object"]["id"])
            if nested_data:
                return nested_data
        if element.get("element_type") == "hda":
            datasets.update({element["object"]["id"]: element["object"]["name"]})
    return datasets


def get_history_dataset(history_id):
    datasets = {}
    username, slug, history_name = get_username_slug(history_id)
    for item in get_request(f"histories/{history_id}/contents"):
        if item.get("state") != "ok":
            continue
        if item.get("history_content_type") == "dataset_collection":
            collection_datasets = get_dataset_collections(history_id, item.get("id"))
            datasets.update(collection_datasets)
        if item.get("history_content_type") == "dataset":
            datasets.update({item["id"]: item["name"]})
    return datasets, username, slug, history_name


def check_inheritance_chain(dataset_id):
    return get_request(f"datasets/{dataset_id}/inheritance_chain")


def main():
    shared_histories = get_shared_histories() if not given_history_id else []
    if given_history_id:
        histories = {given_history_id}
    else:
        histories = (
            {
                h["id"]
                for h in shared_histories
                if h.get("name", "").startswith(starts_with)
            }
            if starts_with
            else {h["id"] for h in shared_histories}
        )

    rows = []
    for history_id in histories:
        print(f"\nProcessing History: {history_id}")
        try:
            datasets, username, slug, history_name = get_history_dataset(history_id)
            print(f"Found {len(datasets)} datasets in history '{history_name}'")
        except Exception as e:
            print(f"Error fetching datasets: {e}")
            continue
        for dataset_id, dataset_name in datasets.items():
            try:
                print(f"Checking dataset: {dataset_id} ({dataset_name})")
                inheritance_chain = check_inheritance_chain(dataset_id)
                if inheritance_chain:
                    rows.append(
                        {
                            "username": username,
                            "url_to_history": f"https://usegalaxy.eu/{slug}",
                            "history_id": history_id,
                            "history_name": history_name,
                            "dataset_id": dataset_id,
                            "dataset_name": dataset_name,
                            "inheritance_chain": "; ".join(
                                [
                                    f"{item.get('name', '')} ({item.get('dep', '')})"
                                    for item in inheritance_chain
                                ]
                            ),
                        }
                    )
            except Exception as e:
                print(f"Error checking inheritance chain: {e}")

    if not rows:
        print("No inheritance chains found.")
        return

    fieldnames = [
        "username",
        "url_to_history",
        "history_id",
        "history_name",
        "dataset_id",
        "dataset_name",
        "inheritance_chain",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    content = buffer.getvalue()
    buffer.close()

    file_name = f"inheritance_chains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    g = Github(os.getenv("GITHUB_TOKEN", ""))
    repo = g.get_repo(os.getenv("GITHUB_REPO", ""))
    commit_message = (
        f"Add inheritance chains for histories starting with '{starts_with}'"
        if starts_with
        else f"Add inheritance chains for history ID {given_history_id}"
    )
    try:
        repo.create_file(
            file_name,
            commit_message,
            content,
            branch="inheritance-chains",
        )
    except Exception as e:
        print(f"Error uploading file to GitHub: {e}")


if __name__ == "__main__":
    try:
        main()
    finally:
        session.close()
