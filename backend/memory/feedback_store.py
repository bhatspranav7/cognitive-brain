import json
import os

FILE_PATH = "feedback.json"


def save_feedback(query, answer, rating):

    data = []

    if os.path.exists(FILE_PATH):

        with open(FILE_PATH, "r") as f:
            data = json.load(f)

    data.append(
        {
            "query": query,
            "answer": answer,
            "rating": rating
        }
    )

    with open(FILE_PATH, "w") as f:
        json.dump(
            data,
            f,
            indent=4
        )