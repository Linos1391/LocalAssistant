<div align="center">

# LocalAssistant

**Locas - your local assistant**

[![][locas-shield]][locas-url]
[![][python-shield]][python-url]
[![][conda-shield]][conda-url]
[![][transformers-shield]][transformers-url]

[locas-shield]: https://img.shields.io/badge/LocalAssisitant-0.1.0dev-red
[locas-url]: https://github.com/Linos1391/LocalAssistant
[python-shield]: https://img.shields.io/badge/Python-3.12+-yellow
[python-url]: https://www.python.org/downloads/
[conda-shield]: https://img.shields.io/badge/Anaconda-24.7+-grass
[conda-url]: https://www.anaconda.com/download
[transformers-shield]: https://img.shields.io/badge/Transformers-4.46+-orange
[transformers-url]: https://huggingface.co/docs/transformers/v4.46.0/index

![LocalAssistant](asset/LocalAssistant.png)

This AI is designed to be used in CLI.

</div>

## Table of contents

1. [Features](#features)

2. [Installing](#installing)

3. [Preparing](#preparing)

4. [Running](#running)

5. [License](#license)

6. [Disclaimer](#disclaimer)

<br>

## Features

<br>

## Installing

1. Clone the repository.

```
git clone https://github.com/Linos1391/LocalAssistant.git
cd LocalAssistant
```

2. Install the required python packages.

```
pip install -r requirements.txt
```

<br>

## Preparing

### OS: Unix

**Notice:** Due to using .cmd, Unix user have to type 'locas.cmd' instead of 'locas'.

Export that path and change permission:

```
export PATH=$PWD:$PATH
chmod a+x locas.cmd
```

Before doing anything, we should download a model first.

```
locas.cmd download -n Qwen Qwen/Qwen2.5-1.5B-Instruct 3
```

<br>

### OS: Window

We have in `./LocalAssistant/` directory.

```
echo %cd%
```

Copy the path below as its your path to locas.cmd file. Remember to left it somewhere so you will not forget.

<br>

Next, we have to add this path to envirment variable. (with 4 steps)

1. Press `Win` and search for `environment` until `edit the system environment variables` shown up. Open it.

![win_pre_1](asset/win_pre_1.png)

2. Click the `Environment Variables` button.

![win_pre_2](asset/win_pre_2.png)

3. Press on `Path` and click `Edit` button. 

![win_pre_3](asset/win_pre_3.png)

4. Click `New` and paste your path in.

![win_pre_4](asset/win_pre_4.png)

**Notice:** When done, click `OK` until out. Otherwise the path might not saved. Try have a look again for sure.

<br>

Before doing anything, we should download a model first.

```
locas download -n Qwen Qwen/Qwen2.5-1.5B-Instruct 3
```

<br>

## Running

### OS: Unix

```
locas.cmd ...
```

Use `locas.cmd -h` for more.

<br>

### OS: Window

```
locas ...
```

Use `locas -h` for more.

<br>

## License

[GNU GPLv3](LICENSE)

<br>

## Disclaimer

This AI was designed to communicating with Hugging Face models in CLI.
