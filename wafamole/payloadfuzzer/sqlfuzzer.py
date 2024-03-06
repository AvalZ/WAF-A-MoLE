"""Strategies and fuzzer class module"""

import random
import re
import sqlparse
from wafamole.payloadfuzzer.fuzz_utils import (
    replace_random,
    filter_candidates,
    random_string,
    num_tautology,
    string_tautology,
    num_contradiction,
    string_contradiction,
)


def reset_inline_comments(payload: str):
    """
    Removes a randomly chosen multi-line comment content.

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    positions = list(re.finditer(r"/\*[^(/\*|\*/)]*\*/", payload))

    if not positions:
        return payload

    pos = random.choice(positions).span()

    replacements = ["/**/"]

    replacement = random.choice(replacements)

    new_payload = payload[: pos[0]] + replacement + payload[pos[1] :]

    return new_payload


def logical_invariant(payload: str):
    """
    Adds an invariant boolean condition to the payload.

    E.g., expression OR False
    where expression is a numeric or string tautology such as 1=1 or 'x'<>'y'

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    # rule matching numeric tautologies
    num_tautologies_pos = list(re.finditer(r'\b(\d+)(\s*=\s*|\s+(?i:like)\s+)\1\b', payload))
    num_tautologies_neg = list(re.finditer(r'\b(\d+)(\s*(!=|<>)\s*|\s+(?i:not like)\s+)(?!\1\b)\d+\b', payload))
    # rule matching string tautologies
    string_tautologies_pos = list(re.finditer(r'(\'|\")([a-zA-Z]{1}[\w#@$]*)\1(\s*=\s*|\s+(?i:like)\s+)(\'|\")\2\4', payload))
    string_tautologies_neg = list(re.finditer(r'(\'|\")([a-zA-Z]{1}[\w#@$]*)\1(\s*(!=|<>)\s*|\s+(?i:not like)\s+)(\'|\")(?!\2)([a-zA-Z]{1}[\w#@$]*)\5', payload))
    results = num_tautologies_pos + num_tautologies_neg + string_tautologies_pos + string_tautologies_neg
    if not results:
        return payload
    candidate = random.choice(results)

    pos = candidate.end()

    replacement = random.choice(
        [
            # AND True
            " AND 1",
            " AND True",
            " AND " + num_tautology(),
            " AND " + string_tautology(),
            # OR False
            " OR 0",
            " OR False",
            " OR " + num_contradiction(),
            " OR " + string_contradiction(),
        ]
    )

    new_payload = payload[:pos] + replacement + payload[pos:]

    return new_payload


def change_tautologies(payload: str):
    """
    Replaces a randomly chosen numeric/string tautology with another one.

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    # rules matching numeric tautologies
    num_tautologies_pos = list(re.finditer(r'\b(\d+)(\s*=\s*|\s+(?i:like)\s+)\1\b', payload))
    num_tautologies_neg = list(re.finditer(r'\b(\d+)(\s*(!=|<>)\s*|\s+(?i:not like)\s+)(?!\1\b)\d+\b', payload))
    # rule matching string tautologies
    string_tautologies_pos = list(re.finditer(r'(\'|\")([a-zA-Z]{1}[\w#@$]*)\1(\s*=\s*|\s+(?i:like)\s+)(\'|\")\2\4', payload))
    string_tautologies_neg = list(re.finditer(r'(\'|\")([a-zA-Z]{1}[\w#@$]*)\1(\s*(!=|<>)\s*|\s+(?i:not like)\s+)(\'|\")(?!\2)([a-zA-Z]{1}[\w#@$]*)\5', payload))
    results = num_tautologies_pos + num_tautologies_neg + string_tautologies_pos + string_tautologies_neg
    if not results:
        return payload
    candidate = random.choice(results)

    while True:
        replacements = [num_tautology(), string_tautology()]
        replacement = random.choice(replacements)
        if candidate != replacement:
            break

    new_payload = (
        payload[: candidate.span()[0]] + replacement + payload[candidate.span()[1] :]
    )

    return new_payload


def spaces_to_comments(payload: str):
    """
    Replaces a randomly chosen space character with a multi-line comment (and vice-versa).

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    # TODO: make it selectable (can be mixed with other strategies)
    symbols = {" ": ["/**/"], "/**/": [" "]}

    symbols_in_payload = filter_candidates(symbols, payload)

    if not symbols_in_payload:
        return payload

    # Randomly choose symbol
    candidate_symbol = random.choice(symbols_in_payload)
    # Check for possible replacements
    replacements = symbols[candidate_symbol]
    # Choose one replacement randomly
    candidate_replacement = random.choice(replacements)

    # Apply mutation at one random occurrence in the payload
    return replace_random(payload, re.escape(candidate_symbol), candidate_replacement)


def spaces_to_whitespaces_alternatives(payload: str):
    """
    Replaces a randomly chosen whitespace character with another one.

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    symbols = {
        " ": ["\t", "\n", "\f", "\v", "\xa0"],
        "\t": [" ", "\n", "\f", "\v", "\xa0"],
        "\n": ["\t", " ", "\f", "\v", "\xa0"],
        "\f": ["\t", "\n", " ", "\v", "\xa0"],
        "\v": ["\t", "\n", "\f", " ", "\xa0"],
        "\xa0": ["\t", "\n", "\f", "\v", " "],
    }

    symbols_in_payload = filter_candidates(symbols, payload)

    if not symbols_in_payload:
        return payload

    # Randomly choose symbol
    candidate_symbol = random.choice(symbols_in_payload)
    # Check for possible replacements
    replacements = symbols[candidate_symbol]
    # Choose one replacement randomly
    candidate_replacement = random.choice(replacements)

    # Apply mutation at one random occurrence in the payload
    return replace_random(payload, re.escape(candidate_symbol), candidate_replacement)


def random_case(payload: str):
    """
    Randomly changes the capitalization of the SQL keywords in the input payload.

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    tokens = []
    # Check if the payload is correctly parsed (safety check).
    try:
        parsed_payload = sqlparse.parse(payload)
    except Exception:
        # Just return the input payload if it cannot be parsed to avoid stopping the fuzzing
        return payload
    for t in parsed_payload:
        tokens.extend(list(t.flatten()))

    sql_keywords = set(sqlparse.keywords.KEYWORDS_COMMON.keys())
    # sql_keywords = ' '.join(list(sqlparse.keywords.KEYWORDS_COMMON..keys()) + list(sqlparse.keywords.KEYWORDS.keys()))

    # Make sure case swapping is applied only to SQL tokens
    new_payload = []
    for token in tokens:
        if token.value.upper() in sql_keywords:
            new_token = ''.join([c.swapcase() if random.random() > 0.5 else c for c in token.value])
            new_payload.append(new_token)
        else:
            new_payload.append(token.value)

    return "".join(new_payload)


def comment_rewriting(payload: str):
    """
    Changes the content of a randomly chosen in-line or multi-line comment.
    
    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    p = random.random()

    if p < 0.5 and ("#" in payload or "-- " in payload):
        return payload + random_string(2)
    elif p >= 0.5 and re.search(r"/\*[^(/\*|\*/)]*\*/", payload):
        return replace_random(payload, r"/\*[^(/\*|\*/)]*\*/", "/*" + random_string() + "*/")
    else:
        return payload


def swap_int_repr(payload: str):
    """
    Changes the representation of a randomly chosen numerical constant with an equivalent one.

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    candidates = list(re.finditer(r'\b\d+\b', payload))

    if not candidates:
        return payload

    candidate_pos = random.choice(candidates).span()

    candidate = payload[candidate_pos[0] : candidate_pos[1]]

    replacements = [
        hex(int(candidate)),
        "(SELECT {})".format(candidate),
        # "({})".format(candidate),
        # "OCT({})".format(int(candidate)),
        # "HEX({})".format(int(candidate)),
        # "BIN({})".format(int(candidate))
    ]

    replacement = random.choice(replacements)

    return payload[: candidate_pos[0]] + replacement + payload[candidate_pos[1] :]


def swap_keywords(payload: str):
    """
    Replaces a randomly chosen SQL operator with a semantically equivalent one.

    Arguments:
        payload: query payload (string)

    Returns:
        str: payload modified
    """
    replacements = {
        # OR
        "||": [" OR ", " or "],
        "OR": ["||", "or"],
        "or": ["OR", "||"],
        # AND
        "&&": [" AND ", " and "],
        "AND": ["&&", "and"],
        "and": ["AND", "&&"],
        # Not equals
        "<>": ["!=", " NOT LIKE ", " not like "],
        "!=": ["<>", " NOT LIKE ", " not like "],
        "NOT LIKE": ["not like"],
        "not like": ["NOT LIKE"],
        # Equals
        "=": [" LIKE ", " like "],
        "LIKE": ["like"],
        "like": ["LIKE"]
    }

    # Use sqlparse to tokenize the payload in order to better match keywords,
    # even when they are composed by multiple keywords such as "NOT LIKE"
    tokens = []
    # Check if the payload is correctly parsed (safety check).
    try:
        parsed_payload = sqlparse.parse(payload)
    except Exception:
        # Just return the input payload if it cannot be parsed to avoid stopping the fuzzing
        return payload
    for t in parsed_payload:
        tokens.extend(list(t.flatten()))

    indices = [idx for idx, token in enumerate(tokens) if token.value in replacements]
    if not indices:
        return payload

    target_idx = random.choice(indices)
    new_payload = "".join([random.choice(replacements[token.value]) if idx == target_idx else token.value for idx, token in enumerate(tokens)])

    return new_payload


class SqlFuzzer(object):
    """SqlFuzzer class"""

    strategies = [
        spaces_to_comments,
        random_case,
        swap_keywords,
        swap_int_repr,
        spaces_to_whitespaces_alternatives,
        comment_rewriting,
        change_tautologies,
        logical_invariant,
        reset_inline_comments
    ]

    def __init__(self, payload):
        self.initial_payload = payload
        self.payload = payload

    def fuzz(self):
        strategy = random.choice(self.strategies)

        self.payload = strategy(self.payload)
        # print(self.payload)

        return self.payload

    def current(self):
        return self.payload

    def reset(self):
        self.payload = self.initial_payload
        return self.payload
