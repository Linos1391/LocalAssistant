"""User friendly LocalAssistant automatic installer."""

import os
import pathlib
import sys
import venv

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

print(f"'{PATH}' will be used.\n")
PYTORCH = input('Visit https://pytorch.org/get-started/locally/ and paste in your command (pip3): ')
assert PYTORCH.split()[0] == 'pip3', "Incorrect commands, expect 'pip3' at start."

os.chdir(PATH)
venv.create('.venv', with_pip=True, prompt='LocalAssistant')

if sys.platform == 'win32':
    COMMAND = '.venv\\Scripts\\activate'
    SEP = '&&'
else:
    COMMAND = 'source .venv/bin/activate'
    SEP = ';'

print('\nInstalling dependences:')

os.system(SEP.join([COMMAND,PYTORCH,'pip3 install LocalAssistant --upgrade']))

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

if sys.platform == 'win32':
    os.system(f"powershell $old_path = [Environment]::GetEnvironmentVariable('path', 'user');\
                           $new_path = $old_path + ';' + '{PATH}';\
                           [Environment]::SetEnvironmentVariable('path', $new_path,'User');")
else:
    os.system(f"chmod a+x locas.cmd;\
                echo 'export LocalAssistant='{PATH}';\
                      export PATH=$LocalAssistant:$PATH' >> ~/.bash_profile;\
                source ~/.bash_profile")
