import json
import os

from backend import config

MEMORY_FILE = str(config.USER_MEMORY_FILE)


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)


def remember(key, value):

    memory = load_memory()

    memory[key] = value

    save_memory(memory)


def recall(key):

    memory = load_memory()

    return memory.get(key)


def forget(key):

    memory = load_memory()

    if key in memory:
        del memory[key]
        save_memory(memory)
        return True

    return False
