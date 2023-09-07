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
    while True:
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
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] ERROR: Bare repository is not supported.\n')
                continue
            
            try:
                remote = repo.remote(remote_name)
            except:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] ERROR: Remote not found\n')
                continue

            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Checking for Github update...')

            try:
                remote.fetch()
            except:
                print(sys.exc_info()[1], end='\n\n')
                continue

            before = list(repo.iter_commits('HEAD'))
            after = list(repo.iter_commits('FETCH_HEAD'))

            if before[0].hexsha != after[0].hexsha and before[0].count() < after[0].count():
                print()
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Update found in Github!')

                for commit in after[:-before[0].count()]:
                    print(commit.message)

                remote.pull()
                remote.update()

                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Repository successfully updated!\n')
            else:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Update not found\n')
        
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Looking for any change to commit...')

            diff = repo.head.commit.diff(None)

            if len(diff) + len(repo.untracked_files) > 0:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Changes found!')

                for change in diff:
                    repo.git.add(change.a_path)
                    if change.a_mode > 0 and change.b_mode > 0:
                        status = 'Update'
                    elif change.a_mode == 0 and change.b_mode > 0:
                        status = 'Create'
                    elif change.a_mode > 0 and change.b_mode == 0:
                        status = 'Delete'
                    
                    repo.index.commit(f'{status} {change.a_path}')

                    print(status, change.a_path)
                
                for change in repo.untracked_files:
                    if os.path.isfile(repo.working_tree_dir + f'/{change}'):
                        status = 'Create'
                    else:
                        status = 'Delete'
                    repo.git.add(change)

                    repo.index.commit(f'{status} {change}')

                    print(status, change)
                
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Changes successfully committed!\n')

            else:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Changes not found\n')

            if len(repo.git.log(f'{remote_name}/{repo.active_branch.name}..{repo.active_branch.name}')) > 0:
                remote.push()
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Commits successfully pushed to "{remote_name}"!\n')
        
        print('\n')
        time.sleep(30)


while check_internet():
    try:
        main()
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
