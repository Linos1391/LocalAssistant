import pathlib
import json
import os
import stat 
import logging

# Path
PROJECT_PATH: str = pathlib.Path(__file__).parent
MODEL_PATH: str = PROJECT_PATH / 'models'
USER_PATH: str = PROJECT_PATH / 'users'

LOGGER = logging.getLogger()

# Custom Exception
class LocalAssistantException(Exception):
    """
    For common errors in MyAssistant
    """
    pass

def _real_remove(path: str):
    """
    Something like shutil.rmtree but without access denied
    """
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)      
     

def _clean_cache(path: str) -> None:
    """
    delete choosen .cache dir (Too dangerous to be used)
    """
    try:
        _real_remove(path)
        LOGGER.debug(f'Cleaned {path}.')
    except: # it doesn't matter
        LOGGER.debug(f'Cannot find {path}, skipped.')

def clean_all_cache() -> None:
    """
    delete all .cache dir
    """
    for path in (
        MODEL_PATH / '.cache',
    ):
        _clean_cache(path)
        LOGGER.info('Cleared all cache')
        
# it happens that i'm too smart.
def _print_dict(data: dict, level: int=0):
    for key, value in data.items():
        if isinstance(value, str):
            print(level*'   ' + f"'{key}': '{value}',")
        else: # value is dict
            print(level*'   ' + "%r: {" % (key)) # use %r as '{' is written
            _print_dict(value, level+1)
            print(level*'   ' + "},")
        
class LocalAssistantConfig:
    PATH: str = PROJECT_PATH / 'locas_config.json'
    DATA: dict = {}
        
    def upload_config_file(self) -> None:
        # dump data to file.
        with open(self.PATH, mode="w", encoding="utf-8") as write_file:
            json.dump(self.DATA, write_file, indent=4)
            write_file.close()

        LOGGER.info("Uploaded current data to config.json file.")

    def get_config_file(self) -> None:
        try:
            LOGGER.debug('Finding locas_config.json file.')

            # Read the data
            with open(self.PATH, mode="r", encoding="utf-8") as read_file:
                self.DATA = json.load(read_file)
                read_file.close()

            LOGGER.debug('Found locas_config.json file.')
        except:
            LOGGER.debug('Cannot find locas_config.json file. Create new one.')

            self.DATA = {
                "hf_token": "", # Hugging Face token.
                "load_in_bits": "8", # 'quantization' method. (So the device won't blow up)
                "models": { # the model that being use for chatting.
                    "Text_Generation": "",
                },
                "users": {
                    "current": "1", # the current user that being used.
                    "1": "default",
                }

            }

            # dump data to file.
            with open(self.PATH, mode="w", encoding="utf-8") as write_file:
                json.dump(self.DATA, write_file, indent=4)
                write_file.close()
        LOGGER.info('Got data from config file.')

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

    def remove_user_with_index(self, target_index: str) -> None:
        # move up until last user
        LOGGER.info(f'Delete user {self.DATA['users'][target_index]}')
        for index in range(int(target_index), len(self.DATA['users'])):
            try:
                self.DATA['users'].update({str(index): self.DATA['users'][str(index+1)]})
            except KeyError: # reach the last user
                self.DATA['users'].pop(str(index))
        
        if len(self.DATA['users']) == 2:
            self.DATA['users'].update({"current": ""})
                
        self.upload_config_file()

# remove all
def self_destruction(choice: str):
    """
    Everything all needs self-destruction.
    """
    option: str = input(f"Are you sure to remove LocalAssistant ({choice}). There will be no turning back, as with data or model. Continue? [y/(n)]: ")
    if option.lower() != 'y':
        print('Self-destruction denied.')
        return
    print('Self-destruction...')
    
    # Locas, kys.
    if choice == 'github':
        _real_remove(pathlib.Path(PROJECT_PATH).parent)
    elif choice == 'pip':
        # delete dist info so you can download again
        for item in os.scandir(pathlib.Path(PROJECT_PATH).parent):
            if not item.is_dir():
                continue
            if not item.name.startswith('LocalAssistant-'):
                continue
            if not item.name.endswith('.dist-info'):
                continue
            _real_remove(item.path)
            break    
        
        _real_remove(pathlib.Path(PROJECT_PATH))
        