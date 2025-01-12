"""Chat processing."""

import logging
import os
from threading import Thread

from transformers import AutoTokenizer, AutoModelForCausalLM,\
    TextIteratorStreamer, BitsAndBytesConfig

from ..utils import ConfigManager, LocalAssistantException
from .memory import MemoryExtension

class ChatExtension():
    """Chat extention for LocalAssistant."""
    def __init__(self):
        self.config = ConfigManager()
        self.utils_ext = self.config.utils_ext

    def _load_local_model(self, model_name: str) -> tuple:
        """
        Load text generation model with wanted bits.

        Args:
            model_name (str): Name of model.

        Raises:
            LocalAssistantException: invalid bits.

        Returns:
            tuple: (text generation, tokenizer)
        """
        path: str = os.path.join(self.utils_ext.model_path, 'Text_Generation', model_name)
        kwarg = dict(local_files_only=True,use_safetensors=True, device_map="auto",)

        used_bit = self.config.data["load_in_bits"]
        match used_bit:
            case '8':
                kwarg.update({'quantization_config': BitsAndBytesConfig(load_in_8bit=True)})
            case '4':
                kwarg.update({'quantization_config': BitsAndBytesConfig(load_in_4bit=True)})
            case 'None':
                pass
            case _:
                logging.error('Invalid bits! We found: %s.', used_bit)
                raise LocalAssistantException(f"Invalid bits! We found: {used_bit}.")
        kwarg.update()
        return (
            AutoModelForCausalLM.from_pretrained(path, **kwarg ),
            AutoTokenizer.from_pretrained(os.path.join(path, 'Tokenizer'), **kwarg)
        )

    @staticmethod
    def _chat(
            history: list,
            text_generation_model: AutoModelForCausalLM,
            tokenizer_model: AutoTokenizer,
            max_new_tokens: int,
            **kwargs,
        ) -> dict:
        """
        Simple chat system.

        Args:
            history (list): list of history.
            text_generation_model (AutoModelForCausalLM): text generation model.
            tokenizer_model (AutoTokenizer): tokenizer of text generation model.
            max_new_tokens (int): max tokens to generate.
            **kwargs: arguments for `apply_chat_template`. Used for memory, etc.

        Returns:
            dict: assistant's whole output.
        """
        # format history.
        format_history = tokenizer_model\
            .apply_chat_template(history, tokenize=False, add_generation_prompt=True, **kwargs)

        input_token = tokenizer_model(format_history, return_tensors="pt", add_special_tokens=False)

        # move token to device.
        input_token = {key: tensor.to(text_generation_model.device)\
            for key, tensor in input_token.items()}

        # make streamer.
        streamer = TextIteratorStreamer(tokenizer_model, skip_prompt=True)

        # threading the generation
        kwargs = dict(input_token, streamer=streamer, max_new_tokens=max_new_tokens, do_sample=True)
        thread = Thread(target=text_generation_model.generate, kwargs=kwargs)
        thread.start()

        full_output: str = ''
        for output in streamer:
            output = output.removesuffix('<|im_end|>')

            full_output += output
            print(output, end='', flush=True)

        return {"role": "assistant", "content": full_output}

    def chat_with_limited_lines(
            self,
            text_generation_model_name: str = '',
            lines: int = 1,
            max_new_tokens: int = 500,
        ):
        """
        Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
        
        Args:
            text_generation_model_name (str): text generation model's name, use config if blank.
            lines (int): lines of chat (not count 'assistant'), default as 1.
            max_new_tokens (int): max tokens to generate, default as 500.
        """

        if lines < 1:
            raise LocalAssistantException("Argument 'lines' should not have non-positive value.")

        history: list = [
            {
                "role": "system", 
                "content": f"You are an Assistant named LocalAssistant (Locas). \
You only have {lines} lines, give the user the best supports as you can."
            },
        ]

        if text_generation_model_name == '':
            self.config.get_config_file()
            self.config.check_for_exist_model(1)
            text_generation_model_name = self.config.data['models']['Text_Generation']
            logging.info('No text generation model, use %s instead.', text_generation_model_name)

        # load model
        logging.debug('Begin to load models.')
        text_generation_model, tokenizer_model = self._load_local_model(text_generation_model_name)
        logging.debug('Done loading models.')

        # chat with limited lines
        print(f"\nStart chatting in {lines} line(s) with '{text_generation_model_name}'\
for text generation.\n\nType 'exit' to exit.", end='')

        for _ in range(lines):
            prompt: str = input('\n\n>> ')
            print()

            if prompt.lower() in ('exit', 'exit()'):
                break

            # append chat to history.
            history.append({"role": "user", "content": prompt,})

            reply = self._chat(history, text_generation_model, tokenizer_model, max_new_tokens)
            history.append(reply)

        # If user want to continue. Sometimes the conversation is cool I guess...
        while True:
            # If don't want to, end this loop
            print("\n\n------------------------------------")
            if input(f"Finished {lines} lines. Want to keep chatting? [y/n]: ").lower() != 'y':
                print("------------------------------------")
                break
            print("------------------------------------", end='')

            prompt: str = input('\n\n>> ')
            print()

            if prompt.lower() in ('exit', 'exit()'):
                break

            # append chat to history.
            history.append({"role": "user", "content": prompt,})

            reply = self._chat(history, text_generation_model, tokenizer_model, max_new_tokens)
            history.append(reply)

    def chat_with_history(
            self,
            text_generation_model_name: str = '',
            user: str = 'default',
            max_new_tokens: int = 500,
            memory_enable: bool = False,
            sentence_transformer_model_name: str = '',
            top_k_memory: int = 0,
            encode_at_start: bool = False,
        ):
        """
        Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
        
        Args:
            text_generation_model_name (str): text generation model's name, use config if blank.
            user (str): chat by user, default as 'default'.
            max_new_tokens (int): max tokens to generate, default as 500.
            
            memory_enable (bool): enable memory function, default as False.
            sentence_transformer_model_name (str): sentence transformer model's name, \
                use config if blank.
            top_k_memory (int): how much memory you want to recall.
            encode_at_start (bool): encode memory before chating.
        """

        self.config.get_config_file()
        self.config.check_for_exist_user(user)

        if text_generation_model_name == '':
            self.config.check_for_exist_model(1)
            text_generation_model_name = self.config.data['models']['Text_Generation']
            logging.info('No text generation model, use %s instead.', text_generation_model_name)

        if memory_enable and sentence_transformer_model_name == '':
            self.config.check_for_exist_model(2)
            sentence_transformer_model_name = self.config.data['models']['Sentence_Transformer']
            logging.info('No sentence transformer model, \
use %s instead.', sentence_transformer_model_name)

        # load model
        logging.debug('Begin to load models.')
        text_generation_model, tokenizer_model = self._load_local_model(text_generation_model_name)
        if memory_enable:
            memory_ext = MemoryExtension(sentence_transformer_model_name) # --- start here ---
            if encode_at_start:
                logging.info('Encoding at start.')
                memory_ext.encode_memory()
        logging.debug('Done loading models.')

        # load chat history.
        logging.debug('Loading history.')
        chat_history, chat_name = self.config.load_chat_history(user)

        # user typed 'exit'
        if chat_name == '':
            return

        # chat with history.
        line_print: str = f"Start chatting as user '{user}' with \
'{chat_name}' for history, '{text_generation_model_name}' for text generation"
        if memory_enable:
            line_print += f", '{sentence_transformer_model_name}' for sentence transformer"
        print(f"{line_print}.\n\nType 'exit' to exit.", end='')

        while True:
            prompt: str = input('\n\n>> ')
            print()

            if prompt.lower() in ('exit', 'exit()'):
                if memory_enable:
                    print('Encoding the our story...')
                    memory_ext.encode_memory()
                return

            # append chat to history.
            chat_history.append({"role": "user", "content": prompt,})

            kwargs = {}
            if memory_enable:
                memories: list = memory_ext.ask_query(prompt, top_k_memory)
                if memories:
                    kwargs = {'memories': memories}

            reply = self._chat(chat_history, text_generation_model,\
                tokenizer_model, max_new_tokens, **kwargs)

            chat_history.append(reply)

            temp_path: str = os.path.join\
                (self.utils_ext.user_path, user, 'history', f'{chat_name}.json')
            self.utils_ext.write_json_file(temp_path, chat_history)
