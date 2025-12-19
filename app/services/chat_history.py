# ==============================================================================
# CHAT HISTORY STORAGE AND MANAGEMENT
# ==============================================================================

# This file is responsible for managing persistent chat history
# for individual users within the application.

# Scope of responsibility:
# - defining the storage location for chat history files
# - loading chat history for a specific user
# - saving updated chat history to disk
# - clearing chat history on user request or logout

# Architectural role:
# - lightweight file-based persistence layer
# - independent from database and authentication layers
# - used by chat-related services and UI components

# Design notes:
# - chat history is stored per user in separate JSON files
# - this avoids database overhead for conversational data
# - the structure is simple, readable and easy to debug

import json
from pathlib import Path

# ==============================================================================
# STORAGE CONFIGURATION
# ==============================================================================

# This section defines the directory structure
# used to store chat history files.

CHAT_DIR = Path("DATA/chat_history")
CHAT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# INTERNAL PATH HELPERS
# ==============================================================================

# This section contains internal helper functions
# used to resolve file paths for user chat history.

def _user_file(user_id: int) -> Path:
    # Returns the filesystem path to the chat history file
    # associated with a specific user.
    return CHAT_DIR / f"user_{user_id}.json"

# ==============================================================================
# CHAT HISTORY READ OPERATIONS
# ==============================================================================

# This section provides safe read access
# to stored user chat history.

def load_chat_history(user_id: int) -> list:
    # Loads chat history for a given user.
    
    # Behaviour:
    # - returns an empty list if no history exists
    # - returns an empty list if the file is unreadable
    file_path = _user_file(user_id)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# ==============================================================================
# CHAT HISTORY WRITE OPERATIONS
# ==============================================================================

# This section handles persisting chat history
# to disk.

def save_chat_history(user_id: int, history: list) -> None:
    # Saves the provided chat history for a given user.
    #
    # Notes:
    # - existing history is fully overwritten
    # - UTF-8 encoding is enforced
    file_path = _user_file(user_id)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ==============================================================================
# CHAT HISTORY MAINTENANCE
# ==============================================================================

# This section provides cleanup functionality
# for user chat history.

def clear_chat_history(user_id: int) -> None:
    # Removes the chat history file for a given user
    # if it exists.
    file_path = _user_file(user_id)

    if file_path.exists():
        file_path.unlink()
