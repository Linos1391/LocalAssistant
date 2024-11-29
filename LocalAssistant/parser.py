import argparse
import os
import shutil
import logging

from utils import MODEL_PATH, USER_PATH, LOGGER, LocalAssistantConfig, clean_all_cache, _print_dict, self_destruction
from models import ModelTask, download_model_by_HuggingFace, chat_with_limited_lines, chat_with_history

# +----------------------------+
# | Setup parser and subparser |
# +----------------------------+

parser = argparse.ArgumentParser(
    prog='locas',
    description='LocalAssistant (locas) is an AI designed to be used in CLI.',
)

# verbose.
parser.add_argument('-v', '--verbose', action='count', help='show debug messages (Can be used multiple times for higher level: CRITICAL[v] -> DEBUG[vvvv])', default=0)

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
    - 'Text_Generation' (or '1'): Download text generation model.
"""
subparser_download.add_argument('TASK', action='store', help=temp_string, default='None')
del temp_string
subparser_download.add_argument('-n', '--name', action='store', help='Name of the model to be saved', default='Untitled')
subparser_download.add_argument('-t', '--token', action='store', help='User Hugging Face\'s token (Some models might be restricted and need authenticated)', default='')

# ____config command____

temp_string="""\
Configurate LocalAssistant.

Example: 
----------------------------------------------------------------------
>> locas config -m

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

----------------------------------------------------------------------

"""
subparser_config = subparser.add_parser(
    name='config',
    help='Configurate LocalAssistant.',
    description=temp_string,
    formatter_class=argparse.RawTextHelpFormatter,
)
del temp_string
subparser_config_group = subparser_config.add_mutually_exclusive_group(required=True)
subparser_config_group.add_argument('-m', '--modify', action='store_true', help='Modify config value')
subparser_config_group.add_argument('-s', '--show', action='store_true', help='Show config data')

# ____user command____

temp_string="""\
Use this to configurate user.
    - To change change user. Type 'locas user TARGET'.
    - To see existed users. Type 'locas config -s' and look at 'users'.
"""
subparser_user = subparser.add_parser(
    name='user',
    help='Config user.',
    description=temp_string,
    formatter_class=argparse.RawDescriptionHelpFormatter
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
subparser_chat.add_argument('-t', '--max_token', metavar='TOKEN', action='store', type=int, help='Max tokens to generate', default= 150)

# ____start command____

subparser_start = subparser.add_parser(
    name='start',
    help='Chat with models using history.',
    description='Chat with models using history.',
)

subparser_start.add_argument('-u', '--user', action='store', help='The user name', default='default')
subparser_start.add_argument('-tgm', '--text_generation', metavar='MODEL', action='store', help='Use downloaded text generation model', default='')
subparser_start.add_argument('-t', '--max_token', metavar='TOKEN', action='store', type=int, help='Max tokens to generate', default= 150)

# ____self-destruction command____

subparser_self_destruction = subparser.add_parser(
    name='self-destruction',
    help='LocalAssistant\'s self-destruction.',
    description='LocalAssistant\'s self-destruction.',
)

subparser_self_destruction.add_argument('CHOICE', action='store', help="Choose 'github' or 'pip'.")

# +-------------------+
# | Process functions |
# +-------------------+

def main():
    parser_arg: argparse.Namespace = parser.parse_args()

    verbose = 4 if parser_arg.verbose > 4 else parser_arg.verbose # limit to 4
    logging.basicConfig(level=(5-verbose) * 10, format="%(asctime)s [%(levelname)s]: %(message)s")

    # get config data from locas_config.json file.
    CONFIG = LocalAssistantConfig()
    CONFIG.get_config_file()
    
    # ____clean cache function____

    if parser_arg.clean:
        clean_all_cache()

    # ____download command function____

    if parser_arg.COMMAND == 'download':
        if parser_arg.TASK not in ('1', 'Text_Generation', '2', 'Sentence_Transformer'):
            LOGGER.error(f"invalid TASK: '{parser_arg.TASK}'")
            subparser_download.error(f"invalid TASK: '{parser_arg.TASK}'")

        # apply hf_token if it in config file.
        if parser_arg.token == '':
            parser_arg.token = CONFIG.DATA['hf_token']

        # convert string to int
        if parser_arg.TASK in ('None', 'Text_Generation', 'Sentence_Transformer'):
            parser_arg.TASK = ModelTask.reverse_name_task(ModelTask, parser_arg.TASK)
        else:
            parser_arg.TASK = int(parser_arg.TASK)
        download_model_by_HuggingFace(parser_arg.name, parser_arg.PATH, parser_arg.token, parser_arg.TASK)

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
                    LOGGER.error(f"invalid KEY: '{command}'")
                    subparser_config.error(f"invalid KEY: '{command}'")
                
                if command == 'hf_token':
                    print("'hf_token' is your Hugging Face token. Some models might be restricted and need authenticated. Use token to login temporately and download model.\n")
                    print("Modify VALUE of 'hf_token' to ... (Type 'exit' to exit.)\n")
                    command = input('>> ')
                    print()

                    # for exit, not everyone remember their token anyway.
                    if command.lower() in ('exit', 'exit()'):
                        continue
                    
                    CONFIG.DATA.update({'hf_token': command})
                    CONFIG.upload_config_file()
                    continue
                
                if command == 'load_in_bits':
                    print("'load_in_bits' is for 'quantization' method. if the VALUE is 16, then model is load in 16 bits (2 bytes) per parameters. Choose from: '4', '8', '16', '32'.\n")
                    print("Modify VALUE of 'load_in_bits' to ... (Type 'exit' to exit.)\n")
                    command = input('>> ')
                    print()
                    
                    # for exit.
                    if command.lower() in ('exit', 'exit()'):
                        continue
                        
                    if command not in ('4', '8', '16', '32'):
                        LOGGER.error(f"invalid VALUE: {command}")
                        subparser_config.error(f"invalid VALUE: {command}")
                            
                    CONFIG.DATA.update({'load_in_bits': command})
                    CONFIG.upload_config_file()
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
                            LOGGER.error(f"invalid KEY: '{command}'")
                            subparser_config.error(f"invalid KEY: '{command}'")
                        
                        for model in CONFIG.DATA['models'].keys():
                            if command != model:
                                continue
                            
                            while True:
                                # print all exist model dir.
                                print('Choose from:')
                                folder_model: list = []
                                for root, folders, _ in os.walk(MODEL_PATH / model):
                                    if root != str(MODEL_PATH / model):
                                        break   
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
                                    LOGGER.error(f"invalid VALUE: '{command}'")
                                    subparser_config.error(f"invalid VALUE: '{command}'")
                                
                                CONFIG.DATA['models'].update({model: command})
                                CONFIG.upload_config_file()
                                break
                            
                if command == 'users':
                    print("Type 'locas user -h' for better config.\n")
                    input('Press ENTER to continue...')
                    print()
                    continue
                
    # ____user command function____

    if parser_arg.COMMAND == 'user':

        exist, exist_index = CONFIG.check_exist_user(parser_arg.TARGET)
        if exist:
            LOGGER.debug(f'User {parser_arg.TARGET} is exist.')
        else:
            LOGGER.debug(f'User {parser_arg.TARGET} is not exist.')

        # create user.
        if parser_arg.create:
            # if user existed, return an error.
            if exist:
                LOGGER.error(f'user is existed: {parser_arg.TARGET}')
                subparser_user.error(f'user is existed: {parser_arg.TARGET}')
                
            # update config file.
            CONFIG.DATA['users'].update({len(CONFIG.DATA['users']): parser_arg.TARGET})
            CONFIG.upload_config_file()
            
            # update on physical directory
            os.mkdir(USER_PATH / parser_arg.TARGET)
            os.mkdir(USER_PATH / parser_arg.TARGET / 'history')
            os.mkdir(USER_PATH / parser_arg.TARGET / 'memory')
            
            LOGGER.info(f'Created user {parser_arg.TARGET}.')

        # delete user.
        elif parser_arg.delete:
            # if user not existed, return an error.
            if not exist:
                LOGGER.error(f'user is not existed: {parser_arg.TARGET}')
                subparser_user.error(f'user is not existed: {parser_arg.TARGET}')
            
            # update config file.
            CONFIG.remove_user_with_index(exist_index)
            
            # update on physical directory
            shutil.rmtree(USER_PATH / parser_arg.TARGET)
            
            LOGGER.info(f'Deleted user {parser_arg.TARGET}.')

        # rename user.
        elif parser_arg.rename is not None:
            # if user not existed, return an error.
            if not exist:
                LOGGER.error(f'user is not existed: {parser_arg.TARGET}')
                subparser_user.error(f'user is not existed: {parser_arg.TARGET}')
            
            # update config file.
            CONFIG.DATA['users'].update({exist_index: parser_arg.rename})
            CONFIG.upload_config_file()
            
            # update on physical directory
            os.rename(USER_PATH / CONFIG.DATA['users'][exist_index], USER_PATH / parser_arg.rename)
            
            LOGGER.info(f'Renamed user {parser_arg.TARGET} to {parser_arg.rename}.')

        # change user.
        else:
            # if user not existed, return an error.
            if not exist:
                LOGGER.error(f'user is not existed: {parser_arg.TARGET}')
                subparser_user.error(f'user is not existed: {parser_arg.TARGET}')
            
            # update config file.
            CONFIG.DATA['users'].update({"current": exist_index})
            CONFIG.upload_config_file()
            
            LOGGER.info(f'Change user to {parser_arg.rename}.')

    # ____chat command function____       

    if parser_arg.COMMAND == 'chat':
        if parser_arg.LINE < 1:
            LOGGER.error(f"invalid LINE: {parser_arg.LINE}")
            subparser_chat.error(f"invalid LINE: {parser_arg.LINE}")
        
        chat_with_limited_lines(parser_arg.text_generation, parser_arg.LINE, parser_arg.max_token)

    # ____start command function____     
    
    if parser_arg.COMMAND == 'start':
        chat_with_history(parser_arg.text_generation, parser_arg.user, parser_arg.max_token)
    
    # ____self-destruction function____
    
    if parser_arg.COMMAND == 'self-destruction':
        choice: str = parser_arg.CHOICE.lower()
        
        if choice not in ('github', 'pip'):
            subparser_self_destruction.error(f'Invalid CHOICE: {choice}')
        
        self_destruction(choice)

if __name__ == '__main__':
    main()
