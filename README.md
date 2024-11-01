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

![LocalAssistant](asset/LocalAssistant.png)

This AI is designed to be used in CLI.

</div>

# Download by Pypi

Visit [Pypi](https://pypi.org/project/LocalAssistant) and follow the instuctrion.

<br>

# Download by source:

## Table of contents

1. [Installing](#installing)

2. [Preparing](#preparing)

3. [Running](#running)

4. [License](#license)

5. [Disclaimer](#disclaimer)

<br>

## Installing

1. Clone the repository.

```
git clone https://github.com/Linos1391/LocalAssistant.git
cd LocalAssistant
```

2. Visit [PyTorch](https://pytorch.org/) and download the version for your device.

3. Install the required python packages.

```
pip install -r requirements.txt
```

<br>

## Preparing 

### [UNIX](#unix) | [Window](#window)

### Unix

We are inside `./LocalAssistant/` directory.

```
echo $PWD
```

The path is your path to locas.cmd file (called as `<your_path>`). Remember to left it somewhere so you will not forget.

<br>

Change permission so we can access later:

```
chmod a+x locas.cmd
```

<br>

Next, we have to add this path to envirment variable. (with 2 steps)

1. Edit the .bash_profile file.

```
echo 'export LocalAssistant="<your_path>"
export PATH=$LocalAssistant:$PATH' >> ~/.bash_profile
```

2. After done, save the changed.

```
source ~/.bash_profile
```

<br>

Before doing anything, we should download a model first.

```
locas.cmd download -n Qwen Qwen/Qwen2.5-1.5B-Instruct 3
```

**Notice:** Due to using .cmd, Unix user have to type 'locas.cmd' instead of 'locas'.

### Window

We are inside `./LocalAssistant/` directory.

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

Then press `OK`.

5. On `System viables` tab, click `New` button.

![win_pre_5](asset/win_pre_5.png)

6. Type `LocalAssistant` on `Variable name`, then paste the path on `Variable value`

![win_pre_6](asset/win_pre_6.png)

Then press `OK`.

**Notice:** When done, click `OK` until out. Otherwise the path might not saved. Try have a look again for sure.

<br>

Before doing anything, we should download a model first.

```
locas download -n Qwen Qwen/Qwen2.5-1.5B-Instruct 3
```

<br>

## Running

#### If you're using Anaconde or Docker, modify [locas.cmd](locas.cmd) file.

### Unix

**Notice:** Due to using .cmd, Unix user have to type 'locas.cmd' instead of 'locas'.

```
locas.cmd ...
```

Use `locas.cmd -h` for more.

### Window

```
locas ...
```

Use `locas -h` for more.

<br>

## License

[GNU GPLv3](LICENSE)

<br>

## Disclaimer

This AI was designed to communicating with Hugging Face models in CLI. Please do not use this AI for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
