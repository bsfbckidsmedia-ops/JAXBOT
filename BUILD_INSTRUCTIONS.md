# Build JaxBot Executable

## Prerequisites

- Python 3.7 or higher
- Windows (for .exe) or Linux

## Quick Build

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Build the Executable
```bash
python build_exe.py
```
Or equivalently:
```bash
python build_jaxbot.py
```

This builds a single-file executable at `dist/JaxBot.exe` (Windows) or `dist/JaxBot` (Linux).

### Step 3: Run
```bash
dist\JaxBot.exe
```
Or double-click any of the `.bat` files (`start_vrchat_bot.bat`, `start_main.bat`, `start_minimal.bat`).

## Using JaxBot Console

When you run `JaxBot.exe`, an interactive console opens with a `jaxbot>` prompt:

```
start         - Start the bot (authenticate & begin monitoring)
stop          - Stop the bot gracefully
status        - Show bot status
chatbox <msg> - Send a message to the VRChat ChatBox
tts <msg>     - Speak a message via text-to-speech
say <msg>     - Send to ChatBox AND speak via TTS
scroll <msgs> - Set scrolling messages (comma-separated)
scroll stop   - Stop scrolling messages
voices        - List available TTS voices
voice <id>    - Set TTS voice by ID
rate <wpm>    - Set TTS speech rate
volume <0-1>  - Set TTS volume
clear         - Clear the ChatBox
config        - Show current configuration
help          - Show help
quit / exit   - Shut down and exit
```

## First Time Setup

1. Edit `nano.env` with your VRChat credentials
2. Run `JaxBot.exe` (or a `.bat` file)
3. Type `start` to authenticate and launch the bot
4. Enable OSC in VRChat (Settings > OSC > Enable) for ChatBox to work

## Portable Package

To create a portable folder with the exe and config files:
```bash
python build_exe.py --pack
```
This creates a `JaxBot_Portable/` folder with `JaxBot.exe`, config files, `START.bat`, and a README.

## Troubleshooting

**"JaxBot.exe not found"**
- Run `python build_exe.py` first to build it

**"ModuleNotFoundError" during build**
- Run `pip install -r requirements.txt` to install all dependencies

**"Antivirus detection"**
- PyInstaller executables may be flagged as false positives — add an exception

**"VRChat authentication failed"**
- Check credentials in `nano.env`
- Verify 2FA code if enabled

**TTS not working on Windows**
- SAPI5 is used by default on Windows (built-in)
- On Linux, install `espeak-ng`

## System Requirements

- **OS**: Windows 7+ or Linux
- **RAM**: 2GB minimum
- **Storage**: 500MB free space
- **Network**: Internet connection for VRChat features
