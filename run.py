import os
import git
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
            print('Internet connection lost.')
            print('Waiting for the internet connection...')
            time.sleep(5)
    
    return True


def repos_data_update():
    path = os.path.dirname(os.path.abspath(__file__))

    ret = []
    try:
        with open(path + '/repos.txt', 'r') as f:
            for line in map(lambda line: line.strip(), f.readlines()):
                if not line.startswith('#') and len(line) > 0:
                    ret.append(line)
    except:
        print('repos.txt not found...')
        exit(-1)
    
    return ret


def main():
    repos = repos_data_update()

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

            if before[0].hexsha != after[0].hexsha and before[0].count() < after[0].count():
                print()
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Update found in Github!')

                remote.pull()
                remote.update()

                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Repository successfully updated!\n')
            else:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Update not found\n')
        
            print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Looking for any change to push...')

            diff = list(reversed(repo.head.commit.diff(None)))

            if len(diff) > 0:
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
                
                remote.push()
                
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Changes successfully committed!')
            else:
                print(f'{datetime.now():%Y-%m-%d %H:%M:%S} [ GIT UPDATE CHECK: {name} ] Changed not found\n')
            
            repos = repos_data_update()

        time.sleep(30)


while check_internet():
    try:
        main()
    except KeyboardInterrupt:
        exit()
    except:
        traceback.print_exc()
