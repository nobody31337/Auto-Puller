import git
import time

with open('repos.txt', 'r') as f:
    repos = list(map(lambda line: line.strip(), f.readlines()))

while len(repos) > 0:
    for repo in repos:
        repo = git.Repo(repo)
        name = repo.working_tree_dir.split("\\")[-1].split("/")[-1]

        print(f'[ GIT UPDATE CHECK: {name} ] Checking for Github update...')

        if repo.bare:
            print(f'[ GIT UPDATE CHECK: {name} ] ERROR: Bare repository is not supported.\n')
            continue
        
        try:
            remote = repo.remote()
        except:
            print(f'[ GIT UPDATE CHECK: {name} ] ERROR: Remote not found\n')
            continue

        remote.fetch()

        before = list(repo.iter_commits('HEAD'))
        after = list(repo.iter_commits('FETCH_HEAD'))

        if before[0].hexsha != after[0].hexsha:
            print(f'[ GIT UPDATE CHECK: {name} ] Update found in Github!')

            remote.pull()
            remote.update()

            print(f'[ GIT UPDATE CHECK: {name} ] Repository successfully updated!\n')
        else:
            print(f'[ GIT UPDATE CHECK: {name} ] Update not found\n')
    
    with open('repos.txt', 'r') as f:
        repos = list(map(lambda line: line.strip(), f.readlines()))

    time.sleep(60)
