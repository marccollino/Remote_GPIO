import os
import sys

def pullFromGit(branch):
    returnPackage = {'error': None}
    try:
        os.system(f'git pull origin {branch}')
        # Restart the script
        os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        returnPackage['error'] = f"An error occurred: {e}"
    return returnPackage