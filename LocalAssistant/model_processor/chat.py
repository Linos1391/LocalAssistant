"""Chat processing."""

import logging
import os
from threading import Thread
import ast

from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

from ..utils import ConfigManager, LocalAssistantException
from .relation_extraction import RebelExtension
from .docs import DocsQuestionAnswerExtension

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
        kwarg = self.config.load_quantization()

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
        ) -> dict | str:
        """
        Simple chat system.

        Args:
            history (list): list of history.
            text_generation_model (AutoModelForCausalLM): text generation model.
            tokenizer_model (AutoTokenizer): tokenizer of text generation model.
            max_new_tokens (int): max tokens to generate.
            **kwargs: arguments for `apply_chat_template`. Used for memory, etc.

        Returns:
            dict|str: assistant's reply (dict); tool called (str).
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
        tool_calling: bool = False
        for output in streamer:
            output = output.removesuffix('<|im_end|>')

            if output == '<tool_call>\n' and not tool_calling: # got business bois.
                tool_calling = True

            full_output += output
            if not tool_calling:
                print(output, end='', flush=True)
        if tool_calling:
            return full_output
        return {"role": "assistant", "content": full_output}

    def chat_with_limited_lines(
            self,
            lines: int = 1,
            max_new_tokens: int = 500,
        ):
        """
        Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)
        
        Args:
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

        # get text generation model.
        self.config.get_config_file()
        self.config.check_for_exist_model(1)
        text_generation_model_name = self.config.data['models']['Text_Generation']

        # load model
        logging.debug('Begin to load models.')
        text_generation_model, tokenizer_model = self._load_local_model(text_generation_model_name)
        logging.debug('Done loading models.')

        # chat with limited lines.
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
            user: str = 'default',
            max_new_tokens: int = 500,
            top_k_memory: int = 0,
            retrieve_memory_only: bool = False,
        ):
        """
        Chat with models with unlimited lines. History will be saved.
        
        Args:
            user (str): chat by user, default as 'default'.
            max_new_tokens (int): max tokens to generate, default as 500.
            top_k_memory (int): how much memory you want to recall.
            retrieve_memory_only (bool): only retrieve and not saving the later memories.
        """

        self.config.get_config_file()
        self.config.check_for_exist_user(user)

        if top_k_memory == 0:
            try:
                top_k_memory = int(self.config.data["top_k_memory"])
            except ValueError:
                top_k_memory = 25
                self.config.data["top_k_memory"] = 25
                self.config.upload_config_file()

        # get text generation model.
        self.config.check_for_exist_model(1)
        text_generation_model_name = self.config.data['models']['Text_Generation']

        # load model.
        logging.debug('Begin to load models.')
        text_generation_model, tokenizer_model = self._load_local_model(text_generation_model_name)
        memory_ext = RebelExtension()
        memory_ext.get_kb(os.path.join(self.utils_ext.user_path, user, 'memory', 'triplet.json'))
        logging.debug('Done loading models.')

        # load chat history.
        logging.debug('Loading history.')
        chat_history, chat_name = self.utils_ext.load_chat_history(user)

        # user typed 'exit'
        if chat_name == '':
            return

        # Define memory tools
        def retrieve_memory_step_1():
            """
            The first step to retrieve memory, return list of entities. \
Entities are objects that have relationship with one another.
            """
            logging.debug('Model gets memory entities.')
            return memory_ext.entities

        def retrieve_memory_step_2(chosen_entity: str):
            """
            The first step to retrieve memory, return list of relationships. \
Relationship are those relations that given entity has with other entities.

            Args:
                chosen_entity: The entity that got relations retrieved.
            """
            if chosen_entity not in memory_ext.entities:
                raise ValueError("Wrong entity, please try again.")

            print(f"    - Retrieve memory related to '{chosen_entity}'.")
            relationship: list = []
            for relation in memory_ext.relations:
                if chosen_entity in (relation['head'], relation['tail']):
                    relation: dict
                    relationship.append(" ".join(tuple(relation.values())))
            return relationship

        def save_memory(memory: str):
            """
            Only use when you, as an assistant, want to remember something precious about user \
that have just been told during the conversation. Must be short and to the point, 5 words minimum.

            Args:
                memory: what to remember, write it short and to the point, 5 words minimum.
            """
            print(f"    - Memory got saved: '{memory}'")
            memory_ext.from_text_to_kb(memory)

        memory_tools = [retrieve_memory_step_1, retrieve_memory_step_2]
        if not retrieve_memory_only:
            memory_tools.append(save_memory)

        # chat with history.
        print(f"\nStart chatting as user '{user}' with '{chat_name}' for history, \
'{text_generation_model_name}' for text generation.\n\nModels sometimes don't want \
to save memory repetitively, remind them might help! Type 'exit' to exit.", end='')
        tool_calling: bool = False
        while True:
            if not tool_calling:
                prompt: str = input('\n\n>> ')
                print()

                if prompt.lower() in ('exit', 'exit()'):
                    if not retrieve_memory_only:
                        print('Let see what we have today! Saved network at:')
                        temp_path: str = os.path.join(self.utils_ext.user_path, user, 'memory')
                        memory_ext.save_kb(os.path.join(temp_path, 'triplet.json'))
                        memory_ext.save_network_html(os.path.join(temp_path, 'network.html'))
                    return

                # append chat to history.
                chat_history.append({"role": "user", "content": prompt,})

            reply = self._chat(chat_history, text_generation_model,\
                tokenizer_model, max_new_tokens, tools=memory_tools)

            if isinstance(reply, str): # used tool.
                tool_calling = True

                def _extract_tool(function, **kwarg) -> str:
                    try:
                        return f'ANSWER: {str(function(**kwarg))}'
                    except Exception as err:
                        return f'ERROR: {err}'

                chat_history.append({"role": "assistant", "content": reply})

                reply = reply.removeprefix('<tool_call>').removesuffix('</tool_call>')
                reply: dict = ast.literal_eval(reply)

                match reply["name"]:
                    case 'retrieve_memory_step_1':
                        tool_return=_extract_tool(retrieve_memory_step_1,**reply["arguments"])
                        chat_history.append({"role": "tools", "content": f"{tool_return}. \
Go step 2 right after. If no entities can be used or get errors, tell user so and end retrieving."})

                    case 'retrieve_memory_step_2':
                        tool_return=_extract_tool(retrieve_memory_step_2,**reply["arguments"])
                        chat_history.append({"role": "tools", "content": f"{tool_return}. \
Please use this information for user's benefit."})

                    case 'save_memory':
                        tool_return=_extract_tool(save_memory,**reply["arguments"])
                        chat_history.append({"role": "tools", "content": \
                            f"{"Return: Successfully saved. Please continue the conversation."\
                                if tool_return.endswith('None') else tool_return}."})

            else: # just a normal chat.
                tool_calling = False
                chat_history.append(reply)

            # save history
            temp_path: str = os.path.join\
                (self.utils_ext.user_path, user, 'history', f'{chat_name}.json')
            self.utils_ext.write_json_file(temp_path, chat_history)

            # save memory
            if not retrieve_memory_only:
                temp_path: str = os.path.join(self.utils_ext.user_path,user,'memory','triplet.json')
                memory_ext.save_kb(temp_path)


    def docs_question_answer(
            self,
            max_new_tokens: int = 500,
            top_k: int = 0,
            allow_score: float = 0.0,
            encode_at_start: bool = False,
            show_retrieve: bool = False,
        ):
        """
        Ask information from provided docs.

        Args:
            max_new_tokens (int): max tokens to generate, default as 500.
            top_k (int, optional): how many sentences you want to retrieve.
            allow_score (float, optional): retrieving process will stop when \
                similiarity score is lower.
            encode_at_start (bool, optional): encode memory before chating.
            show_retrieve (bool, optional): show retrieved data.
        """
        self.config.get_config_file()

        # get text generation model.
        self.config.check_for_exist_model(1)
        text_generation_model_name = self.config.data['models']['Text_Generation']

        # get sentence transformer model.
        self.config.check_for_exist_model(2)
        sentence_transformer_model_name = self.config.data['models']['Sentence_Transformer']

        # get cross encoder model.
        self.config.check_for_exist_model(3)
        cross_encoder_model_name = self.config.data['models']['Cross_Encoder']

        history: list = [
            {
                "role": "system", 
                "content": "You are an Assistant named LocalAssistant (Locas). \
Got provided with tons of docs, your duty is answering user's questions the best as possible. \
If docs' data are nonsense, you can ignore them and use your own words."
            },
        ]

        # load model
        logging.debug('Begin to load models.')
        text_generation_model, tokenizer_model = self._load_local_model(text_generation_model_name)
        docs_ext = DocsQuestionAnswerExtension\
                (sentence_transformer_model_name, cross_encoder_model_name)
        if encode_at_start:
            print("Encoding at start. Please be patient, it may take some minutes.")
            docs_ext.encode()
        logging.debug('Done loading models.')

        print(f"Start docs Q&A with '{text_generation_model_name}' for text generation, \
'{sentence_transformer_model_name}' for sentence transformer, '{cross_encoder_model_name}' \
for cross encoder.\n\nType 'exit' to exit.", end='')

        while True:
            prompt: str = input('\n\n>> ')
            print()

            if prompt.lower() in ('exit', 'exit()'):
                return

            docs_data: list = docs_ext.ask_query(prompt, top_k, allow_score)
            docs_dict: dict = {}
            for data in docs_data:
                try:
                    docs_dict[data['title']].append(data['content'])
                except KeyError:
                    docs_dict.update({data['title']: [data['content']]})

            prompt_input: str = "Retrieved data from docs:\n"
            for index, (title, content) in enumerate(docs_dict.items()):
                prompt_input += f"{index}. From file '{title}':\n"
                for text in content:
                    prompt_input += f"  - {text}\n"
                prompt_input += '\n'

            if show_retrieve:
                div: int = os.get_terminal_size().columns * '-'
                print(f'{div}\n{prompt_input}{div}\n')

            prompt_input += f"\nQuestion: {prompt}"
            history.append({"role": "user", "content": prompt_input,})

            reply = self._chat(history, text_generation_model, tokenizer_model, max_new_tokens)

            history.append(reply)
