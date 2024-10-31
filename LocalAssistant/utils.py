import pathlib
import shutil
import json
import os

# Path
PROJECT_PATH: str = pathlib.Path(__file__).parent
MODEL_PATH: str = PROJECT_PATH / 'models'
USER_PATH: str = PROJECT_PATH / 'users'

# Custom Exception
class LocalAssistantException(Exception):
    """
    For common errors in MyAssistant
    """
    pass

def _clean_cache(path: str, verbose: bool) -> None:
    """
    delete choosen .cache dir (Too dangerous to be used)
    """
    try:
        shutil.rmtree(path)
        if verbose:
            print(f'Cleaned {path}.')
    except: # it doesn't matter
        if verbose:
            print(f'Cannot find {path}, skipped.')

def clean_all_cache(verbose: bool) -> None:
    """
    delete all .cache dir
    """
    for path in (
        MODEL_PATH / '.cache',
    ):
        _clean_cache(path, verbose)
        
# it happens that i'm too smart.
def _print_dict(data: dict, level: int=0):
    for key, value in data.items():
        if isinstance(value, str):
            print(level*'   ' + f"'{key}': '{value}',")
        else: # value is dict
            print(level*'   ' + "%r: {" % (key))
            _print_dict(value, level+1)
            print(level*'   ' + "},")
        
class LocalAssistantConfig:
    PATH: str = PROJECT_PATH / 'locas_config.json'
    DATA: dict = {}
        
    def upload_config_file(self, verbose: bool) -> None:
        # dump data to file.
        with open(self.PATH, mode="w", encoding="utf-8") as write_file:
            json.dump(self.DATA, write_file, indent=4)
            write_file.close()

        if verbose:
            print("Uploaded current data to config.json file.")

    def get_config_file(self, verbose: bool) -> None:
        try:
            if verbose:
                print('Finding locas_config.json file.')

            # Read the data
            with open(self.PATH, mode="r", encoding="utf-8") as read_file:
                self.DATA = json.load(read_file)
                read_file.close()

            if verbose:
                print('Found locas_config.json file.')
        except:
            if verbose:
                print('Cannot find locas_config.json file. Create new one.')

            self.DATA = {
                "hf_token": "", # Hugging Face token.
                "load_in_bits": "8", # 'quantization' method. (So the device won't blow up)
                "models": { # the model that being use for chatting.
                    "Text_Generation": "Qwen",
                    "Tokenizer": "Qwen",
                },
                "users": {
                    "current": "", # the current user that being used.
                }

            }

            # dump data to file.
            with open(self.PATH, mode="w", encoding="utf-8") as write_file:
                json.dump(self.DATA, write_file, indent=4)
                write_file.close()

    def print_config_data(self) -> None:
        _print_dict(self.DATA)

    def check_exist_user_physically(self, target) -> bool:
        for _, folders, _ in os.walk(USER_PATH / target):
            if scanned:
                break
            scanned = True
            
            if 'history' in folders and 'memory' in folders:
                return True
            return False
        
    def check_exist_user(self, target: str) -> tuple[bool, str]:        
        for index in range(1, len(self.DATA['users'])):
            if self.DATA['users'][str(index)].lower() == target.lower(): # Not allow even capitalized.
                return (True, str(index))
        return (False, '0')

    def remove_user_with_index(self, verbose: bool, target_index: str) -> None:
        # move up until last user
        if verbose:
            print(f'Delete user {self.DATA['users'][target_index]}')
        for index in range(int(target_index), len(self.DATA['users'])):
            try:
                self.DATA['users'].update({str(index): self.DATA['users'][str(index+1)]})
            except KeyError: # reach the last user
                self.DATA['users'].pop(str(index))
        
        if len(self.DATA['users']) == 2:
            self.DATA['users'].update({"current": ""})
                
        self.upload_config_file(verbose)
