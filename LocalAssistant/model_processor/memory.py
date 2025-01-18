"""Memory processing."""

import os
import logging

import torch
from sentence_transformers import SentenceTransformer, util

from ..utils import ConfigManager, LocalAssistantException

class MemoryExtension:
    """Control users' memory."""
    def __init__(self, model_name: str):
        self.config = ConfigManager()
        self.utils_ext = self.config.utils_ext

        try:
            temp_path: str = os.path.join\
                (self.utils_ext.model_path, 'Sentence_Transformer', model_name)
            self.model = SentenceTransformer(temp_path, local_files_only=True)
        except Exception as err:
            logging.error('Can not load model due to: %s', err)
            raise LocalAssistantException('Can not load model.') from err

    def encode_memory(self) -> None:
        """Encode user's memory."""
        self.config.get_config_file()

        data: list = []
        role: list = []

        logging.info('Get history\'s data.')
        temp_path: str = os.path.join\
            (self.utils_ext.user_path, self.config.data['users'], 'history')
        for history_file in os.scandir(temp_path):
            # if not json file, continue.
            if not history_file.is_file():
                continue
            if not history_file.name.endswith('.json'):
                continue

            # the rest is .json file.
            logging.debug('Reading %s.', history_file.name)

            json_data = self.utils_ext.read_json_file(history_file.path)

            for conversation in json_data:
                if conversation["role"] == "system": # skip system
                    continue
                role.append(conversation["role"])
                data.append(conversation["content"])

        # save memory to json file.
        logging.debug("Transfer data to .json")
        data_to_json: dict = {}
        for index, item in enumerate(data):
            data_to_json.update({
                index: {
                    "role": role[index],
                    "content": item,
                }
            })

        temp_path = os.path.join\
            (self.utils_ext.user_path, self.config.data['users'], 'memory', 'all_memory.json')
        self.utils_ext.write_json_file(temp_path, data_to_json)

        # encode
        encoded_data = self.model.encode(data, convert_to_tensor=True, show_progress_bar=True)

        temp_path = os.path.join\
            (self.utils_ext.user_path, self.config.data['users'], 'memory', 'encoded_memory.pt')
        torch.save(encoded_data, temp_path)

    def ask_query(self, question: str, top_k: int = 0) -> list[str]:
        """Ask query function."""
        self.config.get_config_file()

        if top_k == 0: # user didnt add top k when chat.
            top_k=int(self.config.data["top_k_memory"])

        temp_path: str = os.path.join\
            (self.utils_ext.user_path, self.config.data['users'], 'memory', 'encoded_memory.pt')
        logging.info('Loading memory from encoded data.')
        try:
            encoded_data = torch.load(temp_path, weights_only=True)
        except FileNotFoundError:
            logging.info('Encoded data not found. Encode new data.')
            self.encode_memory()
            encoded_data = torch.load(temp_path, weights_only=True)

        # encode query.
        encoded_question = self.model.encode(question, convert_to_tensor=True)

        # we only ask one question
        hits = util.semantic_search(encoded_question, encoded_data, top_k=top_k)[0]

        # get json file.
        data: dict = {}
        logging.debug('Get json file.')
        temp_path = os.path.join\
            (self.utils_ext.user_path, self.config.data['users'], 'memory', 'all_memory.json')
        data = self.utils_ext.read_json_file(temp_path)

        # Concluding.
        result: list = []
        for hit in hits:
            if hit['score'] < 0.5:
                break
            pointer: dict = data[str(hit["corpus_id"])]
            whose: str = 'Me: ' if pointer['role'] == 'user' else 'You: '

            result.append(f"{whose}'{pointer['content']}'")
            logging.debug("Use memory: %s'%s'", whose, pointer['content'])

        return result
