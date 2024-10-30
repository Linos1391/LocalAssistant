:; if [ -z 0 ]; then
  @echo off
  goto :WINDOWS
fi
#UNIX

# -- Add Conda or Docker here. Eg: conda activate ... ; python ./LocalAssistant/parser.py $@
python ./LocalAssistant/parser.py $@

exit 0

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

:WINDOWS

REM -- Add Conda or Docker here. Eg: conda activate ... && python LocalAssistant/parser.py %*
python LocalAssistant/parser.py %*
