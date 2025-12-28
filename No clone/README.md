# TTS Studio - No Clone Version

This is a lightweight version of TTS Studio without VieNeu-TTS (Vietnamese Neural TTS) dependencies.

## What's Included

- ✅ **CapCut Voice** - TikTok/CapCut TTS API
- ✅ **Edge TTS** - Microsoft Edge Text-to-Speech
- ✅ **Gemini TTS** - Google Gemini Audio Generation
- ✅ **Script Reader** - Batch process text files and documents
- ✅ **Long Text Engine** - Process long texts with chunking
- ✅ **Authentication Module** - Login/session management

## What's Removed

- ❌ **VieNeu-TTS** - Vietnamese Neural TTS with voice cloning
- ❌ All VieNeu-TTS related code, imports, and UI elements
- ❌ VieNeu-TTS directory and dependencies

## Purpose

This version is for users who:
- Don't need Vietnamese neural TTS with voice cloning
- Want a lighter installation without VieNeu-TTS dependencies
- Want to build a standalone executable without VieNeu-TTS

## Installation

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

Note: You can skip any VieNeu-TTS specific dependencies if listed.

2. Run the application:
```bash
python main.py
```

## Building Executable

This version can be built with PyInstaller or Nuitka without VieNeu-TTS:

```bash
# PyInstaller example
pyinstaller main.py --onefile --windowed --name "TTS-Studio-NoClone"

# Nuitka example
python -m nuitka --onefile --windows-disable-console main.py
```

## Files Included

- `main.py` - Main application (VieNeu-TTS code removed)
- `auth_module.py` - Authentication module (unchanged)
- `capcutvoice/` - CapCut Voice API module
- `edge/` - Edge TTS module

## Differences from Full Version

The only difference is the removal of:
- VieNeu-TTS tab from UI
- VieNeu-TTS configuration sections
- VieNeu-TTS processing methods
- VieNeu-TTS related imports and dependencies

All other functionality (CapCut, Edge, Gemini, Script Reader, Long Text) works exactly the same.
