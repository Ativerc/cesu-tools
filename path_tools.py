from pathlib import Path

import constants

def path_exists_check(receivedpath):
    if Path(receivedpath).exists():
        return True
    else:
        # raise PathDoesntExistError
        return False

def create_path(receivedpath):
    Path(receivedpath).mkdir(parents=True, exist_ok=True) # TODO Needs checks!