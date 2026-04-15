import json
import uuid
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path("data/run_memory.json")


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_run(record: dict):
    memory = load_memory()

    record_to_save = record.copy()

    if "run_id" not in record_to_save:
        record_to_save["run_id"] = str(uuid.uuid4())[:8]

    if "timestamp" not in record_to_save:
        record_to_save["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    memory.append(record_to_save)

    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)