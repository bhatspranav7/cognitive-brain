import json
import os

FEEDBACK_FILE = "feedback.json"


def load_feedback():

    if not os.path.exists(FEEDBACK_FILE):
        return []

    with open(
        FEEDBACK_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_average_rating():

    feedback = load_feedback()

    if not feedback:
        return 0

    ratings = [
        item["rating"]
        for item in feedback
    ]

    return round(
        sum(ratings) / len(ratings),
        2
    )


def get_query_score(query):

    feedback = load_feedback()

    scores = []

    for item in feedback:

        if (
            item.get("query", "")
            .lower()
            == query.lower()
        ):

            scores.append(
                item["rating"]
            )

    if not scores:
        return None

    return round(
        sum(scores) / len(scores),
        2
    )