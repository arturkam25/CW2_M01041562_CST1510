import json
from pathlib import Path

# Folder na historie
CHAT_DIR = Path("DATA/chat_history")
CHAT_DIR.mkdir(parents=True, exist_ok=True)


def _user_file(user_id: int) -> Path:
    """
    Zwraca ścieżkę do pliku historii danego użytkownika
    """
    return CHAT_DIR / f"user_{user_id}.json"


def load_chat_history(user_id: int) -> list:
    """
    Wczytaj historię czatu użytkownika
    """
    file_path = _user_file(user_id)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_chat_history(user_id: int, history: list) -> None:
    """
    Zapisz historię czatu użytkownika
    """
    file_path = _user_file(user_id)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
