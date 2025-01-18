"""Help downloading models."""

import logging
import os
import pathlib

from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer, CrossEncoder

from ..utils import UtilsExtension, LocalAssistantException

class DownloadExtension:
    """Download extention for LocalAssistant."""
    def __init__(self):
        self.utils_ext = UtilsExtension()

    @staticmethod
    def _download_model(
            huggingface_path: str,
            model,
            hf_token: str = '',
        ):
        """
        Some models might be restricted and need authenticated. \
            Use token to login temporately and download model.

        Args:
            huggingface_path (str): path to huggingface model (author/model_name)
            model (Any): model is used.
            hf_token (str): huggingface's token.
        """
        if hf_token == '': # by default, do not use token.
            hf_token: None = None
            logging.debug('Not use token.')
        else:
            logging.debug('Use provided token: %s.', hf_token)

        try:
            if isinstance(model, SentenceTransformer):
                return SentenceTransformer(huggingface_path, token=hf_token)
            if model == 'CrossEncoder':
                return CrossEncoder(huggingface_path)
            return model.from_pretrained\
                (huggingface_path, use_safetensors=True, device_map="auto", token=hf_token)
        except Exception as err:
            logging.error('Can not download model due to: %s.', err)
            raise LocalAssistantException('Can not download model.') from err


    @staticmethod
    def _save_model(
            model:AutoTokenizer|AutoModelForCausalLM|SentenceTransformer,
            path: str|pathlib.Path,
        ) -> str:
        """
        Save model to path. Check if the name has taken and rename. (only dir)

        Args:
            model (AutoTokenizer | AutoModelForCausalLM | SentenceTransformer): model is used.
            path (str | pathlib.Path): path to save to.

        Returns:
            str: path after fixed.
        """
        # take parent and child path
        path = pathlib.Path(path)

        parent: pathlib.Path = path.parent
        child: str = path.name

        try: # make dir if dir not exist
            os.makedirs(parent)
            logging.debug('Made %s directory.', parent.name)
        except FileExistsError:
            pass

        stop: bool = False
        scanned: bool = False
        while not stop:
            for item in os.scandir(parent):
                scanned = True

                if item.name == child:
                    if not item.is_dir():
                        continue
                    logging.debug('Found %s.', child)
                    index: str = item.name.split(' ')[-1]

                    # check if index in (n) format
                    if not index.startswith('(') or not index.endswith(')'):
                        child += ' (1)'
                        break

                    try:
                        index: int = int(index[1:-1])
                    except ValueError: # it was (n) but n is not int
                        child += ' (1)'
                        break

                    child = f'{child[:-4]} ({index + 1})'
                    break
                else:
                    stop = True
            if not scanned: # not scanned mean dir is empty.
                break
        del stop, scanned

        logging.info('Save as %s in %s.', child, parent.name)
        model.save_pretrained(str(parent / child))
        return str(parent / child)

    def download_model_from_huggingface(
            self,
            model_name: str,
            huggingface_path: str,
            hf_token: str = '',
            task: int = 0,
        ) -> None:
        """
        Download model directly from Hugging Face and save it in `models` folder.

        Args:
            model_name (str): The name of models. Used for select model and other config.
            huggingface_path (str): The path to download model.
            hf_token (str): The user Hugging Face access token.
            task (int): Model's task. Defined in `utils_ext.model_task`.
        """
        # if there is no task, return.
        if task == 0:
            return

        # Download model from huggingface path.

        # if user use 'https' path, convert to normal one.
        huggingface_path = huggingface_path.removeprefix('https://huggingface.co/')

        cur_task: str = self.utils_ext.model_task[task].lower().replace('_', ' ')
        logging.info('Download %s model from %s.',cur_task, huggingface_path)
        del cur_task

        match task:
            case 1: # For text generation.
                tokenizer_model = self._download_model(huggingface_path, AutoTokenizer, hf_token)
                text_generation_model = self\
                    ._download_model(huggingface_path, AutoModelForCausalLM, hf_token)

                # save downloaded model
                downloaded_path: str = os.path.join\
                    (self.utils_ext.model_path, 'Text_Generation', model_name)
                downloaded_path = self._save_model(text_generation_model, downloaded_path)
                self._save_model(tokenizer_model, os.path.join(downloaded_path, 'Tokenizer'))

            case 2: # For sentence transformer
                sentence_transformer_model = self\
                    ._download_model(huggingface_path, SentenceTransformer(), hf_token)

                # save downloaded model
                downloaded_path: str = os.path.join\
                    (self.utils_ext.model_path, 'Sentence_Transformer', model_name)
                self._save_model(sentence_transformer_model, downloaded_path)

            case 3: # For cross encoder
                cross_encoder_model = self._download_model\
                    (huggingface_path, 'CrossEncoder', hf_token) # CrossEncoder require input.

                # save downloaded model
                downloaded_path: str = os.path.join\
                    (self.utils_ext.model_path, 'Cross_Encoder', model_name)
                self._save_model(cross_encoder_model, downloaded_path)
