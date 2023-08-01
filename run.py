import os
import git
import time
from datetime import datetime

def repos_data_update():
    global repos

    path = os.path.dirname(os.path.abspath(__file__))

    with open(path + '/repos.txt', 'r') as f:
        repos = []
        for line in map(lambda line: line.strip(), f.readlines()):
            if not line.startswith('#') and len(line) > 0:
                repos.append(line)

repos = []

repos_data_update()

while len(repos) > 0:
    for repo in repos:
        repo = git.Repo(repo)
        name = repo.working_tree_dir.split("\\")[-1].split("/")[-1]

        if repo.bare:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] ERROR: Bare repository is not supported.\n')
            continue
        
        try:
            remote = repo.remote()
        except:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] ERROR: Remote not found\n')
            continue

        print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Checking for Github update...')

        remote.fetch()

        before = list(repo.iter_commits('HEAD'))
        after = list(repo.iter_commits('FETCH_HEAD'))

        if before[0].hexsha != after[0].hexsha:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Update found in Github!')

            remote.pull()
            remote.update()

            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Repository successfully updated!\n')
        else:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Update not found\n')
    
    repos_data_update()

    time.sleep(60)
