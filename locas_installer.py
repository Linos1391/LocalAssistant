"""User friendly LocalAssistant automatic installer."""

import os
import pathlib
import sys
import venv
import subprocess
import shutil

print('Welcome to LocalAssistant automatic installer.')

assert sys.version_info.major >= 3 and sys.version_info.minor >= 10,\
    f'Python version is expected to be above 3.10, but got {sys.version.split()[0]} instead.'

while True:
    PATH: str = input(f'\nPlease choose the path for LocalAssistant [{os.getcwd()}]: ')
    if PATH == '':
        PATH = os.getcwd()
        break

    PATH: pathlib.Path = pathlib.Path(PATH)
    if PATH.exists():
        if not PATH.is_dir():
            print(f"'{PATH}' is not a folder. Please try again.")
            continue
        if input(f"'{PATH}' is already existed, are you sure this is the correct path? (y/[n]): ")\
                .lower() != 'y':
            continue
    else:
        os.makedirs(PATH)
    break
print(f"Using '{PATH}'.")

def _choose_pytorch(compute_platform: dict) -> str:
    """For user to choose with devide they want."""
    print('\nChoose your PyTorch compute from these:')
    for device in compute_platform.keys():
        print(f'  - {device}')

    while True:
        chosen_device = input('Select one [cpu]: ')
        if not chosen_device:
            chosen_device = 'cpu'
        if chosen_device in tuple(compute_platform.keys()):
            print(f'Using {chosen_device}.\n')
            return compute_platform[chosen_device]
        print(f'Invalid compute: {chosen_device}.\n')

# Making appropriate command for right version.
if sys.platform == 'win32': # Window
    PYTHON: str = 'python'
    COMMAND: str = '.venv\\Scripts\\activate'
    SEP: str = '&&'

    compute_dict: dict = {
        "cuda 11.8": "pip3 install \
            torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        "cuda 12.1": "pip3 install \
            torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
        "cuda 12.4": "pip3 install \
            torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124",
        "cpu": "pip3 install torch torchvision torchaudio",
    }
    PYTORCH: str = _choose_pytorch(compute_dict)
else:
    PYTHON: str = 'python3'
    COMMAND: str = 'source .venv/bin/activate'
    SEP: str = ';'

    if sys.platform == 'darwin': # MacOS
        print('MacOS only has cpu compute.\n')
        PYTORCH: str = 'pip3 install torch torchvision torchaudio'
    else: # Linux
        compute_dict: dict = {
            "cuda 11.8": "pip3 install \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
            "cuda 12.1": "pip3 install \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
            "cuda 12.4": "pip3 install torch torchvision torchaudio",
            "rocm": "pip3 install \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2",
            "cpu": "pip3 install t\
                orch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        }
        PYTORCH: str = _choose_pytorch(compute_dict)

os.chdir(PATH)
venv.create('.venv', with_pip=True, prompt='LocalAssistant')

# update pip
subprocess.run(f'{PYTHON} -m pip install --upgrade pip',\
    check=False, shell=True, stdout=subprocess.PIPE)

# Choose version to install.
call_version: list = subprocess.run('pip index versions LocalAssistant --pre',
                              check=False,
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True).stdout.split()
try:
    call_version =  call_version[:call_version.index('LATEST:')]
except ValueError:
    pass

try:
    install_index: int = call_version.index('INSTALLED:')
    install_version: str = call_version[install_index + 1]
    print(f'Detected installed LocalAssistant v{install_version}.')
except ValueError:
    install_index: int = len(call_version)

pre_version: str = ''
latest_version: str = ''

version_list: list = call_version[(call_version.index('versions:')+1):install_index]
print(f'Available version: {" ".join(version_list)}')
for version in version_list:
    if pre_version and latest_version:
        break
    if 'rc' in version:
        pre_version = version.replace(',','')
    else:
        latest_version = version.replace(',','')

print(f'  Pre-release version: {pre_version}\n  Latest version: {latest_version}')
desire_version: str = ''
while True:
    desire_version = input(f'Which version to install [{latest_version}]: ')
    if not desire_version:
        desire_version = latest_version
    if f'{desire_version},' in version_list:
        print(f'Installing LocalAssistant v{desire_version}.')
        break
    print(f'Invalid version: {desire_version}.')

# Installing dependences.
print('\nInstalling dependences:')

os.system(SEP.join([COMMAND,PYTORCH,f'pip3 install LocalAssistant=={desire_version} --upgrade']))

print('Setting up path.')

content: str = f"""\
:; if [ -z 0 ]; then
  @echo off
  goto :WINDOWS
fi
#UNIX

source "{'/'.join(str(PATH).split('\\'))}/.venv/bin/activate" ; locas $@

exit 0

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

:WINDOWS

"{PATH}\\.venv\\Scripts\\activate" && locas %*
"""
with open('locas.cmd', mode="w", encoding="utf-8") as write_file:
    write_file.write(content)
    write_file.close()

if not shutil.which('locas.cmd'): # haven't set path yet.
    if sys.platform == 'win32':
        os.system(f"powershell $old_path = [Environment]::GetEnvironmentVariable('path', 'user');\
                               $new_path = $old_path + ';' + '{PATH}';\
                               [Environment]::SetEnvironmentVariable('path', $new_path,'User');")
    else:
        os.system(f"chmod a+x locas.cmd;\
                    echo 'export LocalAssistant='{PATH}';\
                          export PATH=$LocalAssistant:$PATH' >> ~/.bash_profile;\
                    source ~/.bash_profile")
