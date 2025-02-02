## Installing

Download [locas_installer.py](https://github.com/Linos1391/LocalAssistant/releases/download/v1.1.1/locas_installer.py), and let magic happens.

|          Window          |             Unix           |
| ------------------------ | ---------------------------|
|python locas_installer.py | python3 locas_installer.py |

Let's go through all questions!

### Question 1: Choose path
```
Please choose the path for LocalAssistant. [...]:
```

Now, path is where you want LocalAssistant to be.
```
Your path
│
├───.venv <dir - a python virtual environment>
│
├───documents <dir - to store docs used for `locas docs ...`>
│
├───models <dir - where installed models is stored>
│
├───users <dir - where users' data is stored>
│
└───locas.cmd <file - script to use `locas.cmd` anywhere>
```


Choose the folder, copy its path *(`Ctrl+Shift+C` for Window)*, and paste it in. If leaving it empty, the path will be that inside the bracket `[...]`.

**Notice:** It may ask for comfirmation when folder is already existed.

### Question 2: Choose Pytorch compute

```
Choose your PyTorch compute from these:
  - ...
Select one [cpu]:
```

**Notice:** MacOS will be skipped. *(Only cpu is supported)*

What shown below is your device compute. Copy that compute name to the answer and you are done. Leave it empty for using cpu. Remember to choose the RIGHT compute, `Cuda 12.4` is not with `Cuda 12.6`.

### Question 3: Choose version

```
Available version: ...
  Pre-release version: ...
  Latest version: ...
Which version to install [...]:
```

All version that got published will be shown. Choose the one that fill your need. Leave empty for the latest version.

## Updating

What you need is installing LocalAssistant again on the path where needed to be upgraded *(Question 1)*. Your existed assets won't be touched during this process.
