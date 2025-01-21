<div align="center">

# LocalAssistant

**Locas - your local assistant**

[![][latest-release-shield]][latest-release-url]
[![][latest-commit-shield]][latest-commit-url]
[![][pypi-shield]][pypi-url]
[![][python-shield]][python-url]

[latest-release-shield]: https://badgen.net/github/release/Linos1391/LocalAssistant/development?icon=github
[latest-release-url]: https://github.com/Linos1391/LocalAssistant/releases/latest
[latest-commit-shield]: https://badgen.net/github/last-commit/Linos1391/LocalAssistant/main?icon=github
[latest-commit-url]: https://github.com/Linos1391/LocalAssistant/commits/main
[pypi-shield]: https://img.shields.io/badge/pypi-LocalAssistant-blue
[pypi-url]: https://pypi.org/project/LocalAssistant/
[python-shield]: https://img.shields.io/badge/python-3.10+-yellow
[python-url]: https://www.python.org/downloads/

![icon](https://github.com/Linos1391/LocalAssistant/blob/main/asset/icon.png?raw=true)

**Your CLI friend.**

</div>

<br>

```
>> locas -h

usage: locas [-h] [-v] [-V] COMMAND ...

LocalAssistant (locas) is an AI designed to be used in CLI.

options:
  -h, --help          show this help message and exit
  -v, --verbose       show debug messages (Can be used multiple times for higher level: CRITICAL[v] -> DEBUG[vvvv])
  -V, --version       show program's version number and exit

commands:
  built-in commands (type 'locas COMMAND -h' for better description)

  COMMAND
    download          Download models from Hugging Face
    config            Configurate LocalAssistant.
    user              Config user.
    chat              Chat with models for limited lines. (no history saved)
    start             Chat with models using history.
    self-destruction  LocalAssistant's self-destruction.
```

# Installing

Download [locas_installer.py](https://github.com/Linos1391/LocalAssistant/releases/download/v1.1.0rc1/locas_installer.py), and let magic happens.
```
python3 locas_installer.py
```

Let's try if it works:
```
locas.cmd -h
```

<br>

# Preparing

To chat, we will need model! You can download other models you want. Below is my recommend for first use (Like a starter pack.)

**For text generation:**
*(Choose other models from [here](https://huggingface.co/models?pipeline_tag=text-generation&library=safetensors&sort=trending).)*
```
locas.cmd download -n qwen Qwen/Qwen2.5-1.5B-Instruct 1
```

**For sentence transformer:**
*(Choose other models from [here](https://huggingface.co/sentence-transformers?sort_models=modified#models).)*
```
locas.cmd download -n minilm sentence-transformers/all-MiniLM-L6-v2 2
```

**For cross encoder:**
*(Choose other models from [here](https://huggingface.co/cross-encoder?sort_models=modified#models).)*
```
locas.cmd download -n msmarco cross-encoder/ms-marco-MiniLM-L-6-v2 3
```

<br>

# Running

By default, `locas` works at most of the time:

*(Unix user may try `locas.cmd ...` first. Window user can use both `locas` and `locas.cmd`)*
```
locas ...
```

Learn more about useful functions:
```
locas -h
```

To deactivate: *(It uses python's virtual environment)*
```
deactivate
```

<br>

# Removing

```
locas self-destruction
```

<br>

# License

[GNU GPLv3](LICENSE)

<br>

# Disclaimer

This AI was designed to communicating with Hugging Face models in CLI. Please do not use this AI for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
