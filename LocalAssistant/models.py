import os
import pathlib
import json
from threading import Thread

from huggingface_hub import login, logout
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer, BitsAndBytesConfig
from sentence_transformers import SentenceTransformer, util
import torch

from utils import LocalAssistantException, LocalAssistantConfig, MODEL_PATH, USER_PATH, LOGGER

CONFIG = LocalAssistantConfig()

class ModelTask:
    NONE = 0
    TEXT_GENERATION = 1
    SENTENCE_TRANSFORMER = 2
    # TODO - Add more model:
    # 1.n.n
    # - SENTENCE TRANSFORMATION \ CROSS_ENCODER (Extract data from database)
    # - Search google https://github.com/Nv7-GitHub/googlesearch
    # 2.n.n
    # - TEXT_TO_SPEECH (Voice from AI)
    # - SPEECH_TO_TEXT (Voice chat)
    # - AUDIO_CLASSIFICATION (Multiple user voice chat - https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) I will cook.
    
    def name_task(self, task: int) -> str:
        # for O(1).
        if task == self.NONE: return 'None'
        elif task == self.TEXT_GENERATION: return 'Text_Generation'
        elif task == self.SENTENCE_TRANSFORMER: return 'Sentence_Transformer'
        
        raise LocalAssistantException("Task not found.")
    
    def reverse_name_task(self, task: str) -> str:
        # also for O(1).
        if task == 'None': return self.NONE
        elif task == 'Text_Generation': return self.TEXT_GENERATION
        elif task == 'Sentence_Transformer': return task == self.SENTENCE_TRANSFORMER
        
        raise LocalAssistantException("Task not found.")

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
    LOGGER.debug('Check .cache dir')
    try:
        os.makedirs(MODEL_PATH / '.cache')
    except: # ignore if it existed
        pass
      
def _save_model(model, path: str) -> None:
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
        LOGGER.debug(f'Made {parent.name} directory')
    
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
                    LOGGER.debug(f'Found {folder}.')

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
                    LOGGER.debug(f'Found {file}.')

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
    
    LOGGER.info(f'Save as {child} in {parent.name}.')    
        
    model.save_pretrained(str(parent / child))  

def download_model_by_HuggingFace(
        model_name: str,
        huggingface_path: str,
        hf_token: str = '',
        task: int = ModelTask.NONE,
    ) -> None:
    
    """
    Download model directly from Hugging Face and save it in `models` folder.
    Args:
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
    
    # For text generation.
    if task == ModelTask.TEXT_GENERATION:
        LOGGER.info(f'Download text generation model from {huggingface_path}')
        try: 
            if hf_token == '': # by default, do not use token.
                LOGGER.debug('Not use token.')
                try: 
                    tokenizer_model = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
                    text_generation_model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=huggingface_path, use_safetensors=True, device_map="auto", cache_dir=MODEL_PATH / '.cache')
                except Exception as e:
                    LOGGER.error(f'Can not download text generation model due to: {e}')
                    raise e

            else: # use token.
                LOGGER.debug(f'Use provided token: {hf_token}')
                tokenizer_model = _download_with_login(hf_token, huggingface_path, AutoTokenizer)
                text_generation_model = _download_with_login(hf_token, huggingface_path, AutoModelForCausalLM)
                LOGGER.debug('Log out from token.')
                if isinstance(tokenizer_model, Exception):
                    LOGGER.error(f'Can not download text generation model due to: {tokenizer_model}')
                    raise tokenizer_model
                if isinstance(text_generation_model, Exception):
                    LOGGER.error(f'Can not download text generation model due to: {text_generation_model}')
                    raise text_generation_model
        except Exception as e:
            LOGGER.error(f'Can not download text generation model due to: {e}')
            raise e
        
        # save downloaded model
        _save_model(text_generation_model, MODEL_PATH / 'Text_Generation' / model_name)
        _save_model(tokenizer_model, MODEL_PATH / 'Text_Generation' / model_name / 'Tokenizer')
    
    if task == ModelTask.SENTENCE_TRANSFORMER:
        LOGGER.info(f'Download sentence transformer model from {huggingface_path}')
        try: 
            if hf_token == '': # by default, do not use token.
                LOGGER.debug('Not use token.')
                try: 
                    sentence_transformer_model = SentenceTransformer(model_name_or_path=huggingface_path, cache_folder=MODEL_PATH / '.cache')
                except Exception as e:
                    LOGGER.error(f'Can not download sentence transformer model due to: {e}')
                    raise e

            else: # use token.
                LOGGER.debug(f'Use provided token: {hf_token}')
                try: 
                    sentence_transformer_model = SentenceTransformer(model_name_or_path=huggingface_path, token=hf_token, cache_folder=MODEL_PATH / '.cache')
                except Exception as e:
                    LOGGER.error(f'Can not download sentence transformer model due to: {e}')
                    raise e
                LOGGER.debug('Log out from token.')
                
        except Exception as e:
            LOGGER.error(f'Can not download sentence transformer model due to: {e}')
            raise e
        
        # save downloaded model
        _save_model(sentence_transformer_model, MODEL_PATH / 'Sentence_Transformer' / model_name)

# +-----------------+
# | Memory function |
# +-----------------+
        
# check exist model for each task
def _check_for_exist_model(task: str) -> None:
    """
    Check for exist model. There is nothing we can do if the user chats without any models.
    """
    CONFIG.get_config_file()
    
    if task not in ('Text_Generation', 'Sentence_Transformer'): # Well... sometime I suck
        LOGGER.error(f"Wrong task. Expected 'Text_Generation', but got '{task}'")
        raise LocalAssistantException(f"Wrong task. Expected 'Text_Generation', 'Sentence_Transformer', but got '{task}'")
     
    if CONFIG.DATA['models'][task] != '':
        return # nothing to fix.
    
    scanned: bool = False
    for _, folders, _ in os.walk(MODEL_PATH / task):
        if scanned:
            break
        
        scanned = True
        CONFIG.DATA['models'][task] = folders[0] # if there is no model, this has ignored
            
    if not scanned: # the above line has skipped
        LOGGER.critical(f"There is no models for {task}. Please type 'locas download -h' and download one.")
        raise LocalAssistantException(f"There is no models for {task}. Please type 'locas download -h' and download one.")
    
    CONFIG.upload_config_file()
    LOGGER.info(f'Apply {folders[0]} as model for {task}.')

# Act with memory
class LocalAssistantMemory:
    """
    Control users' memory.
    """
    def __init__(self, model_name):
        if model_name != '':
            try:
                self.Model = SentenceTransformer(model_name_or_path=os.path.join(MODEL_PATH, 'Sentence_Transformer', model_name), local_files_only=True)
            except Exception as e:
                LOGGER.error(e)
                raise e
            
            return
        
        _check_for_exist_model('Sentence_Transformer')
        try:
            self.Model = SentenceTransformer(model_name_or_path=os.path.join(MODEL_PATH, 'Sentence_Transformer', CONFIG.DATA["models"]["Sentence_Transformer"]), local_files_only=True)
        except Exception as e:
            LOGGER.error(e)
            raise e
    
    def encode_memory(self) -> None:
        CONFIG.get_config_file()
        DATA: list = []
        ROLE: list = []
        
        # make file if it not exist yet
        if not CONFIG.check_exist_user_physically(CONFIG.DATA['users'][CONFIG.DATA['users']['current']]):
            try:
                os.makedirs(USER_PATH / CONFIG.DATA['users'][CONFIG.DATA['users']['current']] / 'history')
                LOGGER.debug('History folder is not existed.')
            except:
                pass
            
            try:
                os.makedirs(USER_PATH / CONFIG.DATA['users'][CONFIG.DATA['users']['current']] / 'memory')
                LOGGER.debug('Memory folder is not existed.')
            except:
                pass
            
        LOGGER.info('Get history\'s data.')
        for history_file in os.scandir(USER_PATH / CONFIG.DATA['users'][CONFIG.DATA['users']['current']] / 'history'):
            # if not json file, continue.
            if not history_file.is_file():
                continue
            if not history_file.name.endswith('.json'):
                continue
        
            # the rest is .json file.
            LOGGER.debug(f'Reading {history_file.name}')
            with open(history_file.path, mode="r", encoding="utf-8") as read_file:
                data = json.load(read_file)
                for conversation in data:
                    if conversation["role"] == "system": # skip system
                        continue
                    ROLE.append(conversation["role"])
                    DATA.append(conversation["content"])
                read_file.close()
        
        # save memory to json file.
        LOGGER.debug("Transfer data to .json")
        data_to_json: dict = {}
        for index, item in enumerate(DATA):
            data_to_json.update({
                index: {
                    "role": ROLE[index],
                    "content": item,
                }
            })
        
        with open(os.path.join(USER_PATH, CONFIG.DATA['users'][CONFIG.DATA['users']['current']], 'memory', 'all_memory.json'), mode="w", encoding="utf-8") as write_file:
            json.dump(data_to_json, write_file, indent=4)
            write_file.close()
        
        # encode
        print('Encoding data...')
        encoded_data = self.Model.encode(DATA, convert_to_tensor=True, show_progress_bar=True)
        
        CONFIG.get_config_file()
        torch.save(encoded_data, os.path.join(USER_PATH / CONFIG.DATA['users'][CONFIG.DATA['users']['current']], 'memory', 'encoded_memory.pt'))
            
    def ask_query(self, question: str, top_k: int = 5) -> list[str]:
        CONFIG.get_config_file()
        
        if top_k == 0: # user didnt add top k when chat.
            top_k=int(CONFIG.DATA["top_k_memory"])
        
        # if you can't do it again.
        LOGGER.info('Loading memory from encoded data.')
        try:
            encoded_data = torch.load(os.path.join(USER_PATH / CONFIG.DATA['users'][CONFIG.DATA['users']['current']], 'memory', 'encoded_memory.pt'), weights_only=True)
        except FileNotFoundError:
            LOGGER.info('Encoded data not found. Encode new data.')
            self.encode_memory()
            encoded_data = torch.load(os.path.join(USER_PATH / CONFIG.DATA['users'][CONFIG.DATA['users']['current']], 'memory', 'encoded_memory.pt'), weights_only=True)
            
        # encode query.
        encoded_question = self.Model.encode(question, convert_to_tensor=True)
        
        # we only ask one question
        hits = util.semantic_search(encoded_question, encoded_data, top_k=top_k)[0]
        
        # get json file.
        data: dict = {}
        LOGGER.debug('Get json file.')
        with open(os.path.join(USER_PATH, CONFIG.DATA['users'][CONFIG.DATA['users']['current']], 'memory', 'all_memory.json'), mode="r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            read_file.close()
        
        # Concluding.
        result: list = []
        for hit in hits:
            pointer: dict = data[str(hit["corpus_id"])]
            whose: str = 'I said: ' if pointer['role'] == 'user' else 'You said: '
            
            result.append(f"{whose}'{pointer['content']}'")
        
        return result
    
# +----------------+
# | locas chat ... |
# +----------------+

def _load_local_model(model_name: str) -> tuple:
    path: str = MODEL_PATH / 'Text_Generation' / model_name # for better path
    
    CONFIG.get_config_file()
    used_bit = CONFIG.DATA["load_in_bits"]
    
    # for O(1) I guess
    if used_bit == '32':
        return (
            AutoModelForCausalLM.from_pretrained(path, local_files_only=True, use_safetensors=True, device_map="auto", torch_dtype=torch.float32),
            AutoTokenizer.from_pretrained(path / 'Tokenizer', local_files_only=True, use_safetensors=True, device_map="auto", torch_dtype=torch.float32),
        )
    elif used_bit == '16': # float16 sucks so we use bfloat16
        return (
            AutoModelForCausalLM.from_pretrained(path, local_files_only=True, use_safetensors=True, device_map="auto", torch_dtype=torch.bfloat16),
            AutoTokenizer.from_pretrained(path / 'Tokenizer', local_files_only=True, use_safetensors=True, device_map="auto", torch_dtype=torch.bfloat16),
        )
    elif used_bit == '8':
        return (
            AutoModelForCausalLM.from_pretrained(path, local_files_only=True, use_safetensors=True, device_map="auto", quantization_config=BitsAndBytesConfig(load_in_8bit=True)),
            AutoTokenizer.from_pretrained(path / 'Tokenizer', local_files_only=True, use_safetensors=True, device_map="auto", quantization_config=BitsAndBytesConfig(load_in_8bit=True)),
        )
    elif used_bit == '4':
        return (
            AutoModelForCausalLM.from_pretrained(path, local_files_only=True, use_safetensors=True, device_map="auto", quantization_config=BitsAndBytesConfig(load_in_4bit=True)),
            AutoTokenizer.from_pretrained(path / 'Tokenizer', local_files_only=True, use_safetensors=True, device_map="auto", quantization_config=BitsAndBytesConfig(load_in_4bit=True)),
        )
        
    raise LocalAssistantException(f"Invalid bits! We found: {used_bit}")

def _chat(history: list, text_generation_model, tokenizer_model, max_new_tokens) -> dict:
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
        text_generation_model_name: str = '',
        lines: int = 1,
        max_new_tokens: int = 150,
    ):
    """
    Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
    Args:
        text_generation_model_name (str): name of the text generation model, get from config file if got blank.
        lines (int): lines of chat (not count 'assistant'), default as 1.
        max_new_tokens (int): max tokens to generate, default as 150.
    """
    
    if lines < 1:
        raise LocalAssistantException("Argument 'lines' should not have non-positive value.")
    
    history: list = [
        {"role": "system", "content": f"You are an Assistant named LocalAssistant (Locas). You only have {lines} lines, give the user the best supports as you can."},
    ]
    
    if text_generation_model_name == '':
        _check_for_exist_model('Text_Generation')
        text_generation_model_name = CONFIG.DATA['models']['Text_Generation']
        LOGGER.info(f'User did not add model for text generation, use {text_generation_model_name} instead.')
    
    # load model
    LOGGER.debug('Begin to load models.')
    text_generation_model, tokenizer_model = _load_local_model(text_generation_model_name)
    LOGGER.debug('Done loading models.')
    
    # chat with limited lines
    print(f"\nStart chatting in {lines} lines with '{text_generation_model_name}' for text generation.\n\nType 'exit' to exit.", end='')
    for _ in range(lines):
        prompt: str = input('\n\n>> ')
        print()
        
        # append chat to history.
        history.append({"role": "user", "content": prompt,})
        
        reply = _chat(history, text_generation_model, tokenizer_model, max_new_tokens)
        history.append(reply)
        
    # If user want to continue. Sometimes the conversation is cool I guess...
    while True:
        # If don't want to, end this loop
        print("\n\n------------------------------------")
        if input(f"Finished {lines} lines. Want to keep chatting with next 1 line? [y/n]: ").lower() != 'y': # Everything but 'y' is not allowed
            print("------------------------------------")
            break 
        print("------------------------------------", end='')
        
        prompt: str = input('\n\n>> ')
        print()
    
        if prompt.lower() in ('exit', 'exit()'):
            break
        
        # append chat to history.
        history.append({"role": "user", "content": prompt,})
        
        reply = _chat(prompt, history, text_generation_model, tokenizer_model, max_new_tokens)
        history.append(reply)
    

# +-----------------+
# | locas start ... |
# +-----------------+

def chat_with_history(
        text_generation_model_name: str = '',
        user: str = 'default',
        max_new_tokens: int = 150,
        memory_enable: bool = False,
        sentence_transformer_model_name: str = '',
        top_k_memory: int = 0,
        encode_at_start: bool = False,
    ):
    """
    Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
    Args:
        text_generation_model_name (str): name of the text generation model, get from config file if got blank.
        user (str): chat by user, default as 'default'.
        max_new_tokens (int): max tokens to generate, default as 50.
        memory_enable (bool): enable memory function, default as False.
        sentence_transformer_model_name (str): name of the sentence transformer model, get from config file if got blank. (only memory_enable == True)
        top_k_memory (int): how much memory you want to recall. (only memory_enable == True)
        encode_at_start (bool): encode memory before chating. (only memory_enable == True)
    """

    CONFIG.get_config_file()

    if user == 'default': # user did not add 'user'.
        scanned: bool = False
        for _, folders, _ in os.walk(USER_PATH):
            if scanned:
                break
            scanned = True
            
            if CONFIG.DATA['users']['current'] == '': # not in config file
                LOGGER.info("Config file does not have current user. Set user as default.")
                
                CONFIG.DATA['users'].update({
                        'current': '1',
                        '1': 'default',
                    })
                CONFIG.upload_config_file()
                
                # make dir for user default.
                try:
                    os.makedirs(USER_PATH / 'default' / 'history')
                except:
                    try: 
                        os.mkdir(USER_PATH / 'default' / 'memory')
                    except:
                        pass
            
            if CONFIG.DATA['users'][CONFIG.DATA['users']['current']] in folders:
                LOGGER.info(f"Set user as '{CONFIG.DATA['users'][CONFIG.DATA['users']['current']]}'")
                user = CONFIG.DATA['users'][CONFIG.DATA['users']['current']]
                
        if not scanned: # the above line has been skipped    
            LOGGER.info("Can not find './users' directory, make one.")
            
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
            CONFIG.upload_config_file()
      
    else: # user add 'user'.  
        if not CONFIG.check_exist_user_physically(user):
            exist, exist_index = CONFIG.check_exist_user(user)
            
            if exist:
                CONFIG.DATA['users'].update({exist_index: user})
            else:
                CONFIG.DATA['users'].update({len(CONFIG.DATA['users']): user})
            CONFIG.upload_config_file()
            
            # update on physical directory
            try:
                os.mkdir(USER_PATH)
            except:
                pass
            
            os.mkdir(USER_PATH / user)
            os.mkdir(USER_PATH / user / 'history')
            os.mkdir(USER_PATH / user / 'memory')
            
            LOGGER.debug(f"Created user '{user}'.")
    
    if text_generation_model_name == '':
        _check_for_exist_model('Text_Generation')
        text_generation_model_name = CONFIG.DATA['models']['Text_Generation']
        LOGGER.info(f'User did not add model for text generation, use {text_generation_model_name} instead.')
    
    # load model
    LOGGER.debug('Begin to load models.')
    text_generation_model, tokenizer_model = _load_local_model(text_generation_model_name)
    if memory_enable:
        Memory = LocalAssistantMemory(sentence_transformer_model_name)
        if encode_at_start:
            LOGGER.info('User choose to encode at start.')
            Memory.encode_memory()
    LOGGER.debug('Done loading models.')

    chat_history: list = []
    chat_name: str = ''
    
    # load chat history.
    LOGGER.debug('Loading history.')
    while True:
        scanned: bool = False
        history_list: list = []
        
        for _, _, files in os.walk(USER_PATH / user / 'history'):
            if scanned:
                break
            scanned = True

            if files == []:
                print("\nThere is no history yet, please create one.")
            else:
                print("\nChoose from:")
            for history in files:
                if history.endswith('.json'):
                    print(f'    - {history.removesuffix('.json')}')
                    history_list.append(history.removesuffix('.json'))

        print("\nType 'create [name (Required, 1 WORD ONLY] [system_prompt (Optional)]' to create new history.")
        print("Type 'delete [name (Required, 1 WORD ONLY]' to delete history.")
        print("Type 'exit' to exit.\n")
        command: str = input('>> ')
        if command.lower() in ('exit', 'exit()'):
            break
        
        if command.split()[0].lower() == 'create':
            try:
                command_split = command.split()
                chat_name = command_split[1]
                system_prompt = ' '.join(command_split[2:])
            except ValueError:
                try:
                    chat_name = command.split()[1]
                except:
                    print('locas start: error: require argument [name]\n')
                    LOGGER.error('require argument [name]')
                    exit()
                
                if user == 'default':
                    system_prompt = "You are an Assistant named LocalAssistant (Locas). Give the user the best supports as you can."
                else:
                    system_prompt = f"You are an Assistant named LocalAssistant (Locas) who serves the user called {user}. Give {user} the best supports as you can."
            
            if chat_name in history_list: # throw error if create same name.
                print(f"locas start: error: name {chat_name} is used\n")
                LOGGER.error(f"name {chat_name} is used")
                exit()
            
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
                LOGGER.error('require argument [name]')
                exit()
            
            if chat_name not in history_list: # throw error if create same name.
                print(f"locas start: error: name {chat_name} is not existed\n")
                LOGGER.error(f'name {chat_name} is not existed')
                exit()
            
            os.remove(USER_PATH / user / 'history' / f'{chat_name}.json')
            print()
            continue
        
        
        if command not in history_list:
            LOGGER.error(f'no history name {command}')
            print(f'locas start: error: no history name {command}\n')
            exit()
            
        chat_name = command
            
        with open(USER_PATH / user / 'history' / f'{chat_name}.json', mode="r", encoding="utf-8") as read_file:
            chat_history = json.load(read_file)
            read_file.close()
            
        print()
        break

    if chat_name == '':
        return # user typed 'exit'
    
    # chat with history.
    line_print: str = f"Start chatting as user '{user}' with '{chat_name}' for history, '{text_generation_model_name}' for text generation"
    if memory_enable:
        line_print += f", '{sentence_transformer_model_name}' for sentence transformer"
    print(f"{line_print}.\n\nType 'exit' to exit.", end='')
    
    while True:
        prompt: str = input('\n\n>> ')
        print()
        
        if prompt.lower() in ('exit', 'exit()'):
            if memory_enable:
                print('Encoding the our story...')
                Memory.encode_memory()
            exit()
            
        # append chat to history.
        chat_history.append({"role": "user", "content": prompt,})
        
        if memory_enable:
            memories: list = Memory.ask_query(prompt, top_k_memory)
            print("Your memories that are related to the prompt:")
            for index, memory in enumerate(memories):
                print(f'    {index+1}. {memory}')
            while True:
                mem_to_use: str = ''
                for index in input("Memory to chat with ('Eg: 1 3 4 6' or leave blank to not use): ").split():
                    try: # never understimate your user.
                        index = int(index) - 1
                        mem_to_use += f"\n- {memories[index]}"

                    except ValueError: # 1st line
                        LOGGER.error('user used memory can\'t convert into interger')
                        print('locas chat: error: user used memory can\'t convert into interger\n')
                        mem_to_use = 'loop'
                        break

                    except IndexError: # 2nd line
                        LOGGER.error('user used unknown memory')
                        print('locas chat: error: user used unknown memory\n')
                        mem_to_use = 'loop'
                        break
                if mem_to_use != 'loop':
                    print()
                    break
                

            if mem_to_use not in ('', 'loop'): # got memory
                prompt += f'Memory about our last conversation:{mem_to_use}'
        
        reply = _chat(chat_history, text_generation_model, tokenizer_model, max_new_tokens)
        
        chat_history.append(reply)
        
        with open(USER_PATH / user / 'history' / f'{chat_name}.json', mode="w", encoding="utf-8") as write_file:
            json.dump(chat_history, write_file, indent=4)
            write_file.close()

