"""Used for retrive information from documents."""

import os
import logging
import pathlib
import shutil
import re
from itertools import chain

import pymupdf
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder, util

from ..utils import ConfigManager, LocalAssistantException

class DocsQuestionAnswerExtension:
    """Extension used to process document."""
    def __init__(self, sentence_transformers_name: str, cross_encoder_name: str):
        self.config = ConfigManager()
        self.utils_ext = self.config.utils_ext

        try:
            temp_path: str = os.path.join\
                (self.utils_ext.model_path, 'Sentence_Transformer', sentence_transformers_name)
            self.sentence_transformers = SentenceTransformer(temp_path, local_files_only=True)

            temp_path: str = os.path.join\
                (self.utils_ext.model_path, 'Cross_Encoder', cross_encoder_name)
            self.cross_encoder = CrossEncoder(temp_path, local_files_only=True)
        except Exception as err:
            logging.error('Can not load model due to: %s', err)
            raise LocalAssistantException('Can not load model.') from err

    @staticmethod
    def _split_into_sentences(text: str) -> list[str]:
        """
        Split the text into sentences.

        If the text contains substrings "<prd>" or "<stop>", they would lead 
        to incorrect splitting because they are used as markers for splitting.
        
        Source: https://stackoverflow.com/questions/4576077/how-can-i-split-a-text-into-sentences
        """
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = r"(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s\
|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov|edu|me)"
        digits = "([0-9])"
        multiple_dots = r'\.{2,}'

        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        text = re.sub(f"{digits}[.]{digits}","\\1<prd>\\2",text)
        text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
        if "Ph.D" in text:
            text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub(fr"\s{alphabets}[.] "," \\1<prd> ",text)
        text = re.sub(f"{acronyms} {starters}","\\1<stop> \\2",text)
        text = re.sub(f"{alphabets}[.]{alphabets}[.]{alphabets}[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(f"{alphabets}[.]{alphabets}[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(f" {suffixes}[.] {starters}"," \\1<stop> \\2",text)
        text = re.sub(f" {suffixes}[.]"," \\1<prd>",text)
        text = re.sub(f" {alphabets}[.]"," \\1<prd>",text)
        if "”" in text:
            text = text.replace(".”","”.")
        if "\"" in text:
            text = text.replace(".\"","\".")
        if "!" in text:
            text = text.replace("!\"","\"!")
        if "?" in text:
            text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        if sentences and not sentences[-1]:
            sentences = sentences[:-1]
        return sentences

    def _get_file(self, path: str) -> list:
        """To get file, for `_get_docs()`."""
        path: pathlib.Path = pathlib.Path(path)

        result: list = []
        if not path.is_dir():
            return [path]
        for item in os.scandir(path):
            result += self._get_file(item.path)
        return result

    def _get_docs(self) -> tuple:
        """
        Get all documents that currently exist.

        Returns:
            tuple: list of exist docs (if is dir, go inside).
        """
        result: list = []

        logging.debug("Get path from 'share_path.json'.")
        try: # get all path that doesn't get copy.
            data: list = self.utils_ext.read_json_file\
                (os.path.join(self.utils_ext.docs_path, 'share_path.json'))
            for path in data:
                if pathlib.Path(path).exists():
                    result += self._get_file(path)
        except FileNotFoundError:
            pass

        logging.debug("Get path from copied documents.")
        # get those copied.
        for item in os.scandir(self.utils_ext.docs_path):
            if item.name in ('share_path.json', 'docs_data.json', 'encoded_docs_data.pt'):
                continue
            result += self._get_file(item.path)
        return tuple(result)

    def _make_name(self, name: str, file_type: str = '') -> str:
        """Make a valid name."""
        stop: bool = False
        scanned: bool = False
        while not stop:
            for item in os.scandir(self.utils_ext.docs_path):
                scanned = True

                if item.name == str(f'{name}.{file_type}' if file_type else name):
                    logging.debug('Found %s.%s.', name, file_type)
                    index: str = item.name.split('.', maxsplit=1)[0].split(' ')[-1]

                    # check if index in (n) format
                    if not index.startswith('(') or not index.endswith(')'):
                        name += ' (1)'
                        break

                    try:
                        index: int = int(index[1:-1])
                    except ValueError: # it was (n) but n is not int
                        name += ' (1)'
                        break

                    name = f'{name[:-4]} ({index + 1})'
                    break
                else:
                    stop = True
            if not scanned: # not scanned mean dir is empty.
                break
        return f'{name}.{file_type}' if file_type else name

    def upload_docs(self, path: str, copy: bool = False, not_encode: bool = False) -> None:
        """
        Upload documents for LocalAssistant to use.

        Args:
            path (str): used to locate documents' path.
            copy (bool, optional): Whether to copy file/folder. Defaults to False.
            not_encode (bool, optional): not to encode. Defaults to False.

        Raises:
            LocalAssistantException: not a valid path.
        """
        print("Loading datasets. Please be patient, it may take some minutes.")

        path: pathlib.Path = pathlib.Path(path)
        if not path.exists():
            logging.error("'%s' is not a valid path.", path)
            raise LocalAssistantException(f"'{path}' is not a valid path.")

        try:
            os.makedirs(self.utils_ext.docs_path)
        except FileExistsError:
            pass

        if not copy: # we only need path.
            logging.debug("Put path in 'share_path.json' file.")
            try:
                total_path = self.utils_ext.read_json_file\
                    (os.path.join(self.utils_ext.docs_path, 'share_path.json'))
            except FileNotFoundError:
                total_path: list = []
            total_path.append(str(path))
            self.utils_ext.write_json_file\
                (os.path.join(self.utils_ext.docs_path, 'share_path.json'), total_path)
            self.encode()
            return

        # copy them to `documents` folder.
        logging.debug("Copy data to documents.")
        file_name = self._make_name(*path.name.split('.', maxsplit=1))

        # with dir
        if path.is_dir():
            shutil.copytree\
                (path, os.path.join(self.utils_ext.docs_path, file_name))
        # with archived file.
        elif path.name.endswith(tuple(chain(*(f[1] for f in shutil.get_unpack_formats())))):
            shutil.unpack_archive\
                (path, os.path.join(self.utils_ext.docs_path, file_name.split('.', maxsplit=1)[0]))
        # with other file types.
        else:
            shutil.copyfile\
                (path, os.path.join(self.utils_ext.docs_path, file_name))

        if not not_encode:
            self.encode()

    def encode(self) -> None:
        """Encode documents."""
        self.config.get_config_file()

        logging.info('Get existed docs.')
        docs: tuple = self._get_docs()

        # save memory to json file.
        logging.debug("Transfer data to .json")
        data_to_json: dict = {}
        index: int = -1
        data: list = []

        for doc in docs:
            if str(doc).lower().endswith\
                    (('.pdf','.xps', '.epub', '.mobi', '.fb2', '.cbz', '.svg', '.txt')):
                pdf_file = pymupdf.open(doc)
                docs_data = '\n'.join([page.get_text() for page in pdf_file])
            else:
                try:
                    file = open(doc, mode="r", encoding="utf-8")
                    docs_data = file.read()
                    file.close()
                except UnicodeDecodeError:
                    file.close()
                    logging.error("Can not read file '%s'", pathlib.Path(doc).name)

                    # delete on json file.
                    try:
                        share_path: list = self.utils_ext.read_json_file\
                            (os.path.join(self.utils_ext.docs_path, 'share_path.json'))
                    except FileNotFoundError:
                        pass
                    else:
                        if str(doc) in share_path:
                            share_path.remove(str(doc))
                            self.utils_ext.write_json_file(os.path.join\
                                (self.utils_ext.docs_path, 'share_path.json'), share_path)
                            continue

                    # delete on copied path.
                    for item in os.scandir(self.utils_ext.docs_path):
                        if str(doc) == str(item.path):
                            if item.is_dir():
                                shutil.rmtree(item.path)
                            else:
                                os.remove(item.path)
                            continue

            # add data to json.
            for sentence in self._split_into_sentences(docs_data):
                if sentence in data: # prevent repetiton.
                    continue

                index += 1
                data.append(sentence)

                data_to_json.update({
                    index: {
                        "title": pathlib.Path(doc).name,
                        "content": sentence,
                    }
                })

        temp_path = os.path.join(self.utils_ext.docs_path, 'docs_data.json')
        self.utils_ext.write_json_file(temp_path, data_to_json)

        # encode
        encoded_data = self.sentence_transformers\
            .encode(data, convert_to_tensor=True, show_progress_bar=True)

        temp_path = os.path.join(self.utils_ext.docs_path, 'encoded_docs_data.pt')
        torch.save(encoded_data, temp_path)

    def ask_query(self, question: str, top_k: int = 0, allow_score: float = 0.0) -> list[str]:
        """Ask query function."""
        self.config.get_config_file()

        if top_k == 0: # user didnt add top k when chat.
            top_k = int(self.config.data["documents"]["top_k"])
        if allow_score == 0.0:
            allow_score = float(self.config.data["documents"]["allow_score"])

        temp_path: str = os.path.join(self.utils_ext.docs_path, 'encoded_docs_data.pt')
        logging.info('Loading docs from encoded data.')
        try:
            encoded_data = torch.load(temp_path, weights_only=True)
        except FileNotFoundError:
            logging.info('Encoded data not found. Encode new data.')
            self.encode()
            encoded_data = torch.load(temp_path, weights_only=True)

        # encode query.
        encoded_question = self.sentence_transformers.encode(question, convert_to_tensor=True)

        scores = util.dot_score(encoded_question, encoded_data)[0].tolist()
        hits = list(zip(range(len(scores)), scores))
        hits = sorted(hits, key=lambda x: x[1], reverse=True)

        # get json file.
        logging.debug('Get json file.')
        temp_path = os.path.join(self.utils_ext.docs_path, 'docs_data.json')
        data = self.utils_ext.read_json_file(temp_path)

        # Retrieve data using sentence transformers.
        retrieve_data: list = []
        for hit_data, hit_score in hits[:200]: # maximum 200 lines.
            if hit_score < allow_score:
                break
            retrieve_data.append((question, data[str(hit_data)]['content']))

        # Re-rank using cross encoder.
        scores = self.cross_encoder.predict(retrieve_data)

        hits = list(zip(hits, scores))
        hits = sorted(hits, key=lambda x: x[1], reverse=True)

        # Compile results.
        result: list = []
        for (hit_data, _), _ in hits[:top_k]:
            pointer: dict = data[str(hit_data)]
            result.append(pointer)
            logging.debug("Retrieve '%s' from '%s'.", pointer["content"], pointer["title"])

        return result
