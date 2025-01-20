"""Parser, define when goes `locas -h`."""

import argparse

PARSER = argparse.ArgumentParser(
    prog='locas',
    description='LocalAssistant (locas) is an AI designed to be used in CLI.',
)

# verbose.
PARSER.add_argument('-v', '--verbose', action='count', help='show debug \
messages (Can be used multiple times for higher level: CRITICAL[v] -> DEBUG[vvvv])', default=0)

# version.
PARSER.add_argument('-V', '--version', action='version', version='LocalAssistant 1.1.0')

subparser = PARSER.add_subparsers(
    title='commands',
    description="built-in commands (type 'locas COMMAND -h' for better description).",
    metavar='COMMAND',
    dest='COMMAND',
)

# +--------------------+
# | locas download ... |
# +--------------------+

subparser_download = subparser.add_parser(
    name='download',
    help='Download models from Hugging Face',
    description='Download models from Hugging Face',
    formatter_class=argparse.RawTextHelpFormatter,
)

subparser_download.add_argument('PATH', action='store', help='Path of the Hugging Face\'s model')

TEMP_STRING: str = """\
Model\'s task. Choose from:
    - 'Text_Generation' (or '1'): Download text generation model.
    - 'Sentence_Transformer' (or '2'): Download sentence transformer model.
    - 'Cross_Encoder' (or '3'): Download cross encoder model.
"""
subparser_download.add_argument('TASK', action='store', help=TEMP_STRING, default=0)
del TEMP_STRING

subparser_download.add_argument('-n', '--name', action='store',\
    help='Name of the model to be saved', default='Untitled')

subparser_download.add_argument('-t', '--token', action='store', help='User Hugging \
Face\'s token (Some models might be restricted and need authenticated)', default='')

# +------------------+
# | locas config ... |
# +------------------+

TEMP_STRING: str = """\
Configurate LocalAssistant.
 
----------------------------Example-----------------------------------
>> locas config -m

"hf_token": "",
"load_in_bits": "8",
"top_k_memory": "5",
"models": {
    "Text_Generation": "",
    "Sentence_Transformer": "",
    "Cross_Encoder": "",
},
"documents": {
    "top_k": "10",
    "allow_score": "0.8",
},
"users": "default"

Type KEY to modify KEY's VALUE. Type 'exit' to exit.

>> load_in_bits

'load_in_bits' is for 'quantization' method. If the VALUE is 8, then model is load in 8 bits (1 bytes) per parameters. Choose from: '4', '8', 'None'.

Modify VALUE of 'load_in_bits' to ... (Type 'exit' to exit.)

>> None
----------------------------------------------------------------------

"""
subparser_config = subparser.add_parser(
    name='config',
    help='Configurate LocalAssistant.',
    description=TEMP_STRING,
    formatter_class=argparse.RawTextHelpFormatter,
)
del TEMP_STRING

subparser_config_group = subparser_config.add_mutually_exclusive_group(required=True)

subparser_config_group.add_argument('-m', '--modify', action='store_true',\
    help='Modify config value')

subparser_config_group.add_argument('-s', '--show', action='store_true', help='Show config data')

# +----------------+
# | locas user ... |
# +----------------+

TEMP_STRING: str = """\
Use this to configurate user.
    - To change change user. Type 'locas user TARGET'.
    - To do other stuff, use (-c|-d|-r NAME).
    - To show exist user. Type 'locas user show'.
"""
subparser_user = subparser.add_parser(
    name='user',
    help='Config user.',
    description=TEMP_STRING,
    formatter_class=argparse.RawDescriptionHelpFormatter
)
del TEMP_STRING

subparser_user.add_argument('TARGET', action='store', help='The target')

subparser_user_group = subparser_user.add_mutually_exclusive_group()

subparser_user_group.add_argument('-c', '--create', action='store_true',\
    help='Create user with TARGET name')

subparser_user_group.add_argument('-d', '--delete', action='store_true',\
    help='Delete user with TARGET name')

subparser_user_group.add_argument('-r', '--rename', action='store', metavar='NAME',\
    help='Rename TARGET with NAME')

# +----------------+
# | locas chat ... |
# +----------------+

subparser_chat = subparser.add_parser(
    name='chat',
    help='Chat with models for limited lines. (no history saved)',
    description='Chat with models for limited lines. \
Recommend for fast chat as non-user. (no history saved)',
)

subparser_chat.add_argument('LINE', action='store', type=int, help='Number of line to chat with')

subparser_chat.add_argument('-tgm', '--text-generation', metavar='MODEL', action='store',\
    help='Use downloaded text generation model', default='')

subparser_chat.add_argument('-t', '--max-token', metavar='TOKEN', action='store', type=int,\
    help='Max tokens to generate', default= 500)

# +-----------------+
# | locas start ... |
# +-----------------+

subparser_start = subparser.add_parser(
    name='start',
    help='Chat with models using history.',
    description='Chat with models using history.',
)

subparser_start.add_argument('-u', '--user', action='store',\
    help='The user name', default='default')

subparser_start.add_argument('-tgm', '--text-generation', metavar='MODEL', action='store',\
    help='Use downloaded text generation model', default='')

subparser_start.add_argument('-t', '--max-token', metavar='TOKEN', action='store', type=int,\
    help='Max tokens to generate', default= 500)

subparser_start.add_argument('-m', '--memory-enable', action='store_true',\
    help='Enable memory function')

subparser_start.add_argument('-stm', '--sentence-transformer', metavar='MODEL', action='store',\
    help='Use downloaded sentence transformer model. (When memory enabled)', default='')

subparser_start.add_argument('-tk', '--top-k-memory', metavar='TOP_K', action='store', type=int,\
    help='How much memory you want to recall. (When memory enabled)', default= 0)

subparser_start.add_argument('--encode-at-start', action='store_true',\
    help='Encode memory before chating. (When memory enabled)')

# +----------------+
# | locas docs ... |
# +----------------+

subparser_docs = subparser.add_parser(
    name='docs',
    help='Ask information from provided documents.',
    description='Ask information from provided documents.',
)

subparser_docs = subparser_docs.add_subparsers(
    title='actions',
    description='Action to do with documents.',
    metavar='ACTION',
    dest='ACTION',
)

subparser_docs_upload = subparser_docs.add_parser(
    name='upload',
    help='Upload files/folders to documents.',
    description='Upload files/folders to documents.',
)

subparser_docs_upload.add_argument('PATH', action='store', help='Path to add.')

subparser_docs_upload.add_argument('-c', '--copy', action='store_true',\
    help='Copy provided folders/files to docs.')

subparser_docs_upload.add_argument('--not-encode', action='store_true',\
    help='Do not encode after upload. (if user want to upload multiple docs)')

subparser_docs_chat = subparser_docs.add_parser(
    name='chat',
    help='Ask queries from docs and get answer.',
    description='Ask queries from docs and get answer.'
)

subparser_docs_chat.add_argument('-tgm', '--text-generation', metavar='MODEL', action='store',\
    help='Use downloaded text generation model', default='')

subparser_docs_chat.add_argument('-t', '--max-token', metavar='TOKEN', action='store', type=int,\
    help='Max tokens to generate', default= 500)

subparser_docs_chat.add_argument('-stm', '--sentence-transformer',metavar='MODEL',action='store',\
    help='Use downloaded sentence transformer model.', default='')

subparser_docs_chat.add_argument('-cem', '--cross-encoder',metavar='MODEL',action='store',\
    help='Use downloaded cross encoder model.', default='')

subparser_docs_chat.add_argument('-tk', '--top-k', metavar='TOP_K', action='store', type=int,\
    help='How many sentences you want to retrieve.', default= 0)

subparser_docs_chat.add_argument('-s', '--allow-score',metavar='SCORE',action='store',type=float,\
    help='Retrieving process will stop when similiarity score is lower.', default= 0.0)

subparser_docs_chat.add_argument('--encode-at-start', action='store_true',\
    help='Encode docs before chating.')

subparser_docs_chat.add_argument('--show-retrieve', action='store_true',\
    help='Show the retrieved data from docs.')

# +----------------------------+
# | locas self-destruction ... |
# +----------------------------+

subparser_self_destruction = subparser.add_parser(
    name='self-destruction',
    help='LocalAssistant\'s self-destruction.',
    description='LocalAssistant\'s self-destruction.',
)

subparser_self_destruction.add_argument('-a', '--all', action='store_true',\
    help='Delete the whole folder (included models, history, etc).')
