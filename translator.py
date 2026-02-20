from grammar.rules import RULES

def translate(text: str, dialect: str, mode: str, speaker_gender: str, you_form: str):
    cleaned = " ".join(text.strip().split())
    for rule in RULES:
        result = rule(cleaned, dialect=dialect, mode=mode, speaker_gender=speaker_gender, you_form=you_form)
        if result is None:
            continue
        # A rule matched and returned something (success or a safe error)
        return result

    # No rules matched: correctness-first response
    return {
        "error": "I can’t safely translate this sentence yet (correctness-first). Try simpler patterns like 'I am + adjective', 'I am + -ing', or 'I like + noun'.",
        "callouts": [
            {"title": "What to try next", "text": "Examples: 'I am tired.' 'I am studying.' 'I like soccer.'"}
        ]
    }
