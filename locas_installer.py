"""User friendly LocalAssistant automatic installer."""

import os
import pathlib
import sys
import venv
import subprocess
import shutil

def choose_path() -> str:
    """To choose the path. Use the same path to upgrade."""
    while True:
        path: str = input(f'\nPlease choose the path for LocalAssistant. [{os.getcwd()}]: ')
        if path == '':
            path = os.getcwd()
            break

        path: pathlib.Path = pathlib.Path(path)
        if path.exists():
            if not path.is_dir():
                print(f"'{path}' is not a folder. Please try again.")
                continue
            if input(f"'{path}' is an existed folder, are you sure to use path? \
(If you are updating LocalAssistant, go ahead!) (y/[n]): ").lower() != 'y':
                continue
        else:
            os.makedirs(path)
        break
    print(f"Using '{path}'.")
    return path

def _choose_pytorch_compute(compute_platform: dict) -> str:
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

def choose_command() -> tuple[str]:
    """Making appropriate command for right version."""
    if sys.platform == 'win32': # Window
        python: str = 'python'
        command: str = '.venv\\Scripts\\activate'
        sep: str = '&&'

        compute_dict: dict = {
            "cuda 11.8": "pip3 install \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
            "cuda 12.1": "pip3 install \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
            "cuda 12.4": "pip3 install \
                torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124",
            "cpu": "pip3 install torch torchvision torchaudio",
        }
        pytorch: str = _choose_pytorch_compute(compute_dict)
    else:
        python: str = 'python3'
        command: str = 'source .venv/bin/activate'
        sep: str = ';'

        if sys.platform == 'darwin': # MacOS
            print('MacOS only has cpu compute.\n')
            pytorch: str = 'pip3 install torch torchvision torchaudio'
        else: # Linux
            compute_dict: dict = {
                "cuda 11.8": "pip3 install torch torchvision torchaudio \
                    --index-url https://download.pytorch.org/whl/cu118",
                "cuda 12.1": "pip3 install torch torchvision torchaudio \
                    --index-url https://download.pytorch.org/whl/cu121",
                "cuda 12.4": "pip3 install torch torchvision torchaudio",
                "rocm": "pip3 install torch torchvision torchaudio \
                    --index-url https://download.pytorch.org/whl/rocm6.2",
                "cpu": "pip3 install torch torchvision torchaudio \
                    --index-url https://download.pytorch.org/whl/cpu",
            }
            pytorch: str = _choose_pytorch_compute(compute_dict)
    return (python, command, sep, pytorch)

def choose_version() -> str:
    """Choose version to install."""
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
    return desire_version

def setup_path(env_path: str):
    """So that locas can be called everywhere."""
    print('\nSetting up path.')

    content: str = f"""\
:; if [ -z 0 ]; then
  @echo off
  goto :WINDOWS
fi

#UNIX
source "{'/'.join(str(env_path).split('\\'))}/.venv/bin/activate" ; locas $@
exit 0
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
:WINDOWS
"{env_path}\\.venv\\Scripts\\activate" && locas %*
"""
    with open('locas.cmd', mode="w", encoding="utf-8") as write_file:
        write_file.write(content)
        write_file.close()

    if not shutil.which('locas.cmd'): # haven't set path yet.
        if sys.platform == 'win32':
            os.system(f"powershell $old_path=[Environment]::GetEnvironmentVariable('path','user');\
                                   $new_path=$old_path+';'+'{env_path}';\
                                   [Environment]::SetEnvironmentVariable('path',$new_path,'User');")
        else:
            os.system(f"chmod a+x locas.cmd;\
                        echo 'export LocalAssistant='{env_path}';\
                              export PATH=$LocalAssistant:$PATH' >> ~/.bash_profile;\
                        source ~/.bash_profile")

def setup_rebel(env_path: str, command: str, python: str, sep: str):
    """For our beloved memory."""
    path = os.path.join(env_path, 'models', 'built-in', 'Rebel')
    if pathlib.Path(path).exists():
        print('Found user already install Rebel (Relation extraction).')
        return
    print('Process to install Rebel (Relation extraction model).')

    temp_path: str = os.path.join(env_path, '_temp.py')

    temp_file = open(temp_path, mode='w', encoding='utf-8')
    temp_file.write('from LocalAssistant.model_processor import DownloadExtension\
\nDownloadExtension().download_rebel()')
    temp_file.close()

    os.system(sep.join((command, f'{python} "{temp_path}"')))
    os.remove(temp_path)

def main():
    """The main function."""
    print('Welcome to LocalAssistant automatic installer.')
    assert sys.version_info.major >= 3 and sys.version_info.minor >= 10,\
        f'Python version is expected to be above 3.10, but got {sys.version.split()[0]} instead.'

    env_path: str = choose_path()
    _python, _command, _sep, _pytorch = choose_command()

    os.chdir(env_path)
    venv.create('.venv', with_pip=True, prompt='LocalAssistant')

    # update pip to use `pip index versions LocalAssistant`.
    subprocess.run(f'{_python} -m pip install --upgrade pip',\
        check=False, shell=True, stdout=subprocess.PIPE)
    version = choose_version()

    # Installing dependences.
    print('\nInstalling dependences:')
    os.system(_sep.join([_command, _pytorch, f'pip3 install LocalAssistant=={version} --upgrade']))

    setup_path(env_path)
    setup_rebel(env_path, _command, _python, _sep)

if __name__ == '__main__':
    main()
