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

![icon](asset/icon.png)

**Your CLI friend.**

<br>

![LocalAssistant](asset/LocalAssistant.png)

</div>

# Which one should I use?
- [Pypi version](#download-by-pypi-recommended) is great, it works how I want. But if you want projects to be organized by using Anaconda / Docker... It sucks.
- [Github version](#download-by-github) solves that by using PATH, then user may modify `locas.cmd` file to use Anaconda. However, Unix user have to type `locas.cmd` instead of `locas`.

**Summary:** Window user may use Github version while Pypi is for Unix user. I still recommended Pypi though.

<br>

# Download by Pypi: (Recommended)

Visit [Pypi](https://pypi.org/project/LocalAssistant) and follow the instuctrion.

<br>

# Download by GitHub:

## Installing

1. Clone the repository.

```
git clone https://github.com/Linos1391/LocalAssistant.git
cd LocalAssistant
```

2. Visit [PyTorch](https://pytorch.org/get-started/locally/) and download the version for your device.

```
# Example: (Me using WINDOW with CUDA 12.4)

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

3. Install the required python packages.

```
pip install -r requirements.txt
```

<br>

## Preparing 

<details>
  <summary><h3>Unix</h3></summary>

  ### Set up path:
  
  Go to your `LocalAssistant` directory (where `requirements.txt` is stored). 

  ```
  cd ...
  ```

  Then thing goes:

  ```
  chmod a+x locas.cmd
  echo 'export LocalAssistant=$PWD
  export PATH=$LocalAssistant:$PATH' >> ~/.bash_profile
  source ~/.bash_profile
  ```

  <br>

  ### Chatting:

  **Notice:** Due to using .cmd, Unix user have to type 'locas.cmd' instead of 'locas'.

  Before doing anything, we should download a model first.

  ```
  locas.cmd download -n qwen Qwen/Qwen2.5-1.5B-Instruct 1
  ```

  We will use `locas start` for AI's memory.

  
  ```
  locas.cmd start
  ```

  <br>

  ### Chatting with memory:

  **Notice:** Due to using .cmd, Unix user have to type 'locas.cmd' instead of 'locas'.

  Before doing anything, we should download a model first.

  ```
  locas.cmd download -n allmpnetv2 sentence-transformers/all-mpnet-base-v2 2
  ```

  Memory only allow on `locas start`, remember that. Anyway, let's dive into it!

  ```
  locas.cmd start -m
  ```

</details>

<details>
  <summary><h3>Window</h3></summary>

  ### Set up path:
  
  Open your Powershell. Go to your `LocalAssistant` directory (where `requirements.txt` is stored). 
    
  ```
  cd ...
  ```
    
  Then thing goes:

  ```
  $old_path = [Environment]::GetEnvironmentVariable('path', 'user');
  $new_path = $old_path + ';' + $PWD
  [Environment]::SetEnvironmentVariable('path', $new_path,'User');
  ```

  Then close your Powershell.

  <br>

  ### Chatting:

  Before doing anything, we should download a model first.

  ```
  locas download -n qwen Qwen/Qwen2.5-1.5B-Instruct 1
  ```

  We will use `locas start` for AI's memory.

  ```
  locas start
  ```

  <br>

  ### Chatting with memory:

  Before doing anything, we should download a model first.

  ```
  locas download -n allmpnetv2 sentence-transformers/all-mpnet-base-v2 2
  ```

  Memory only allow on `locas start`, remember that. Anyway, let's dive into it!

  ```
  locas start -m
  ```
  
</details>

<br>

## Running

#### If you're using Anaconde or Docker, modify [locas.cmd](locas.cmd) file.

<details>
  <summary><h3>Unix</h3></summary>
  
  **Notice:** Due to using .cmd, Unix user have to type 'locas.cmd' instead of 'locas'.

  ```
  locas.cmd ...
  ```

  Use `locas.cmd -h` for more.
    
</details>

<details>
  <summary><h3>Window</h3></summary>
  
  ```
  locas ...
  ```

  Use `locas -h` for more.
  
</details>

<br>

## Removing

**Warning:** This act will delete all LocalAssistant files.
```
locas self-destruction github
```

<br>

## License

[GNU GPLv3](LICENSE)

<br>

## Disclaimer

This AI was designed to communicating with Hugging Face models in CLI. Please do not use this AI for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
