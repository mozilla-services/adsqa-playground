import os
import requests

def get_commit_hashes(owner, repo, file_path, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {'Authorization': f'token {token}'} if token else {}
    params = {'path': file_path}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    commits = response.json()

    # Extract the latest and the previous commit hashes
    latest_commit = commits[0]['sha'] if commits else None
    previous_commit = commits[1]['sha'] if len(commits) > 1 else None
    return latest_commit, previous_commit


def fetch_file_content(owner, repo, commit_hash, file_path, token=None):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{commit_hash}/{file_path}"
    headers = {'Authorization': f'token {token}'} if token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


def save_content_to_file(content, file_path):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "mars", "Automation") # This folder can be changed
    if not os.path.exists(desktop_path):
        os.makedirs(desktop_path)

    save_path = os.path.join(desktop_path, file_path)
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"File saved locally: {save_path}")


def main():
    owner = "mozilla-services"
    repo = "quicksuggest-rs"
    file_path = "source-data/overview.txt"
    token = "INSERT YOUR TOKEN HERE"  # GitHub token for authenticated requests

    # Get latest and previous commit hashes
    latest_commit, previous_commit = get_commit_hashes(owner, repo, file_path, token)

    if latest_commit:
        # Fetch content of latest version
        latest_content = fetch_file_content(owner, repo, latest_commit, file_path, token)
        save_content_to_file(latest_content, "latest.txt")

        latest_file_url = f"https://github.com/{owner}/{repo}/blob/{latest_commit}/{file_path}"
        print(f"Latest version URL: {latest_file_url}")
    else:
        print("Could not fetch the latest version URL.")

    if previous_commit:
        # Fetch content of previous version
        previous_content = fetch_file_content(owner, repo, previous_commit, file_path, token)
        save_content_to_file(previous_content, "previous.txt")

        previous_file_url = f"https://github.com/{owner}/{repo}/blob/{previous_commit}/{file_path}"
        print(f"Previous version (-1) URL: {previous_file_url}")
    else:
        print("No previous version (-1) available.")


if __name__ == "__main__":
    main()

def read_lines(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def parse_categories(lines):
    categories = {}
    current_title = None

    for line in lines:
        if line.startswith("title:"):
            current_title = line.replace("title: ", "").strip()
            if current_title not in categories:
                categories[current_title] = []
        elif line.startswith("http"):
            continue  # Skip the URL lines
        elif current_title:
            keywords = line.split(',')
            categories[current_title].extend(keywords)

    return categories

def compare_files(oldfile, newfile, output_file):
    lines1 = read_lines(oldfile)
    lines2 = read_lines(newfile)

    categories1 = parse_categories(lines1)
    categories2 = parse_categories(lines2)

    with open(output_file, 'w') as file:
        # Compare categories in oldfile with newfile
        for title in categories1.keys():
            keywords1 = categories1.get(title, [])
            keywords2 = categories2.get(title, [])

            added_keywords = [keyword for keyword in keywords2 if keyword not in keywords1]
            removed_keywords = [keyword for keyword in keywords1 if keyword not in keywords2]

            if added_keywords or removed_keywords:
                file.write(f"title: {title}\n")
                if added_keywords:
                    added_keywords_cleaned = [keyword for keyword in added_keywords if keyword.strip()]
                    if added_keywords_cleaned:
                        file.write(f"added: {', '.join(added_keywords_cleaned)}.\n")
                if removed_keywords:
                    removed_keywords_cleaned = [keyword for keyword in removed_keywords if keyword.strip()]
                    if removed_keywords_cleaned:
                        file.write(f"removed: {', '.join(removed_keywords_cleaned)}.\n")
                file.write("\n")

        # Compare categories in newfile that are not in oldfile
        for title in categories2.keys():
            if title not in categories1:
                keywords2 = categories2.get(title, [])
                added_keywords_cleaned = [keyword for keyword in keywords2 if keyword.strip()]
                if added_keywords_cleaned:
                    file.write(f"title: {title}\n")
                    file.write(f"added: {', '.join(added_keywords_cleaned)}.\n")
                    file.write("\n")

if __name__ == "__main__":
    oldfile = "previous.txt"
    newfile = "latest.txt"
    output_file = "differences.txt"
    compare_files(oldfile, newfile, output_file)
