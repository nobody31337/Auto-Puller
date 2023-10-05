import os
import sys
import git
import json
import time
import requests
import traceback
from datetime import datetime


def check_internet():
    response_code = 0

    while response_code != 200:
        try:
            response = requests.get('https://google.com')
            response_code = response.status_code
        except:
            print('Waiting for the internet connection...')
            time.sleep(5)
    
    return True


def repos_data_update():
    path = os.path.dirname(os.path.abspath(__file__))

    ret = {}

    try:
        with open(path + '/data.json', 'r') as js:
            ret = json.load(js)
    except:
        print('data.json not found...')
        exit(-1)
    
    return ret


def main():
    repos = repos_data_update()

    if 'repos' not in repos or len(repos['repos']) < 1:
        print('Please add repository data to the data.json file.')
        time.sleep(10)
        exit(-1)
    
    for repo_data in repos['repos']:
        try:
            repo = git.Repo(repo_data['path'])
        except:
            print(sys.exc_info()[1], end='\n\n')
            continue

        name = repo.working_tree_dir.split("\\")[-1].split("/")[-1]
        remote_name = repo_data['remote'] if 'remote' in repo_data else 'origin'
        if repo.bare:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tERROR: Bare repository is not supported.\n')
            continue
        
        try:
            remote = repo.remote(remote_name)
        except:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tERROR: Remote not found\n')
            continue

        print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tChecking for Github update...\n')

        try:
            remote.fetch()
        except:
            print(sys.exc_info()[1], end='\n\n')
            continue

        mode = repo_data['mode'] if 'mode' in repo_data else 'both'
        pullmode = mode in ('pull', 'both')
        pushmode = mode in ('push', 'both')

        if pullmode:
            before = list(repo.iter_commits('HEAD'))
            after = list(repo.iter_commits('FETCH_HEAD'))

            if before[0].hexsha != after[0].hexsha and before[0].count() <= after[0].count():
                print()
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tUpdate found in Github!\n')

                for commit in after[:-before[0].count()]:
                    print(commit.message.strip())

                remote.pull()
                remote.update()

                print(f'\n{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tRepository successfully updated!\n')
            else:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tUpdate not found\n')

        if pushmode:
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tLooking for changes to commit...\n')

            diff = repo.head.commit.diff(None)

            if len(diff) + len(repo.untracked_files) > 0:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tChanges found!\n')

                for change in diff:
                    repo.git.add(change.a_path)
                    if change.a_mode > 0 and change.b_mode > 0:
                        status = 'Update'
                    elif change.a_mode == 0 and change.b_mode > 0:
                        status = 'Create'
                    elif change.a_mode > 0 and change.b_mode == 0:
                        status = 'Delete'

                    commit_message = f'{status} {change.a_path}'

                    repo.index.commit(commit_message)

                    print(commit_message)

                for change in repo.untracked_files:
                    if os.path.isfile(repo.working_tree_dir + f'/{change}'):
                        status = 'Create'
                    else:
                        status = 'Delete'
                    repo.git.add(change)

                    commit_message = f'{status} {change}'

                    repo.index.commit(commit_message)

                    print(commit_message)
                
                print(f'\n{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tChanges successfully committed!\n')
            else:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tChanges not found\n')

            if len(list(repo.iter_commits(f'{remote_name}/{repo.active_branch.name}..{repo.active_branch.name}'))) > 0:
                remote.push()
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ]\n\tCommits successfully pushed to "{remote_name}"!\n')

    print('\n')


while check_internet():
    try:
        main()
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
    
    time.sleep(30)
