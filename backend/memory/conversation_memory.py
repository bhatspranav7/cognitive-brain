conversation_history = []


def save_interaction(question, answer):

    conversation_history.append(
        {
            "question": question,
            "answer": answer
        }
    )


def get_recent_context(limit=5):

    return conversation_history[-limit:]