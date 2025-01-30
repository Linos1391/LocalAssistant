## Downloading Model

First, we may start by install all required models. It will take lots of time, so paste the code below in and go somewhere or grab some coffee during the process.

```
locas.cmd download -n qwen Qwen/Qwen2.5-1.5B-Instruct 1
locas download -n minilm sentence-transformers/all-MiniLM-L6-v2 2
locas download -n msmarco cross-encoder/ms-marco-MiniLM-L-6-v2 3
```

You can choose other models if felt bother. [Learn more](models.md).

## Know The Difference: `locas` vs `locas.cmd`

Confuse why I use `locas.cmd` at the first line instead of `locas` like the others?

LocalAssistant uses Python's virtual environment, that means `locas` can be called within the environment. But no one will find the folder, activate the venv, call `locas`. It takes up to 3 steps!

Therefore, I made `locas.cmd` file with device's PATH connect to LocalAssistant folder. By this way, you can call `locas.cmd` anywhere in current terminal. *(Do not try on WSL and ask me why error shows.)*

**Notice:** Windows user can use `locas` in any cases. But `locas.cmd` is a must for Unix.

## Chating With Limited Lines

Really straight forward, just chatting and nothing else. Can be used for quick chat. Chat history will NOT be saved during this process.

```
locas.cmd chat 5
```

Now, you can communicate with the assistant for 5 lines. But hold tight, nothing has been shown yet.

## Real Chat

Here, memory and history will be saved. Different users can be created for each need.

```
locas.cmd start
```

Use `exit` to exit. After chatting, a memory graph will shown up. If wonder why no memory is saved, try ask the model so!

## Document Query

First, let's upload a document. The path can point to both path or file (archive file is only available when copying)

```
locas.cmd docs upload <path_to_docs>
```

After done encoding. We now can ask question related to added documents.

```
locas.cmd docs chat
```

## Deactivate

Those above are the main functions. Now let's deactivate LocalAssistant:

```
deactivate
```
