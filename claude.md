# Project Instructions

This file contains project-specific instructions, guidelines, and conditions for Claude when working in this repository.

# Application
MineDeezCoords is a Python-based Discord bot (`discord.py`) designed for managing Minecraft coordinates across multiple dimensions with support for the Catalan language.

How it works:
1. Discord Bot Engine (`bot.py`): Handles slash commands, interactive buttons, views, and automated status/embed updates.
2. Persistent Storage (`coordinates.json` & backups): Saves and loads location records persistently for 3 dimensions (Overworld 🌳, Nether 👹, End 😈) with automatic timestamped backups.
3. Catalan Formatting (`format_location_name`): Formats location names following Catalan grammar and preposition rules while preserving mid-word capitals.

# For who
This is for me, Joaquim. I'm a photographer and filmmaker, and I want to keep everything organized and accessible. I'm not a programmer, but I have a little bit of technical knowledge, so I want you to explain changes to the app in one sentence and keep them easy to understand.

# Rules
1. Always, before a change, first plan and wait until I say yes.
2. One change at a time. When it works, we save it with a git commit and we move to the next one.
3. Always ask me any information you need to do it better and this way not doing mistakes.
4. Never commit sensitive data or secrets (like Discord bot tokens or `.env` files).
5. Keep changes minimal and follow existing codebase patterns and language conventions (Catalan documentation/UI where applicable).
