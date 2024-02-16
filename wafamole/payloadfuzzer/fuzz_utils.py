import re
import random
import string
from wafamole.utils.check import type_check


def replace_nth(candidate, sub, wanted, n):
    """Replace the n-th occurrence of a portion of the candidate with wanted.

    Arguments:
        candidate (str) : the string to be modified
        sub (str) 		: regexp containing what to substitute
        wanted (str) 	: the string that will replace sub
        n (int)			: the index of the occurrence to replace

    Raises:
        TypeError : bad type passed as arguments

    Returns:
        (str) : the modified string
    """
    type_check(candidate, str, "candidate")
    type_check(sub, str, "sub")
    type_check(wanted, str, "wanted")
    type_check(n, int, "n")
    match = [m for m in re.finditer(re.escape(sub), candidate)][n - 1]
    before = candidate[:match.start()]
    after = candidate[match.end():]
    result = before + wanted + after
    return result


def replace_random(candidate, sub, wanted):
    """Replace one picked at random of the occurrence of sub inside candidate with wanted.

    Arguments:
        candidate (str) : the string to be modified
        sub (str) 		: regexp containing what to substitute
        wanted (str) 	: the string that will replace sub

    Raises:
        TypeError : bad type passed as arguments

    Returns:
        (str) : the modified string
    """
    type_check(candidate, str, "candidate")
    type_check(sub, str, "sub")
    type_check(wanted, str, "wanted")

    occurrences = list(re.finditer(sub, candidate))
    if not occurrences:
        return candidate

    match = random.choice(occurrences)

    before = candidate[:match.start()]
    after = candidate[match.end():]
    result = before + wanted + after

    return result


def filter_candidates(symbols, payload):
    """It removes all the symbols that are not contained inside the input payload string.

    Arguments:
        symbols (dict)  : dictionary of symbols to filter (using the key)
        payload (str)   : the payload to use for the filtering

    Raises:
        TypeError : bad types passed as argument

    Returns:
        list : a list containing all the symbols that are contained inside the payload.

    """
    type_check(symbols, dict, "symbols")
    type_check(payload, str, "payload")

    return [s for s in symbols.keys() if re.search(r'{}'.format(re.escape(s)), payload)]


def random_char(spaces=True):
    """Returns a random character.

    Keyword Arguments:
        spaces (bool) : include spaces [default = True]

    Raises:
        TypeError: spaces not bool


    Returns:
        str : random character
    """

    type_check(spaces, bool, "spaces")
    chars = string.digits + string.ascii_letters + string.punctuation
    if spaces:
        chars += string.whitespace
    return random.choice(chars)


def random_string(max_len=5, spaces=True):
    """It creates a random string.

    Keyword Arguments:
        max_length (int) : the maximum length of the string [default=5]
        spaces (bool) : if True, all the printable character will be considered. Else, only letters and digits [default=True]

    Raises:
        TypeError: bad type passed as argument

    Returns:
        (str) : random string

    """
    type_check(max_len, int, "max_length")
    type_check(spaces, bool, "spaces")

    return "".join(
        [random_char(spaces=spaces) for i in range(random.randint(1, max_len))]
    )


def string_tautology():
    """Returns a random tautology chosen from a fixed set.

    Returns:
        (str) : string containing a tautology
    """
    # TODO: remove magic numbers, move it at top of document
    value_s = random_string(random.randint(1, 5))

    tautologies = [
        # Strings - equals
        "'{}'='{}'".format(value_s, value_s),
        "'{}' LIKE '{}'".format(value_s, value_s),
        "'{}'='{}'".format(value_s, value_s),
        "'{}' LIKE '{}'".format(value_s, value_s),
        # Strings - not equal
        "'{}'!='{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}'<>'{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}' NOT LIKE '{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}'!='{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}'<>'{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}' NOT LIKE '{}'".format(value_s, value_s + random_string(1, spaces=False)),
    ]

    return random.choice(tautologies)


def string_contradiction():
    """Returns a random contradiction chosen from a fixed set.

    Returns:
        (str) : string containing a contradiction
    """
    value_s = random_string(random.randint(1, 5))

    contradictions = [
        # Strings - equals
        "'{}'='{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}' LIKE '{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}'='{}'".format(value_s, value_s + random_string(1, spaces=False)),
        "'{}' LIKE '{}'".format(value_s, value_s + random_string(1, spaces=False)),
        # Strings - not equal
        "'{}'!='{}'".format(value_s, value_s),
        "'{}'<>'{}'".format(value_s, value_s),
        "'{}' NOT LIKE '{}'".format(value_s, value_s),
        "'{}'!='{}'".format(value_s, value_s),
        "'{}'<>'{}'".format(value_s, value_s),
        "'{}' NOT LIKE '{}'".format(value_s, value_s),
    ]

    return random.choice(contradictions)


def num_tautology():
    """Returns a random tautology explicit using numbers chosen from a fixed set.

    Returns:
        (str) : string containing a tautology
    """
    value_n = random.randint(1, 10000)

    tautologies = [
        # Numbers - equal
        "{}={}".format(value_n, value_n),
        "{} LIKE {}".format(value_n, value_n),
        # Numbers - not equal
        "{}!={}".format(value_n, value_n + 1),
        "{}<>{}".format(value_n, value_n + 1),
        "{} NOT LIKE {}".format(value_n, value_n + 1),
        "{} IN ({},{},{})".format(value_n, value_n - 1, value_n, value_n + 1),
    ]

    return random.choice(tautologies)


def num_contradiction():
    """Returns a random contradiction explicit using numbers chosen from a fixed set.

    Returns:
        (str) : string containing a contradiction
    """
    value_n = random.randint(1, 10000)

    contradictions = [
        # Numbers - equal
        "{}={}".format(value_n, value_n + 1),
        "{} LIKE {}".format(value_n, value_n + 1),
        # Numbers - not equal
        "{}!={}".format(value_n, value_n),
        "{}<>{}".format(value_n, value_n),
        "{} NOT LIKE {}".format(value_n, value_n),
        "{} NOT IN ({},{},{})".format(value_n, value_n - 1, value_n, value_n + 1),
    ]

    return random.choice(contradictions)
