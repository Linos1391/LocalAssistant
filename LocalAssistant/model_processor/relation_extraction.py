"""Memory processing."""

import os
import logging

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig
from pyvis.network import Network

from ..utils import ConfigManager, LocalAssistantException

class RebelExtension:
    """
    Control users' memory.
    
    Source for learners like me and for me 10 years later: 
    https://medium.com/nlplanet/building-a-knowledge-base-from-texts-a-full-practical-example-8dbbffb912fa 
    """
    def __init__(self):
        self.config = ConfigManager()
        self.utils_ext = self.config.utils_ext

        self.entities, self.relations = [], []

        try:
            temp_path: str = os.path.join\
                (self.utils_ext.model_path, 'built-in', 'Rebel')
            self.model = AutoModelForSeq2SeqLM.from_pretrained(temp_path,device_map="auto",\
                local_files_only=True, length_penalty = 0.0, max_length = 256, min_length = 12,\
                    no_repeat_ngram_size = 0, num_beams = 4,)
            self.model_config = GenerationConfig(
                    length_penalty = 0.0,
                    max_length = 256,
                    min_length = 12,
                    no_repeat_ngram_size = 0,
                    num_beams = 4,
                )

            self.tokenizer = AutoTokenizer.from_pretrained\
                (os.path.join(temp_path, 'Tokenizer'), local_files_only=True, device_map="auto")
        except Exception as err:
            logging.error('Can not load model due to: %s', err)
            raise LocalAssistantException('Can not load model.') from err

    @staticmethod
    def _are_relations_equal(r1, r2):
        return all(r1[attr] == r2[attr] for attr in ("head", "type", "tail"))

    def _exists_relation(self, r1):
        return any(self._are_relations_equal(r1, r2) for r2 in self.relations)

    def _exist_entity(self, e1):
        return any(e1 == e2 for e2 in self.entities)

    def _add_relation(self, r):
        if not self._exists_relation(r):
            self.relations.append(r)
        for e in (r['head'], r['tail']):
            if not self._exist_entity(e):
                self.entities.append(e)

    @staticmethod
    def _extract_triplets(input_text: str):
        triplets = []
        subject, relation, object_ = '', '', ''
        input_text = input_text.strip()
        current = 'x'
        for token in input_text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
            if token == "<triplet>":
                current = 't'
                if relation != '':
                    triplets.append\
                        ({'head': subject.strip(),'type': relation.strip(),'tail': object_.strip()})
                    relation = ''
                subject = ''
            elif token == "<subj>":
                current = 's'
                if relation != '':
                    triplets.append\
                        ({'head': subject.strip(),'type': relation.strip(),'tail': object_.strip()})
                object_ = ''
            elif token == "<obj>":
                current = 'o'
                relation = ''
            else:
                if current == 't':
                    subject += ' ' + token
                elif current == 's':
                    object_ += ' ' + token
                elif current == 'o':
                    relation += ' ' + token
        if subject != '' and relation != '' and object_ != '':
            triplets.append({'head':subject.strip(),'type':relation.strip(),'tail':object_.strip()})
        return triplets

    def from_text_to_kb(self, input_text):
        """Extract text to nodes."""
        input_token = self.tokenizer\
            (input_text, max_length=512, padding=True, truncation=True, return_tensors='pt')

        # move token to device.
        input_token = {key: tensor.to(self.model.device)\
            for key, tensor in input_token.items()}

        # Generate
        generated_tokens = self.model.generate(
            **input_token,
            generation_config=self.model_config,
        )
        decoded_preds = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)

        # create kb
        for sentence_pred in decoded_preds:
            relations = self._extract_triplets(sentence_pred)
            for r in relations:
                self._add_relation(r)

    def save_kb(self, path: str):
        """save current kb to file."""
        logging.info('Save current knowledge base.')
        kb: dict = {
            "entities": self.entities,
            "relations": self.relations,
        }
        self.utils_ext.write_json_file(path, kb)

    def get_kb(self, path: str):
        """get current kb from file."""
        logging.info('Get current knowledge base.')
        try:
            kb: dict = self.utils_ext.read_json_file(path)
        except FileNotFoundError:
            kb: dict = {
                "entities": [],
                "relations": [],
            }
            self.utils_ext.write_json_file(path, kb)

        self.entities = kb['entities']
        self.relations = kb['relations']

    def save_network_html(self, path: str):
        """create network"""
        logging.info('Making network visual.')
        net = Network(directed=True, width="700px", height="700px", bgcolor="#eeeeee")

        # nodes
        color_entity = "#00FF00"
        for e in self.entities:
            net.add_node(e, shape="circle", color=color_entity)

        # edges
        for r in self.relations:
            net.add_edge(r["head"], r["tail"],
                        title=r["type"], label=r["type"])

        # save network
        net.repulsion(
            node_distance=200,
            central_gravity=0.2,
            spring_length=200,
            spring_strength=0.05,
            damping=0.09
        )
        net.set_edge_smooth('dynamic')
        net.show(path, notebook=False)
