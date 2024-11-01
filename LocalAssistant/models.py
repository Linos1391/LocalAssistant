import os
import pathlib
import json
from threading import Thread

from huggingface_hub import login, logout
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
import torch

from utils import LocalAssistantException, LocalAssistantConfig, MODEL_PATH, USER_PATH

CONFIG = LocalAssistantConfig()

# +--------------------+
# | locas download ... |
# +--------------------+

def _download_with_login(hf_token: str, huggingface_path: str, AutoModel):
    """
    Some models might be restricted and need authenticated. Use token to login temporately and download model.
    """
    
    try:
        login(hf_token)
        model = AutoModel.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
    except Exception as e:
        return e
    
    try: # we still logout if cannot download.
        logout(hf_token) 
    except Exception as e:
        return e
    
    return model  

def _check_cache_dir() -> None:
    """
    Check if .cache dir is made yet, it not, create one.
    """
    try:
        os.makedirs(MODEL_PATH / '.cache')
    except: # ignore if it existed
        pass

class ModelTask:
    NONE = 0
    TEXT_GENERATION = 1
    TOKENIZER = 2
    TEXT_GENERATION_AND_TOKENIZER = 3
    
    def name_task(self, task: int) -> str:
        # for O(1).
        if task == self.NONE: return 'None'
        if task == self.TEXT_GENERATION: return 'Text_Generation'
        if task == self.TOKENIZER: return 'Tokenizer'
        if task == self.TEXT_GENERATION_AND_TOKENIZER: return 'Text_Generation_and_Tokenizer'
        
        raise LocalAssistantException("Task not found.")
    
    def reverse_name_task(self, task: str) -> str:
        # also for O(1).
        if task == 'None': return self.NONE
        if task == 'Text_Generation': return self.TEXT_GENERATION
        if task == 'Tokenizer': return self.TOKENIZER
        if task == 'Text_Generation_and_Tokenizer': return self.TEXT_GENERATION_AND_TOKENIZER
        
        raise LocalAssistantException("Task not found.")
         
def _save_model(model, path: str, verbose: bool) -> None:
    """
    Save model to path. Check if the name has taken.
    """   
    # take parent and child path   
    parent: pathlib.Path = pathlib.Path(path).parent
    child: str = pathlib.Path(path).name
    
    try: # make dir if dir not exist
        for item in os.scandir(path=parent):
            pass
    except FileNotFoundError:
        os.makedirs(parent)
        if verbose:
            print(f'Made {parent.name} directory')
    
    stop: bool = False
    while not stop:
        for root, folders, files in os.walk(top=parent):
            if root != str(parent):
                break
            
            if folders == [] and files == []: # if dir is empty -> Skip anyway
                stop = True
                break
                
            # check for same folder name.
            for folder in folders:
                if folder == child: 
                    if verbose:
                        print(f'Found {folder}.')

                    # remove unnecessary space
                    while folder.endswith(' '):
                        folder = folder[:-1]

                    index: str = folder.split(' ')[-1]

                    # check if index in (n) format
                    if not (index.startswith('(') and index.endswith(')')):
                        child += ' (1)'
                        break
                    
                    try: # it was (n) but n is not int
                        index: int = int(index[1:-1])
                    except ValueError:
                        child += ' (1)'
                        break
                    
                    child = f'{child[:-4]} ({index + 1})'
                    break
            
            # check for same file name.
            for file in files:
                if file == child: 
                    if verbose:
                        print(f'Found {file}.')

                    # remove unnecessary space
                    while file.endswith(' '):
                        file = file[:-1]

                    index: str = file.split(' ')[-1]

                    # check if index in (n) format
                    if not (index.startswith('(') and index.endswith(')')):
                        child += ' (1)'
                        break
                    
                    try: # it was (n) but n is not int
                        index: int = int(index[1:-1])
                    except ValueError:
                        child += ' (1)'
                        break
                    
                    child = f'{child[:-4]} ({index + 1})'
                    break    
            
            # last check (in folders only, we already done in files)
            if child not in folders:
                stop = True
    
    if verbose:
        print(f'Save as {child} in {parent.name}.')    
        
    model.save_pretrained(parent / child)  

def download_model_by_HuggingFace(
        verbose: bool,
        model_name: str,
        huggingface_path: str,
        hf_token: str = '',
        task: int = ModelTask.NONE,
    ) -> None:
    
    """
    Download model directly from Hugging Face and save it in `models` folder.
    Args:
        verbose (bool): show debug messages
        model_name (str): The name of models. Used for select model and other config.
        huggingface_path (str): The path to download model.
        hf_token (str): The user Hugging Face access token. Some models might be restricted and need authenticated. Use token to login temporately and download model. (Default = '' as None)
        task (enum): Model's task.
    """
    # if there is no task, return.
    if task == ModelTask.NONE:
        return
    
    # Download model from huggingface path (We only use safetensors) and save to .cache
    
    # check .cache dir
    _check_cache_dir()

    # if user use 'https' path, convert to normal one.
    huggingface_path = huggingface_path.removeprefix('https://huggingface.co/')
    
    # For tokenizers only.
    if task == ModelTask.TOKENIZER:
        if verbose:
            print(f'Download only tokenizer from {huggingface_path}')
        try:
            if hf_token == '': # by default, do not use token.
                if verbose:
                    print('Not use token.')
                try: 
                    tokenizer_model = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
                except Exception as e:
                    raise e

            else: # use token.
                if verbose:
                    print(f'Use provided token: {hf_token}')
                tokenizer_model = _download_with_login(hf_token, huggingface_path, AutoTokenizer)
                if verbose:
                    print('Log out from token.')
                if isinstance(tokenizer_model, Exception):
                    raise tokenizer_model
        except Exception as e:
            raise e 
    
        # save downloaded model
        _save_model(tokenizer_model, MODEL_PATH / ModelTask.name_task(ModelTask, ModelTask.TOKENIZER) / model_name, verbose)
    
    # For text generation only.
    if task == ModelTask.TEXT_GENERATION:
        if verbose:
            print(f'Download only text generation from {huggingface_path}')
        try:
            if hf_token == '': # by default, do not use token.
                if verbose:
                    print('Not use token.')
                try: 
                    text_generation_model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
                except Exception as e:
                    raise e

            else: # use token.
                if verbose:
                    print(f'Use provided token: {hf_token}')
                text_generation_model = _download_with_login(hf_token, huggingface_path, AutoModelForCausalLM)
                if verbose:
                    print('Log out from token.')
                if isinstance(text_generation_model, Exception):
                    raise text_generation_model
        except Exception as e:
            raise e 
        
        # save downloaded model
        _save_model(text_generation_model, MODEL_PATH / ModelTask.name_task(ModelTask, ModelTask.TEXT_GENERATION) / model_name, verbose)
    
    # For text generation and tokenizer.
    if task == ModelTask.TEXT_GENERATION_AND_TOKENIZER:
        if verbose:
            print(f'Download text generation and tokenizer from {huggingface_path}')
        try: 
            if hf_token == '': # by default, do not use token.
                if verbose:
                    print('Not use token.')
                try: 
                    tokenizer_model = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
                    text_generation_model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
                except Exception as e:
                    raise e

            else: # use token.
                if verbose:
                    print(f'Use provided token: {hf_token}')
                tokenizer_model = _download_with_login(hf_token, huggingface_path, AutoTokenizer)
                text_generation_model = _download_with_login(hf_token, huggingface_path, AutoModelForCausalLM)
                if verbose:
                    print('Log out from token.')
                if isinstance(tokenizer_model, Exception):
                    raise tokenizer_model
                if isinstance(text_generation_model, Exception):
                    raise text_generation_model
        except Exception as e:
            raise e
        
        # save downloaded model
        _save_model(tokenizer_model, MODEL_PATH / ModelTask.name_task(ModelTask, ModelTask.TOKENIZER) / model_name, verbose)
        _save_model(text_generation_model, MODEL_PATH / ModelTask.name_task(ModelTask, ModelTask.TEXT_GENERATION) / model_name, verbose)
    
# +----------------+
# | locas chat ... |
# +----------------+

def _check_for_exist_model(verbose: bool, task: str) -> None:
    """
    Check for exist model. There is nothing we can do if the user chats without any models.
    """
    CONFIG.get_config_file(verbose)
    
    if task not in ('Text_Generation', 'Tokenizer'):
        raise LocalAssistantException("Wrong task sir") # Only human can do wrong.

    if CONFIG.DATA['models'][task] != '':
        return # nothing to fix.
    
    scanned: bool = False
    for _, folders, _ in os.walk(MODEL_PATH / task):
        if scanned:
            break
        
        scanned = True
        CONFIG.DATA['models'][task] = folders[0] # if there is no model, this has ignored
            
    if not scanned: # the above line has skipped    
        raise LocalAssistantException(f"There is no models for {task}. Please type 'locas download -h' and download one.")
    
    CONFIG.upload_config_file(verbose)
    if verbose:
        print(f'Apply {folders[0]} as model for {task}.')
    
def _chat(history: list, text_generation_model, tokenizer_model, max_new_tokens) -> dict | bool:
    prompt: str = input('\n\n>> ')
        
    if prompt.lower() in ('exit', 'exit()'):
        return False
    
    print()
    
    # append chat to history.
    history.append({"role": "user", "content": prompt,})
    
    # format history.
    formatted_history = tokenizer_model.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
    input_token = tokenizer_model(formatted_history, return_tensors="pt", add_special_tokens=False)        
    
    # move token to device.
    input_token = {key: tensor.to(text_generation_model.device) for key, tensor in input_token.items()}
    
    # make streamer.
    streamer = TextIteratorStreamer(tokenizer_model, skip_prompt=True)
    
    # threading the generation
    generation_kwargs = dict(input_token, streamer=streamer, max_new_tokens=max_new_tokens, do_sample=True)
    thread = Thread(target=text_generation_model.generate, kwargs=generation_kwargs)
    thread.start()
    
    full_output: str = ''     
    for output in streamer:
        output = output.removesuffix('<|im_end|>')
        
        full_output += output
        print(output, end='', flush=True)
        
    return {"role": "assistant", "content": full_output}
    
def chat_with_limited_lines(
        verbose: bool,
        text_generation_model_name: str = '',
        tokenizer_model_name: str = '',
        lines: int = 1,
        max_new_tokens: int = 150,
    ):
    """
    Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
    Args:
        verbose (bool): show debug messages
        text_generation_model_name (str): name of the text generation model, get from config file if got blank.
        tokenizer_model_name (str): name of the tokenizer model, get from config file if got blank.
        lines (int): lines of chat (not count 'assistant'), default as 1.
        max_new_tokens (int): max tokens to generate, default as 150.
    """
    
    if lines < 1:
        raise LocalAssistantException("Argument 'lines' should not have non-positive value.")
    
    history: list = [
        {"role": "system", "content": f"You are an Assistant named LocalAssistant (Locas). You only have {lines} lines, give the user the best supports as you can."},
    ]
    
    if text_generation_model_name == '':
        _check_for_exist_model(verbose, 'Text_Generation')
        CONFIG.get_config_file(verbose)
        text_generation_model_name = CONFIG.DATA['models']['Text_Generation']
        if verbose:
            print(f'User did not add model for text generation, use {text_generation_model_name} instead.')
        
    if tokenizer_model_name == '':
        _check_for_exist_model(verbose, 'Tokenizer')
        CONFIG.get_config_file(verbose)
        tokenizer_model_name = CONFIG.DATA['models']['Tokenizer']
        if verbose:
            print(f'User did not add model for text generation, use {tokenizer_model_name} instead.')
    
    # load model
    if verbose:
        print('Begin to load models.')
    text_generation_model = AutoModelForCausalLM.from_pretrained(MODEL_PATH / 'Text_Generation' / text_generation_model_name, use_safetensors=True, device_map="auto", torch_dtype=torch.bfloat16) #float32 is wasteful!
    tokenizer_model = AutoTokenizer.from_pretrained(MODEL_PATH / 'Tokenizer' / tokenizer_model_name, use_safetensors=True, device_map="auto", torch_dtype=torch.bfloat16)
    if verbose:
        print('Done loading models.')
    
    print(f"\nStart chatting in {lines} lines with '{text_generation_model_name}' for text generation and '{tokenizer_model_name}' for tokenizer.\n\nType 'exit' to exit.", end='')
    for _ in range(lines):
        reply = _chat(history, text_generation_model, tokenizer_model, max_new_tokens)
        if not reply: # User exit.
            break
        
        history.append(reply)

# +-----------------+
# | locas start ... |
# +-----------------+

def chat_with_history(
        verbose: bool,
        text_generation_model_name: str = '',
        tokenizer_model_name: str = '',
        user: str = 'default',
        max_new_tokens: int = 150,
    ):
    """
    Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
    Args:
        verbose (bool): show debug messages
        text_generation_model_name (str): name of the text generation model, get from config file if got blank.
        tokenizer_model_name (str): name of the tokenizer model, get from config file if got blank.
        user (str): chat by user, default as 'default'.
        max_new_tokens (int): max tokens to generate, default as 50.
    """

    CONFIG.get_config_file(verbose)

    if user == 'default': # user did not add 'user'.
        scanned: bool = False
        for _, folders, _ in os.walk(USER_PATH):
            if scanned:
                break
            scanned = True
            
            if CONFIG.DATA['users']['current'] == '': # not in config file
                if verbose:
                    print("Config file does not have current user. Set user as default.")
                
                CONFIG.DATA['users'].update({
                        'current': '1',
                        '1': 'default',
                    })
                CONFIG.upload_config_file(verbose)
                
                # make dir for user default.
                try:
                    os.makedirs(USER_PATH / 'default' / 'history')
                except:
                    try: 
                        os.mkdir(USER_PATH / 'default' / 'memory')
                    except:
                        pass
            
            if CONFIG.DATA['users'][CONFIG.DATA['users']['current']] in folders:
                if verbose:
                    print(f"Set user as '{CONFIG.DATA['users'][CONFIG.DATA['users']['current']]}'")
                user = CONFIG.DATA['users'][CONFIG.DATA['users']['current']]
                
        if not scanned: # the above line has been skipped    
            try:
                os.mkdir(USER_PATH)
            except:
                pass
                
            os.mkdir(USER_PATH / 'default')
            os.mkdir(USER_PATH / 'default' / 'history')
            os.mkdir(USER_PATH / 'default' / 'memory')
            CONFIG.DATA['users'].update({
                    'current': '1',
                    '1': 'default',
                })
            CONFIG.upload_config_file(verbose)
      
    else: # user add 'user'.  
        if not CONFIG.check_exist_user_physically(user):
            exist, exist_index = CONFIG.check_exist_user(user)
            
            if exist:
                CONFIG.DATA['users'].update({exist_index: user})
            else:
                CONFIG.DATA['users'].update({len(CONFIG.DATA['users']): user})
            CONFIG.upload_config_file(verbose)
            
            # update on physical directory
            try:
                os.mkdir(USER_PATH)
            except:
                pass
            
            os.mkdir(USER_PATH / user)
            os.mkdir(USER_PATH / user / 'history')
            os.mkdir(USER_PATH / user / 'memory')
            
            if verbose:
                print(f"Created user '{user}'.")
    
    if text_generation_model_name == '':
        _check_for_exist_model(verbose, 'Text_Generation')
        CONFIG.get_config_file(verbose)
        text_generation_model_name = CONFIG.DATA['models']['Text_Generation']
        if verbose:
            print(f'User did not add model for text generation, use {text_generation_model_name} instead.')
        
    if tokenizer_model_name == '':
        _check_for_exist_model(verbose, 'Tokenizer')
        CONFIG.get_config_file(verbose)
        tokenizer_model_name = CONFIG.DATA['models']['Tokenizer']
        if verbose:
            print(f'User did not add model for text generation, use {tokenizer_model_name} instead.')
    
    # load model
    if verbose:
        print('Begin to load models.')
    text_generation_model = AutoModelForCausalLM.from_pretrained(MODEL_PATH / 'Text_Generation' / text_generation_model_name, use_safetensors=True, device_map="auto", torch_dtype=torch.bfloat16) #float32 is wasteful!
    tokenizer_model = AutoTokenizer.from_pretrained(MODEL_PATH / 'Tokenizer' / tokenizer_model_name, use_safetensors=True, device_map="auto", torch_dtype=torch.bfloat16)
    if verbose:
        print('Done loading models.')

    chat_history: list = []
    chat_name: str = ''
    
    # load chat history.
    if verbose:
        print('Loading history.')
    while True:
        scanned: bool = False
        history_list: list = []
        
        for _, _, files in os.walk(USER_PATH / user / 'history'):
            if scanned:
                break
            scanned = True

            if files == []:
                print("There is no history yet, please create one.")
            else:
                print("Choose from:")
            for history in files:
                if history.endswith('.json'):
                    print(f'    - {history.removesuffix('.json')}')
                    history_list.append(history.removesuffix('.json'))

        print("Type 'create [name (Required, 1 WORD ONLY] [system_prompt (Optional)]' to create new history.")
        print("Type 'delete [name (Required, 1 WORD ONLY]' to delete history.")
        print("Type 'exit' to exit.\n")
        command: str = input('>> ')
        if command.lower() in ('exit', 'exit()'):
            break
        
        if command.split()[0].lower() == 'create':
            try:
                chat_name, system_prompt = command.split(maxsplit=3)[1:3]
            except ValueError:
                try:
                    chat_name = command.split()[1]
                except:
                    print('locas start: error: require argument [name]\n')
                    continue
                
                system_prompt = "You are an Assistant named LocalAssistant (Locas). Give the user the best supports as you can."
            
            if chat_name in history_list: # throw error if create same name.
                print(f"locas start: error: name {chat_name} is used\n")
                continue
            
            chat_history = [
                {"role": "system", "content": system_prompt},
            ]
            print()
            break
        
        if command.split()[0].lower() == 'delete':
            try:
                chat_name = command.split()[1]
            except:
                print('locas start: error: require argument [name]\n')
                continue
                
                system_prompt = "You are an Assistant named LocalAssistant (Locas). Give the user the best supports as you can."
            
            if chat_name not in history_list: # throw error if create same name.
                print(f"locas start: error: name {chat_name} is not existed\n")
                continue
            
            os.remove(USER_PATH / user / 'history' / f'{chat_name}.json')
            print()
            continue
        
        
        if command not in history_list:
            print(f'locas start: error: No history name {command}')
            continue
            
        chat_name = command
            
        with open(USER_PATH / user / 'history' / f'{chat_name}.json', mode="r", encoding="utf-8") as read_file:
            chat_history = json.load(read_file)
            read_file.close()
            
        print()
        break

    if chat_name == '':
        return # user typed 'exit'
    
    # chat with history.
    print(f"Start chatting as user '{user}' with '{chat_name}' for history, '{text_generation_model_name}' for text generation and '{tokenizer_model_name}' for tokenizer.\n\nType 'exit' to exit.", end='')
    while True:
        reply = _chat(chat_history, text_generation_model, tokenizer_model, max_new_tokens)
        
        if not reply: # User exit.
            break
        
        chat_history.append(reply)
        
        with open(USER_PATH / user / 'history' / f'{chat_name}.json', mode="w", encoding="utf-8") as write_file:
            json.dump(chat_history, write_file, indent=4)
            write_file.close()
            
