import argparse
import os
import shutil

from utils import MODEL_PATH, USER_PATH, LocalAssistantConfig, clean_all_cache, _print_dict
from models import ModelTask, download_model_by_HuggingFace, chat_with_limited_lines

# +----------------------------+
# | Setup parser and subparser |
# +----------------------------+

parser = argparse.ArgumentParser(
    prog='locas',
    description='LocalAssistant (locas) is an AI designed to be used in CLI.',
)

# verbose.
parser.add_argument('-v', '--verbose', action='store_true', help='show debug messages')

# clean cache.
parser.add_argument('-c', '--clean', action='store_true', help='delete all .cache directory (RECOMMEND USING WHEN DONE)')

# version.
parser.add_argument('-V', '--version', action='version', version='LocalAssistant 0.1.0dev')

subparser = parser.add_subparsers(
    title='commands', 
    description="built-in commands (type 'locas COMMAND -h' for better description)", 
    metavar='COMMAND',
    dest='COMMAND',
)

# +-----------------------+
# | Setup parser commands |
# +-----------------------+

# ____download command____

subparser_download = subparser.add_parser(
    name='download', 
    help='Download models from Hugging Face', 
    description='Download models from Hugging Face',
    formatter_class=argparse.RawTextHelpFormatter,
)
subparser_download.add_argument('PATH', action='store', help='Path of the Hugging Face\'s model')
temp_string:str="""\
Model\'s task. Choose from:
    - 'Text_Generation' (or '1'): Download text generation only
    - 'Tokenizer' (or '2'): Download tokenizer only
    - 'Text_Generation_and_Tokenizer' (or '3'): Download both text generation and tokenizer
"""
subparser_download.add_argument('TASK', action='store', help=temp_string, default='None')
del temp_string
subparser_download.add_argument('-n', '--name', action='store', help='Name of the model to be saved', default='Untitled')
subparser_download.add_argument('-t', '--token', action='store', help='User Hugging Face\'s token (Some models might be restricted and need authenticated)', default='')

# ____config command____

temp_string="""\
Configurate LocalAssistant.

Eg: 
```
'hf_token': '',
'load_in_bits': '8',
'models': {
   'Text_Generation': 'Qwen',
   'Tokenizer': 'Qwen',
},
'users': {
   'current': '1',
   '1': {
      'Name': 'Default User',
      'Memory': 'None',
   },
},
Type KEY to modify KEY's VALUE. Type 'exit' to exit.

>> load_in_bits

'load_in_bits' is for 'quantization' method. if the VALUE is 16, then model is load in 16 bits (2 bytes) per parameters. Choose from: '4', '8', '16', '32'.

Modify VALUE of 'load_in_bits' to ... (Type 'exit' to exit.)

>> 16

'hf_token': '',
'load_in_bits': '16',
'models': {
   'Text_Generation': 'Qwen',
   'Tokenizer': 'Qwen',
},
'users': {
   'current': '1',
   '1': {
      'Name': 'Default User',
      'Memory': 'None',
   },
},
Type KEY to modify KEY's VALUE. Type 'exit' to exit.

>> exit
```


"""
subparser_config = subparser.add_parser(
    name='config',
    help='Configurate LocalAssistant.',
    description=temp_string,
    formatter_class=argparse.RawTextHelpFormatter,
)
del temp_string
subparser_config_group = subparser_config.add_mutually_exclusive_group()
subparser_config_group.add_argument('-m', '--modify', action='store_true', help='Modify config value')
subparser_config_group.add_argument('-s', '--show', action='store_true', help='Show config data')

# ____user command____

temp_string="""\
Config user. Use this to change, create, delete and rename users.

To see existed users. Type 'locas config -s' and look at 'users'.
"""
subparser_user = subparser.add_parser(
    name='user',
    help='Config user.',
    description=temp_string,
)
del temp_string
subparser_user.add_argument('TARGET', action='store', help='The target')
subparser_user_group = subparser_user.add_mutually_exclusive_group()
subparser_user_group.add_argument('-c', '--create', action='store_true', help='Create user with TARGET name')
subparser_user_group.add_argument('-d', '--delete', action='store_true', help='Delete user with TARGET name')
subparser_user_group.add_argument('-r', '--rename', action='store', metavar='NAME', help='Rename TARGET with NAME')

# ____chat command____

subparser_chat = subparser.add_parser(
    name='chat',
    help='Chat with models for limited lines. (no history saved)',
    description='Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)',
)
subparser_chat.add_argument('LINE', action='store', type=int, help='Number of line to chat with')
subparser_chat.add_argument('-tgm', '--text_generation', metavar='MODEL', action='store', help='Use downloaded text generation model', default='')
subparser_chat.add_argument('-tm', '--tokenizer', metavar='MODEL', action='store', help='Use downloaded tokenizer model', default='')
subparser_chat.add_argument('-t', '--max_token', metavar='TOKEN', action='store', type=int, help='Max tokens to generate', default= 50)

# +-------------------+
# | Process functions |
# +-------------------+

parser_arg: argparse.Namespace = parser.parse_args()

# get config data from locas_config.json file.
CONFIG = LocalAssistantConfig()
CONFIG.get_config_file(parser_arg.verbose)

# ____clean cache function____

if parser_arg.clean:
    clean_all_cache(parser_arg.verbose)

# ____download command function____

if parser_arg.COMMAND == 'download':
    if parser_arg.TASK not in ('1', 'Text_Generation', '2', 'Tokenizer', '3', 'Text_Generation_and_Tokenizer'):
        print(f"locas download: error: expect 'Text_Generation', 'Tokenizer', 'Text_Generation_and_Tokenizer', got '{parser_arg.task}'")
        parser_arg.TASK = 'None'
    
    # apply hf_token if it in config file.
    if parser_arg.token == '':
        parser_arg.token = CONFIG.DATA['hf_token']
    
    # convert string to int
    if parser_arg.TASK in ('None', 'Text_Generation', 'Tokenizer', 'Text_Generation_and_Tokenizer'):
        parser_arg.TASK = ModelTask.reverse_name_task(ModelTask, parser_arg.TASK)
    else:
        parser_arg.TASK = int(parser_arg.TASK)
    download_model_by_HuggingFace(parser_arg.verbose, parser_arg.name, parser_arg.PATH, parser_arg.token, parser_arg.TASK)
    
# ____config command function____

if parser_arg.COMMAND == 'config':
    # show config data.
    if parser_arg.show:
        # get data from the file.
        CONFIG.print_config_data()
        
    # modify config data.
    if parser_arg.modify:
        command: str = ''
        while True:
            CONFIG.print_config_data()
            print("Type KEY to modify KEY's VALUE. Type 'exit' to exit.\n")
            command = input('>> ')
            command = command.lower()
            print()
            
            if command in ('exit', 'exit()'):
                break
            
            if command not in tuple(CONFIG.DATA.keys()):
                print(f"locas config: error: no KEY named '{command}'\n")
                input('Press ENTER to continue...')
                print()
                continue
            
            if command == 'hf_token':
                print("'hf_token' is your Hugging Face token. Some models might be restricted and need authenticated. Use token to login temporately and download model.\n")
                print("Modify VALUE of 'hf_token' to ... (Type 'exit' to exit.)\n")
                command = input('>> ')
                print()
                
                # for exit, not everyone remember their token anyway.
                if command.lower() in ('exit', 'exit()'):
                    continue
                
                CONFIG.DATA.update({'hf_token': command})
                CONFIG.upload_config_file(parser_arg.verbose)
                continue
            
            if command == 'load_in_bits':
                while command not in ('4', '8', '16', '32'):
                    print("'load_in_bits' is for 'quantization' method. if the VALUE is 16, then model is load in 16 bits (2 bytes) per parameters. Choose from: '4', '8', '16', '32'.\n")
                    print("Modify VALUE of 'load_in_bits' to ... (Type 'exit' to exit.)\n")
                    command = input('>> ')
                    print()
                    
                    # for exit.
                    if command.lower() in ('exit', 'exit()'):
                        command = CONFIG.DATA['load_in_bits'] # if exit, nothing change.
                        break
                    
                    if command not in ('4', '8', '16', '32'):
                        print(f"locas config: error: expect '4', '8', '16', '32', got {command}\n")
                CONFIG.DATA.update({'load_in_bits': command})
                CONFIG.upload_config_file(parser_arg.verbose)
                continue
            
            if command == 'models':
                while True:
                    _print_dict(CONFIG.DATA['models'])
                    print("\nType KEY to modify KEY's VALUE. Type 'exit' to exit.\n")
                    command = input('>> ')
                    print()

                    if command.lower() in ('exit', 'exit()'):
                        break
                    
                    if command not in tuple(CONFIG.DATA['models'].keys()):
                        print(f"locas config: error: no KEY named '{command}'\n")
                        input('Press ENTER to continue...')
                        print()
                        continue
                    
                    for model in CONFIG.DATA['models'].keys():
                        if command != model:
                            continue
                        
                        while True:
                            # print all exist model dir.
                            print('Choose from:')
                            folder_model: list = []
                            for _, folders, _ in os.walk(MODEL_PATH / model, topdown=False):
                                folder_model = folders
                            for folder in folder_model:
                                print(f'    - {folder}')
                            print()
                            
                            print(f"Modify VALUE of '{model}' to ... (Type 'exit' to exit.)\n")
                            command = input('>> ')
                            print()
                            
                            # for exit.
                            if command.lower() in ('exit', 'exit()'):
                                break
                            
                            if command not in folder_model:
                                print(f"locas config: error: '{command} is not from allowed name'\n")
                                input('Press ENTER to continue...')
                                print()
                                continue
                            
                            CONFIG.DATA['models'].update({model: command})
                            CONFIG.upload_config_file(parser_arg.verbose)
                            break
            
            if command == 'users':
                print("Type 'locas user -h' for better config.\n")
                input('Press ENTER to continue...')
                print()
                continue
            
# ____user command function____

if parser_arg.COMMAND == 'user':
    
    exist, exist_index = CONFIG.check_exist_user(parser_arg.TARGET)
    if parser_arg.verbose:
        if exist:
            print(f'User {parser_arg.TARGET} is exist.')
        else:
            print(f'User {parser_arg.TARGET} is not exist.')
    
    # create user.
    if parser_arg.create:
        if exist:
            print(f'local user: error: user {parser_arg.TARGET} existed')
        else: # if user existed, return an error.
            # update config file.
            CONFIG.DATA['users'].update({len(CONFIG.DATA['users']): parser_arg.TARGET})
            CONFIG.upload_config_file(parser_arg.verbose)
                
            # update on physical directory
            os.mkdir(USER_PATH / parser_arg.TARGET)
            os.mkdir(USER_PATH / parser_arg.TARGET / 'history')
            os.mkdir(USER_PATH / parser_arg.TARGET / 'memory')
            
            if parser_arg.verbose:
                print(f'Created user {parser_arg.TARGET}.')
    
    # delete user.
    elif parser_arg.delete:
        if not exist:
            print(f'local user: error: user {parser_arg.TARGET} is not existed')
        else: # if user not existed, return an error.
            # update config file.
            CONFIG.remove_user_with_index(parser_arg.verbose, exist_index)
            
            # update on physical directory
            shutil.rmtree(USER_PATH / parser_arg.TARGET)

            if parser_arg.verbose:
                print(f'Deleted user {parser_arg.TARGET}.')
    
    # rename user.
    elif parser_arg.rename is not None:
        if not exist:
            print(f'local user: error: user {parser_arg.TARGET} is not existed')
        else: # if user not existed, return an error.
            # update config file.
            CONFIG.DATA['users'].update({exist_index: parser_arg.rename})
            CONFIG.upload_config_file(parser_arg.verbose)
            
            # update on physical directory
            os.rename(USER_PATH / CONFIG.DATA['users'][exist_index], USER_PATH / parser_arg.rename)

            if parser_arg.verbose:
                print(f'Renamed user {parser_arg.TARGET} to {parser_arg.rename}.')
    
    # change user.
    else:
        if not exist:
            print(f'local user: error: user {parser_arg.TARGET} is not existed')
        else: # if user not existed, return an error.
            # update config file.
            CONFIG.DATA['users'].update({"current": exist_index})
            CONFIG.upload_config_file(parser_arg.verbose)

            if parser_arg.verbose:
                print(f'Change user to {parser_arg.rename}.')

# ____chat command function____       
             
if parser_arg.COMMAND == 'chat':
    if parser_arg.LINE < 1:
        print("locas chat: error: Argument 'LINE' should not have non-positive value.")
    else:
        chat_with_limited_lines(parser_arg.verbose, parser_arg.text_generation, parser_arg.tokenizer, parser_arg.LINE, parser_arg.max_token)
