import os
from pathlib import Path

from pydriller import RepositoryMining, GitRepository

"""
This script mines off-by-one errors from a specified 
local directory containing Java project repositories
"""

home = str(Path.home())
# @TODO add this to configuration
# Path containing GitHub repositories of Java projects
dataset_path = os.path.join(home, "ml4se_dataset", "unique_mining")
project_names = os.listdir(dataset_path)

print("Starting to look through projects")
for project_name in project_names:
    path = os.path.join(dataset_path, project_name)
    repository_mining = RepositoryMining(path)
    # print("Starting to analyze commits for {}".format(path))
    try:
        for commit in repository_mining.traverse_commits():
            gr = GitRepository(repository_mining.path_to_repo[0])
            for modified_file in commit.modifications:
                if modified_file.filename.endswith(".java"):
                    diff = modified_file.diff
                    parsed_diff = gr.parse_diff(diff)

                    lines_containing_less_or_equal = []
                    lines_containing_less = []
                    lines_containing_greater_or_equal = []
                    lines_containing_greater = []
                    for deletion in parsed_diff['deleted']:
                        line_nr = deletion[0]
                        content = deletion[1]
                        if " <= " in content:
                            lines_containing_less_or_equal.append(line_nr)
                        if " < " in content:
                            lines_containing_less.append(line_nr)
                        if " >= " in content:
                            lines_containing_greater_or_equal.append(line_nr)
                        if " > " in content:
                            lines_containing_greater.append(line_nr)

                    for addition in parsed_diff['added']:
                        line_nr = addition[0]
                        content = addition[1]
                        # <= to <
                        if line_nr in lines_containing_less_or_equal and " < " in content:
                            print(modified_file.filename + ":" + str(addition[0]))
                            print("<= to <")
                            print(gr.repo.remotes.origin.url[:-4] + "/commit/" + commit.hash)
                        # < to <=
                        if line_nr in lines_containing_less and " <= " in content:
                            print(modified_file.filename + ":" + str(addition[0]))
                            print("< to <=")
                            print(gr.repo.remotes.origin.url[:-4] + "/commit/" + commit.hash)
                        # >= to >
                        if line_nr in lines_containing_greater_or_equal and " > " in content:
                            print(modified_file.filename + ":" + str(addition[0]))
                            print(">= to >")
                            print(gr.repo.remotes.origin.url[:-4] + "/commit/" + commit.hash)
                        # > to >=
                        if line_nr in lines_containing_greater and " >= " in content:
                            print(modified_file.filename + ":" + str(addition[0]))
                            print("> to >=")
                            print(gr.repo.remotes.origin.url[:-4] + "/commit/" + commit.hash)
    except Exception as e:
        print("Could not scan project: {}. Skipping it.".format(project_name))
        continue
