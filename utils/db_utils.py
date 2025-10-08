
import json
import os

HISTORY_PATH = "data/history.json"

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []

    if os.path.getsize(HISTORY_PATH) == 0:
        return []

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(username, disease, language, solution):
    history = load_history()
    entry = {"user": username, "disease": disease, "language": language, "solution": solution}
    history.append(entry)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)