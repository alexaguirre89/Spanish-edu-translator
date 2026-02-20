# grammar/rules.py
import re
from grammar.verbs import agree_adjective, present_conjugate

# Tiny bilingual lexicon (grow over time)
LEX_ADJ = {
    "tired": {"lemma": "cansado", "type": "feeling"},
    "bored": {"lemma": "aburrido", "type": "feeling"},
    "happy": {"lemma": "contento", "type": "feeling"},
    "sad": {"lemma": "triste", "type": "feeling"},
    "smart": {"lemma": "inteligente", "type": "trait"},
    "hardworking": {"lemma": "trabajador", "type": "trait"},
    "lazy": {"lemma": "perezoso", "type": "trait"},
}

LEX_NOUN = {
    "soccer": {"mx": "futbol", "es": "futbol", "gender": "m"},
    "car": {"mx": "carro", "es": "coche", "gender": "m"},
    "house": {"mx": "casa", "es": "casa", "gender": "f"},
}

def callout(title: str, text: str) -> dict:
    return {"title": title, "text": text}

def detect_subject(en: str, you_form: str) -> tuple[str, str]:
    """
    Returns (spanish_subject_key, english_subject)
    spanish_subject_key is one of: yo, tu, usted, el, ella, nosotros, nosotras, ellos, ellas, ustedes
    """
    s = en.strip().lower()
    if s.startswith("i "): return "yo", "i"
    if s.startswith("you "): return ("usted" if you_form == "usted" else "tu"), "you"
    if s.startswith("he "): return "el", "he"
    if s.startswith("she "): return "ella", "she"
    if s.startswith("we "): return "nosotros", "we"
    if s.startswith("they "): return "ellos", "they"
    return "yo", "i"

# ----------------------------
# Rule 1: Ser vs Estar + adjectives
# Supports: I am/You are/He is/She is/We are + adjective
# ----------------------------
BE_ADJ_RE = re.compile(r"^(i|you|he|she|we|they)\s+(am|are|is)\s+([a-z]+)\.?$", re.I)

def rule_ser_estar_adjective(en: str, dialect: str, mode: str, speaker_gender: str, you_form: str):
    m = BE_ADJ_RE.match(en.strip())
    if not m:
        return None

    subj_key, _ = detect_subject(en, you_form)
    adj_en = m.group(3).lower()

    if adj_en not in LEX_ADJ:
        return {
            "error": f"I recognize the pattern, but I don't know the adjective '{adj_en}' yet (add it to the lexicon).",
            "callouts": [callout("MVP Limitation", "This app prioritizes correctness. Add the missing adjective to the lexicon to translate safely.")],
        }

    adj_info = LEX_ADJ[adj_en]
    adj_lemma = adj_info["lemma"]
    kind = adj_info["type"]  # feeling or trait

    # choose copula
    copula = "estar" if kind == "feeling" else "ser"

    # conjugate
    verb = present_conjugate(copula, subj_key)
    if not verb:
        return {"error": "Could not conjugate verb for this subject (MVP bug).", "callouts": []}

    # gender/number
    if subj_key in ("nosotros", "ellos", "ustedes"):
        number = "p"
    else:
        number = "s"

    if subj_key == "ella":
        gender = "f"
    elif subj_key == "el":
        gender = "m"
    elif subj_key in ("nosotros", "yo", "tu", "usted"):
        gender = speaker_gender
    else:
        gender = "m"

    adj_surface = agree_adjective(adj_lemma, gender=gender, number=number)

    # callouts
    callouts = []
    callouts.append(callout(
        "Ser vs. Estar",
        "Use **estar** for temporary states/feelings and **ser** for traits/identity. "
        f"Here, '{adj_en}' is treated as a **{kind}**, so we used **{copula}**."
    ))
    callouts.append(callout(
        "Adjective Agreement",
        f"Adjectives match **gender/number**. We used **{adj_surface}** based on the subject."
    ))

    if mode == "hint":
        return {
            "hint": [
                f"Verb root: **{copula}** (present tense). Conjugate for **{subj_key}**.",
                f"Adjective lemma: **{adj_lemma}**. Make it agree with the subject.",
                "Put together: ______ ______."
            ],
            "callouts": callouts
        }

    return {"spanish": f"{verb} {adj_surface}.", "callouts": callouts}

# ----------------------------
# Rule 2: Present progressive (estar + gerund)
# Supports: I am studying / He is eating / We are writing (limited verb list)
# ----------------------------
PROG_RE = re.compile(r"^(i|you|he|she|we|they)\s+(am|are|is)\s+([a-z]+ing)\.?$", re.I)

GERUND_BASE = {
    "studying": "estudiar",
    "eating": "comer",
    "writing": "escribir",
    "reading": "leer",
    "talking": "hablar",
}

def make_gerund(inf: str) -> str | None:
    inf = inf.lower()
    if inf.endswith("ar"):
        return inf[:-2] + "ando"
    if inf.endswith(("er", "ir")):
        return inf[:-2] + "iendo"
    return None

def rule_present_progressive(en: str, dialect: str, mode: str, speaker_gender: str, you_form: str):
    m = PROG_RE.match(en.strip())
    if not m:
        return None

    subj_key, _ = detect_subject(en, you_form)
    ing = m.group(3).lower()

    if ing not in GERUND_BASE:
        return {
            "error": f"I recognize the pattern, but I don't know the -ing verb '{ing}' yet.",
            "callouts": [callout("MVP Limitation", "Add this -ing verb to the progressive verb list to support it.")],
        }

    inf = GERUND_BASE[ing]
    estar = present_conjugate("estar", subj_key)
    ger = make_gerund(inf)
    if not estar or not ger:
        return {"error": "Could not build present progressive (MVP bug).", "callouts": []}

    callouts = [callout(
        "Present Progressive",
        "Use **estar + gerund** to say what someone is doing right now. "
        f"**{estar} {ger}** = '{en.strip()}'"
    )]

    if mode == "hint":
        return {
            "hint": [
                "Use **estar** in the present tense for the subject.",
                f"Make the gerund: **{inf}** → **{ger}**",
                "Put together: ______ ______."
            ],
            "callouts": callouts
        }

    return {"spanish": f"{estar} {ger}.", "callouts": callouts}

# ----------------------------
# Rule 3: Gustar (I like X / We like X) limited nouns
# Supports: I like the car / I like soccer / We like the house
# ----------------------------
GUSTAR_RE = re.compile(r"^(i|we)\s+like\s+(the\s+)?([a-z]+)\.?$", re.I)

def rule_gustar(en: str, dialect: str, mode: str, speaker_gender: str, you_form: str):
    m = GUSTAR_RE.match(en.strip())
    if not m:
        return None

    subj = m.group(1).lower()
    noun_en = m.group(3).lower()

    if noun_en not in LEX_NOUN:
        return {
            "error": f"I recognize 'like', but I don't know the noun '{noun_en}' yet.",
            "callouts": [callout("MVP Limitation", "Add the noun to the noun lexicon to translate gustar safely.")],
        }

    noun = LEX_NOUN[noun_en]["mx"] if dialect == "mx" else LEX_NOUN[noun_en]["es"]
    gender = LEX_NOUN[noun_en]["gender"]

    # singular only for MVP
    article = "el" if gender == "m" else "la"

    # gustar agrees with thing liked (singular gusta)
    gusta = "gusta"

    # IO pronoun depends on who likes
    io = "me" if subj == "i" else "nos"

    callouts = [
        callout(
            "Gustar Structure",
            "With **gustar**, the thing you like is the grammatical subject. "
            "So Spanish says: 'To me, the car is pleasing.'"
        ),
        callout(
            "Indirect Object Pronouns",
            f"We used **{io}** because it means 'to me' (me) or 'to us' (nos)."
        ),
        callout(
            "Articles",
            f"We used **{article}** because '{noun}' is {'masculine' if gender=='m' else 'feminine'}."
        ),
    ]

    if mode == "hint":
        return {
            "hint": [
                f"IO pronoun: **{io}**",
                f"Use **{gusta}** (singular) because the thing liked is singular.",
                f"Use article **{article}** + noun **{noun}**",
                "Put together: ______ ______ ______ ______."
            ],
            "callouts": callouts
        }

    return {"spanish": f"{io} {gusta} {article} {noun}.", "callouts": callouts}

# ----------------------------
# Registry of rules (order matters)
# ----------------------------
RULES = [
    rule_present_progressive,
    rule_gustar,
    rule_ser_estar_adjective,
]
