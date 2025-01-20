"""Main process of LocalAssistant"""

import logging
import argparse
import os
import shutil

from .parser import PARSER
from .utils import LocalAssistantException
from .model_processor import DownloadExtension, ChatExtension, DocsQuestionAnswerExtension

chat_ext = ChatExtension()
utils_ext = chat_ext.utils_ext
config = chat_ext.config

config.get_config_file()

def _download(parser_arg: argparse.Namespace):
    """download command function"""

    if parser_arg.TASK == 0:
        return

    try:
        task: int = int(parser_arg.TASK)
    except ValueError: # is string
        try:
            task: int = utils_ext.reverse_model_task[parser_arg.TASK]
        except KeyError as err: # not found
            logging.error("Invalid TASK: '%s'.", parser_arg.TASK)
            raise LocalAssistantException(f"invalid TASK: '{parser_arg.TASK}'.") from err
    if not 0 < task <= len(utils_ext.model_task):
        logging.error("Invalid TASK: '%s'.", parser_arg.TASK)
        raise LocalAssistantException(f"invalid TASK: '{parser_arg.TASK}'.")

    DownloadExtension().download_model_from_huggingface\
        (parser_arg.name, parser_arg.PATH, parser_arg.token, task)

def _config(parser_arg: argparse.Namespace):
    """Config command function"""

    def _change_single(name: str, name_help: str, condition = None) -> bool:
        """
        Fast VALUE changer.
        
        Returns:
            bool: whether function executed successfully.
        """
        print(f"{name_help}\n\nModify VALUE of '{name}' to ... (Type 'exit' to exit.)\n")
        command: str = input('>> ')
        print()

        # for exit, not everyone remember their token anyway.
        if command.lower() in ('exit', 'exit()'):
            return False

        if condition is not None:
            if not condition(command):
                logging.error("Invalid VALUE: '%s'.", command)
                raise LocalAssistantException(f"Invalid VALUE: '{command}'.")

        config.data.update({name: command})
        config.upload_config_file()
        return True

    # show config data.
    if parser_arg.show:
        config.print_config_data()
        return

    # modify config data.
    command: str = ''
    while True:
        config.print_config_data()
        print("Type KEY to modify KEY's VALUE. Type 'exit' to exit.\n")
        command = input('>> ')
        command = command.lower()
        print()

        if command in ('exit', 'exit()'):
            break

        if command not in tuple(config.data.keys()):
            logging.error("Invalid KEY: '%s'.", command)
            raise LocalAssistantException(f"Invalid KEY: '{command}'.")

        match command:
            case 'hf_token':
                if not _change_single(command, "'hf_token' is your Hugging Face token. \
Some models might be restricted and need authenticated."):
                    break
                continue

            case 'load_in_bits':
                def _check_valid(command: str) -> bool:
                    if command in ('4', '8', 'None'):
                        return True
                    return False

                if not _change_single(command, "'load_in_bits' is for 'quantization' method. \
If the VALUE is 8, then model is load in 8 bits (1 bytes) per parameters. \
Choose from: '4', '8', 'None'.", _check_valid):
                    break
                continue

            case 'top_k_memory':
                def _check_valid(command: str) -> bool:
                    if int(command) > 0:
                        return True
                    return False

                if not _change_single(command,\
                    "'top_k_memory' let us know how much memory you want to recall.", _check_valid):
                    break
                continue

            case 'models':
                while True:
                    utils_ext.print_dict(config.data['models'])
                    print("\nType KEY to modify KEY's VALUE. Type 'exit' to exit.\n")
                    command = input('>> ')
                    print()

                    if command.lower() in ('exit', 'exit()'):
                        break

                    if command not in tuple(config.data['models'].keys()):
                        logging.error("Invalid KEY: '%s'.", command)
                        raise LocalAssistantException(f"Invalid KEY: '{command}'.")

                    while True:
                        print('Choose from:')

                        model: str = config.data['models'][command]
                        folder_model: list = []
                        for item in os.scandir(os.path.join(utils_ext.model_path, model)):
                            if item.is_dir():
                                folder_model.append(item.name)
                                print(f'    - {item.name}')

                        if not _change_single(model, ''):
                            break
                        continue

            case 'documents':
                while True:
                    utils_ext.print_dict(config.data['documents'])
                    print("\nType KEY to modify KEY's VALUE. Type 'exit' to exit.\n")
                    command = input('>> ')
                    print()

                    if command.lower() in ('exit', 'exit()'):
                        break

                    if command not in tuple(config.data['documents'].keys()):
                        logging.error("Invalid KEY: '%s'.", command)
                        raise LocalAssistantException(f"Invalid KEY: '{command}'.")

                    if command == 'top_k':
                        def _check_valid(command: str) -> bool:
                            if 0 < int(command) < 51:
                                return True
                            return False

                        if not _change_single(command,"'top_k' let us know how many \
lines you want to retrieve. Maximum is 50 lines.", _check_valid):
                            break
                        continue

                    if command == 'allow_score':
                        def _check_valid(command: str) -> bool:
                            if 0 <= float(command) <= 1:
                                return True
                            return False

                        if not _change_single(command,"'allow_score' will make the retrieving \
process stop when similiarity score is lower.", _check_valid):
                            break
                        continue

            case 'users':
                print("Type 'locas user -h' for better configuration.\n")
                continue

def _user(parser_arg: argparse.Namespace):
    """User command function."""

    exist = config.check_exist_user_physically(parser_arg.TARGET)

    # show user.
    if parser_arg.TARGET.lower() == 'show':
        users: list = []
        for item in os.scandir(utils_ext.user_path):
            if not item.is_dir():
                continue
            if config.check_exist_user_physically(item.name):
                users.append(item.name)
        if users:
            print('Existed users:')
        for user in users:
            print(f'    - {user}')

    # create user.
    elif parser_arg.create:
        if exist:
            logging.error("User '%s' is existed.", parser_arg.TARGET)
            raise LocalAssistantException(f"User '{parser_arg.TARGET}' is existed.")
        config.check_for_exist_user(parser_arg.TARGET)
        logging.info('Created user %s.', parser_arg.TARGET)

    # delete user.
    elif parser_arg.delete:
        if not exist:
            logging.error("User '%s' is not existed.", parser_arg.TARGET)
            raise LocalAssistantException(f"User '{parser_arg.TARGET}' is not existed.")
        shutil.rmtree(os.path.join(utils_ext.user_path, parser_arg.TARGET))
        logging.info('Deleted user %s.', parser_arg.TARGET)

        # rename user.
    elif parser_arg.rename is not None:
        if not exist:
            logging.error("User '%s' is not existed.", parser_arg.TARGET)
            raise LocalAssistantException(f"User '{parser_arg.TARGET}' is not existed.")

        if config.check_exist_user_physically(parser_arg.rename):
            logging.error("User '%s' is existed.", parser_arg.rename)
            raise LocalAssistantException(f"User '{parser_arg.rename}' is existed.")

        os.rename(os.path.join(utils_ext.user_path, parser_arg.TARGET),\
                  os.path.join(utils_ext.user_path, parser_arg.rename))
        logging.info('Renamed user %s to %s.', parser_arg.TARGET, parser_arg.rename)

    # change user.
    else:
        if not exist:
            logging.error("User '%s' is not existed.", parser_arg.TARGET)
            raise LocalAssistantException(f"User '{parser_arg.TARGET}' is not existed.")
        config.data.update({'users': parser_arg.TARGET})
        logging.info('Change user to %s.', parser_arg.TARGET)

def _chat(parser_arg: argparse.Namespace):
    """Chat command function."""

    if parser_arg.LINE < 1:
        logging.error("Invalid LINE: %s", parser_arg.LINE)
        raise LocalAssistantException(f"Invalid LINE: {parser_arg.LINE}")

    chat_ext.chat_with_limited_lines\
        (parser_arg.text_generation, parser_arg.LINE, parser_arg.max_token)

def _start(parser_arg: argparse.Namespace):
    """Start command function."""

    chat_ext.chat_with_history(parser_arg.text_generation, parser_arg.user, parser_arg.max_token,\
        parser_arg.memory_enable, parser_arg.sentence_transformer,\
        parser_arg.top_k_memory, parser_arg.encode_at_start)

def _docs(parser_arg: argparse.Namespace):
    """Docsqa command function."""

    if parser_arg.ACTION == 'upload':
        config.check_for_exist_model(2)
        config.check_for_exist_model(3)
        DocsQuestionAnswerExtension\
            (config.data['models']['Sentence_Transformer'],config.data['models']['Cross_Encoder'])\
            .upload_docs(parser_arg.PATH, parser_arg.copy, parser_arg.not_encode)

    else:
        chat_ext.docs_question_answer(parser_arg.text_generation, parser_arg.max_token,\
            parser_arg.sentence_transformer, parser_arg.cross_encoder, parser_arg.top_k,\
            parser_arg.allow_score, parser_arg.encode_at_start, parser_arg.show_retrieve)

def _self_destruction(parser_arg: argparse.Namespace):
    """Self-destruction function."""

    utils_ext.self_destruction(parser_arg.all)

def main():
    """Main, the one and only."""
    parser_arg: argparse.Namespace = PARSER.parse_args()

    verbose = 4 if parser_arg.verbose > 4 else parser_arg.verbose # limit to 4
    logging.basicConfig(level=(5-verbose) * 10, format="%(asctime)s [%(levelname)s]: %(message)s")

    match parser_arg.COMMAND:
        case 'download':
            _download(parser_arg)
        case 'config':
            _config(parser_arg)
        case 'user':
            _user(parser_arg)
        case 'chat':
            _chat(parser_arg)
        case 'start':
            _start(parser_arg)
        case 'docs':
            _docs(parser_arg)
        case 'self-destruction':
            _self_destruction(parser_arg)

if __name__ == '__main__':
    main()
