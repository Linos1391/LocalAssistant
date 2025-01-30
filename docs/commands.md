## Download

This function made downloading model easier.

```
>> locas download -h

usage: locas download [-h] [-n NAME] [-t TOKEN] PATH TASK

Download models from Hugging Face

positional arguments:
  PATH                  Path of the Hugging Face's model
  TASK                  Model's task. Choose from:
                            - 'Text_Generation' (or '1'): Download text generation model.
                            - 'Sentence_Transformer' (or '2'): Download sentence transformer model.
                            - 'Cross_Encoder' (or '3'): Download cross encoder model.

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name of the model to be saved
  -t TOKEN, --token TOKEN
                        User Hugging Face's token (Some models might be restricted and need authenticated)
```

Example for this function is already shown at [Models](models.md).

## Config

This function focuses mainly on editing config file.

```
>> locas config -h

usage: locas config [-h] (-m | -s)

Configurate LocalAssistant.

options:
  -h, --help    show this help message and exit
  -m, --modify  Modify config value
  -s, --show    Show config data
```

### Show

Showing config data.

```
>> locas config -s

'hf_token': '',
'load_in_bits': '8',
'top_k_memory': '25',
'models': {
   'Text_Generation': '',
   'Sentence_Transformer': '',
   'Cross_Encoder': '',
},
'documents': {
   'top_k': '10',
   'allow_score': '0.6',
},
'users': 'default',
```

### Modify

Modifying config data. I am NOT recommend editing `locas_config.json` file manually.

```
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
    "allow_score": "0.6",
},
"users": "default"

Type KEY to modify KEY's VALUE. Type 'exit' to exit.

>> load_in_bits

'load_in_bits' is for 'quantization' method. If the VALUE is 8, then model is load in 8 bits (1 bytes) per parameters. Choose from: '4', '8', 'None'.

Modify VALUE of 'load_in_bits' to ... (Type 'exit' to exit.)

>> None
```

In short, user have to choose KEY first, then change the KEY's VALUE to the desire one. Remember to follow instruction carefully.

**Notice:** To configurate user, visit [User](#user).

| Group     | KEY                  | description |
| :-------: | -------------------- | ----------- |
| N/A       | hf_token             | 'hf_token' is your Hugging Face token. Some  models might be restricted and need authenticated. |
| N/A       | load_in_bits         | 'load_in_bits' is for 'quantization' method. If the VALUE is 8, then model is load in 8 bits (1 bytes) per parameters. |
| N/A       | top_k_memory         | 'top_k_memory' lets us know how much memory you want to recall. |
| models    | Text_Generation      | 'Text_Generation' stores default model for text generation. |
| models    | Sentence_Transformer | 'Sentence_Transformer' stores default model for sentence transformer. |
| models    | Cross_Encoder        | 'Cross_Encoder' stores default model for cross encoder. |
| documents | top_k                | 'top_k' lets us know how many lines you want to retrieve. Maximum is 50 lines.
| documents | allow_score          | 'allow_score' will make the retrieving process stop when similiarity score is lower. |

## User

This function is used for manipulating users' data.

```
>> locas user -h

usage: locas user [-h] [-c | -d | -r NAME] TARGET

Use this to configurate user.
    - To change change user. Type 'locas user TARGET'.
    - To do other stuff, use (-c|-d|-r NAME).
    - To show exist user. Type 'locas user show'.

positional arguments:
  TARGET                The target

options:
  -h, --help            show this help message and exit
  -c, --create          Create user with TARGET name
  -d, --delete          Delete user with TARGET name
  -r NAME, --rename NAME
                        Rename TARGET with NAME
```

### Show existed users

```
locas user show
```

### Change current user

Replace `<target>` with desire user's name. If that name is not available, raise error.

```
locas user <target>
```

### Create new user

Replace `<target>` with desire user's name. If that name is already taken, raise error.

```
locas user -c <target>
```

### Delete user

Replace `<target>` with desire user's name. If that name is not existed, raise error.

```
locas user -d <target>
```

### Rename user

Replace `<target>` with desire user's name, `NAME` with name that got changed to. If that name is not existed,is already taken, raise error.

```
locas user -r NAME <target>
```

## Chat

This function lets you chat with model for typed lines. Best used for fast chat.

```
>> locas chat -h

usage: locas chat [-h] [-t TOKEN] LINE

Chat with models for limited lines. Recommend for fast chat as non-user. (no history saved)

positional arguments:
  LINE                  Number of line to chat with

options:
  -h, --help            show this help message and exit
  -t TOKEN, --max-token TOKEN
                        Max tokens to generate
```

What to be concerned is LINE. Predict how much lines you need for the question, analyze the most straight forward query. I recommend above 10 lines, you can exit whenever you want anyway.

## Start

What made LocalAssistant a local assistant.

```
>> locas start -h

usage: locas start [-h] [-u USER] [-t TOKEN] [-tk TOP_K] [--retrieve-memory-only]

Chat with models using history.

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  The user name
  -t TOKEN, --max-token TOKEN
                        Max tokens to generate
  -tk TOP_K, --top-k-memory TOP_K
                        How much memory you want to recall.
  --retrieve-memory-only
                        Only retrieve and not saving the later memories.
```

### History

Before starting, LocalAssistant may ask you to make a new history or using an existed one. Let's have a look at what we can do.

```
-------------------------------------------
There is no history yet, please create one.
--------------------OR---------------------
Choose from:
    - ...
-------------------------------------------

Type 'create [name (Required, 1 WORD ONLY)] [system_prompt (Optional)]' to create new history.
Type 'delete [name (Required, 1 WORD ONLY)]' to delete history.
Type 'exit' to exit.
```

**Choose:** Continue an existed history.

Argument `<target>` must be in 'Choose from' section.

```
<target>
```

**Create:** Create a new history.

Argument `<target>` must not be in 'Choose from' section.

```
create <target>
```

You are also able to made your own system_prompt.

```
create <target> You are my Powershell terminal. When I type in commands, only reply with terminal's output, do not try to explain until I said so.
```

**delete:** Delete a history.

Argument `<target>` must be in 'Choose from' section.

```
delete <target>
```

### Memory

There are current two main memory tools.

| Function        | Usage |
| --------------- | ----- |
| Retrieve memory | Retrieve available entities. Then choosing one of them to retrieve relationships. |
| Save memory     | The assistant will paste in memory they found interested. Then the memory got analyzed by Rebel and returning relationships. |

**Notice:** If you want the model to save memory, just ask them so, remember to specific the memory for better result. Theoretically, model can automatically save memory, it is that they only save whenever they want, and that made sometimes memory saved so random.

## Docs

Document Query extension for LocalAssistant.

```
>> locas docs -h

usage: locas docs [-h] ACTION ...

Ask information from provided documents.

options:
  -h, --help  show this help message and exit

actions:
  Action to do with documents.

  ACTION
    upload    Upload files/folders to documents.
    extract   Relation extraction docs through query.
    chat      Ask queries from docs and get answer.
```

### Upload

Upload docs for asking later.

```
>> locas docs upload -h

usage: locas docs upload [-h] [-c] [--not-encode] PATH

Upload files/folders to documents.

positional arguments:
  PATH          Path to add.

options:
  -h, --help    show this help message and exit
  -c, --copy    Copy provided folders/files to docs.
  --not-encode  Do not encode after upload. (if user want to upload multiple docs)
```

By default, this function will add path as shared path, meaning if original path got edited, added path is then useless. Therefore, I made `copy` ability, the item go with added path is copied to our folder, hence better configurating later.

**Notice:** Archived files are available only when copying.

### Extract

Extract relations from docs.

```
>> locas docs extract -h

usage: locas docs extract [-h] [-tk TOP_K] [-s SCORE]

Relation extraction docs through query.

options:
  -h, --help            show this help message and exit
  -tk TOP_K, --top-k TOP_K
                        How many sentences you want to retrieve.
  -s SCORE, --allow-score SCORE
                        Retrieving process will stop when similiarity score is lower.
```

After Rebel was added, docs data is now able to use relation extraction. There must be at lease a doc to work.

### Chat

Chat with model, find information from docs, and so on.

```
>> locas docs chat -h

usage: locas docs chat [-h] [-t TOKEN] [-tk TOP_K] [-s SCORE] [--encode-at-start] [--show-retrieve]

Ask queries from docs and get answer.

options:
  -h, --help            show this help message and exit
  -t TOKEN, --max-token TOKEN
                        Max tokens to generate
  -tk TOP_K, --top-k TOP_K
                        How many sentences you want to retrieve.
  -s SCORE, --allow-score SCORE
                        Retrieving process will stop when similiarity score is lower.
  --encode-at-start     Encode docs before chating.
  --show-retrieve       Show the retrieved data from docs.
```

The only thing you need to know is `--show-retrieve`. Use it if you want to know where information came from, which file contained, or what the sentence said.

## Self Destruction

Everything needs a self-destruction!

```
>> locas self-destruction -h

usage: locas self-destruction [-h] [-a]

LocalAssistant's self-destruction.

options:
  -h, --help  show this help message and exit
  -a, --all   Delete the whole folder (included models, history, etc).
```

ONLY use when you install by provided methods in [Installation](installation.md). If you `pip install` or `git clone` earlier, never use it for your own goods.
