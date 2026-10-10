<<<<<<< HEAD
# DeskBuddy AI (Windows 11)

A beginner-friendly desktop assistant prototype:
- Cartoon animation with a music-reactive bounce
- Click-to-speak voice recognition
- Text commands
- Opens Chrome, Edge, VS Code, Calculator, Notepad, File Explorer, and YouTube
- Optional AI responses through an OpenAI-compatible API

## 1. Install Python
Install Python 3.12 or 3.13 (64-bit) from https://www.python.org/downloads/windows/
During setup, tick **Add python.exe to PATH** if that option is shown.

## 2. Open this folder in VS Code
Open the folder `DeskBuddyAI` in VS Code, then choose Terminal > New Terminal.

## 3. Create a virtual environment
In the VS Code terminal (PowerShell), run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `py -3.12` isn't available, try `py -3.13`. If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Run the assistant
```powershell
python deskbuddy.py
```

## 5. Try it
- Click **Start music mode**, then play YouTube through your laptop speakers. The microphone listens to nearby sound and the character bounces in response.
- Click **Listen**, then say "open Chrome", "open Calculator", or "open VS Code".
- Or type those commands into the text box.
- Try "what time is it?" or "help".

Music mode and voice recognition both use the microphone. Stop music mode before pressing Listen; the app does this automatically.

## Optional: enable AI answers
AI API calls may cost money. Do not share your API key with anyone or put it in code that you upload to GitHub.

In PowerShell, for the current terminal session only:
```powershell
$env:OPENAI_API_KEY="paste-your-own-key-here"
$env:OPENAI_MODEL="gpt-4o-mini"
python deskbuddy.py
```
Use a key from your provider's official dashboard. API usage is usually billed separately from a ChatGPT subscription. If you do not have a key, app launching, time, help, and basic voice commands still work.

## Microphone troubleshooting
- Windows Settings > Privacy & security > Microphone: allow desktop apps to access the microphone.
- Select the correct input device in Windows Settings > System > Sound.
- Increase the speaker volume; the first version detects sound through the microphone, not direct YouTube/system-audio loopback.
- Speech recognition uses an internet service, so an internet connection is required.

## Limitations of this first version
- The cartoon is a custom-drawn animated placeholder, not a true rigged 3D model yet.
- Music reaction measures sound level from the microphone. It does not identify songs or guarantee exact beat synchronization.
- Speech recognition requires internet.
- The optional AI feature needs a separate API key and may incur charges.
- Only listed/known apps are launched for safety; arbitrary shell commands are not executed.
=======
# DeskBuddy-AI
A desktop cartoon AI assistant with voice commands, app launching, and music-reactive animation.
>>>>>>> c18cc978db73333d572f66e062cb4b3ef821730a
