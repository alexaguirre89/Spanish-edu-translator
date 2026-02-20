def translate(text, dialect="mx", mode="translate"):
    text = text.lower().strip()

    # VERY simple examples to start
    if text == "i am tired":
        if mode == "hint":
            return {
                "output": None,
                "explanation": "Use ESTAR for feelings or temporary states.",
                "hint": "Verb: estar (present, yo) + adjective cansado/a"
            }

        return {
            "output": "Estoy cansado." if dialect == "mx" else "Estoy cansado.",
            "explanation": "We use ESTAR because 'tired' is a feeling, not a permanent trait."
        }

    if text == "i am happy":
        return {
            "output": "Estoy contento.",
            "explanation": "Happiness is treated as a temporary emotional state, so ESTAR is used."
        }

    # fallback
    return {
        "output": "Translation not supported yet.",
        "explanation": "This sentence pattern is not implemented in the MVP."
    }
