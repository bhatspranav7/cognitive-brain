import json
import os

from backend import config

FILE_PATH = str(config.FEEDBACK_FILE)


def save_feedback(query, answer, rating):

    data = []

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    data.append(
        {
            "query": query,
            "answer": answer,
            "rating": rating,
        }
    )

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
