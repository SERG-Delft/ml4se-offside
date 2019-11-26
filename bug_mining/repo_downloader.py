import json
import os
from pathlib import Path

import git
import requests

"""
This script downloads the top 500 GitHub Java project with most stars to local storage
"""

URLs = []
for page_nr in range(1, 11):
    print("Making request #{}".format(page_nr))
    myResponse = requests.get(
        "https://api.github.com/search/repositories?q=+language:java&sort=stars&order=desc&page={}&per_page=50".format(
            page_nr))
    if (myResponse.ok):
        jData = json.loads(myResponse.content)
        for repo in jData['items']:
            URLs.append(repo['html_url'])
    else:
        myResponse.raise_for_status()

home = str(Path.home())
# @TODO add this to configuration
dataset_path = os.path.join(home, "ml4se_dataset", "mining")
repo_nr = 1
for URL in URLs:
    clone_dir = os.path.join(dataset_path, URL.split("/")[-1])
    print("Starting to clone repo #{}: {} to {}".format(repo_nr, URL, clone_dir))
    if (os.path.isdir(clone_dir)):
        print("Clone of already exists. Skipping")
    else:
        print("Downloading repo. Please wait...")
        git.Repo.clone_from("{}.git".format(URL), clone_dir)
    repo_nr += 1
