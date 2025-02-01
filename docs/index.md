**LocalAssistant - Your CLI friend**

```
>> locas.cmd -h

usage: locas [-h] [-v] [-V] COMMAND ...

LocalAssistant (locas) is an AI designed to be used in CLI.

options:
  -h, --help          show this help message and exit
  -v, --verbose       show debug messages (Can be used multiple times for higher level: CRITICAL[v] -> DEBUG[vvvv])
  -V, --version       show program's version number and exit

commands:
  built-in commands (type 'locas COMMAND -h' for better description).

  COMMAND
    download          Download models from Hugging Face
    config            Configurate LocalAssistant.
    user              Config user.
    chat              Chat with models for limited lines. (no history saved)
    start             Chat with models using history.
    docs              Ask information from provided documents.
    self-destruction  LocalAssistant's self-destruction.
```
## Guidance

Learn more through these instructions below:

- [Installation](installation.md)
- [Quick Start](quick_start.md)
- [Models](models.md)
- [Commands](commands.md)

## Contribution

Below is what I tried but could not get it done. So your help will help me a lot!

- **Call time:** I tested `locas` with Powershell's `Measure-Command`, I got 7-9s. But then when trying with `CProfile.run()`, it's approximately 0.2s... Why...?
- **pytest:** I know this sounds wrong, but I don't even know where to start. Maybe I will try again, but not right now I guess.

Not just those above. All contributions are welcomed, I would be grateful for one day having peer coders beside me!

## License

[GNU GPLv3](https://github.com/Linos1391/LocalAssistant/blob/main/LICENSE)

## Disclaimer

This AI was designed to communicating with Hugging Face models in CLI. Please do not use this AI for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
