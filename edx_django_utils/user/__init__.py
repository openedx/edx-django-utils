"""
User and group utilities useful to multiple django services will live here.
"""

import random
import string
import sys
import unicodedata

from django.conf import settings


def _password_complexity():
    """
    Inspect AUTH_PASSWORD_VALIDATORS setting and generate a dict with the requirements for
    usage in the `generate_password` function.
    """
    password_validators = settings.AUTH_PASSWORD_VALIDATORS
    known_validators = {
        "common.djangoapps.util.password_policy_validators.MinimumLengthValidator": "min_length",
        "common.djangoapps.util.password_policy_validators.MaximumLengthValidator": "max_length",
        "common.djangoapps.util.password_policy_validators.AlphabeticValidator": "min_alphabetic",
        "common.djangoapps.util.password_policy_validators.UppercaseValidator": "min_upper",
        "common.djangoapps.util.password_policy_validators.LowercaseValidator": "min_lower",
        "common.djangoapps.util.password_policy_validators.NumericValidator": "min_numeric",
        "common.djangoapps.util.password_policy_validators.PunctuationValidator": "min_punctuation",
        "common.djangoapps.util.password_policy_validators.SymbolValidator": "min_symbol",
    }
    complexity = {}

    for validator in password_validators:
        param_name = known_validators.get(validator["NAME"], None)
        if param_name is not None:
            complexity[param_name] = validator["OPTIONS"].get(param_name, 0)

    # merge alphabetic with lower and uppercase
    if complexity.get("min_alphabetic") and (
        complexity.get("min_lower") or complexity.get("min_upper")
    ):
        complexity["min_alphabetic"] = max(
            0,
            complexity["min_alphabetic"]
            - complexity.get("min_lower", 0)
            - complexity.get("min_upper", 0),
        )

    return complexity


def _symbols():
    """Get all valid symbols"""
    symbols = []
    for c in map(chr, range(sys.maxunicode + 1)):
        if 'S' in unicodedata.category(c):
            symbols.append(c)
    return symbols


def generate_password(length=12, chars=string.ascii_letters + string.digits):
    """Generate a valid random password using the configured password validators,
    `AUTH_PASSWORD_VALIDATORS` setting if defined."""
    if length < 8:
        raise ValueError("password must be at least 8 characters")

    password = ''
    choice = random.SystemRandom().choice

    default_min_length = 8
    complexity = _password_complexity()
    password_length = max(length, complexity.get('min_length', default_min_length))

    password_rules = {
        'min_lower': list(string.ascii_lowercase),
        'min_upper': list(string.ascii_uppercase),
        'min_alphabetic': list(string.ascii_letters),
        'min_numeric': list(string.digits),
        'min_punctuation': list(string.punctuation),
        'min_symbol': list(_symbols()),
    }

    for rule, elems in password_rules.items():
        needed = complexity.get(rule, 0)
        for _ in range(needed):
            next_char = choice(elems)
            password += next_char
            elems.remove(next_char)

    # fill the password to reach password_length
    if len(password) < password_length:
        password += ''.join(
            [choice(chars) for _ in range(password_length - len(password))]
        )

    password_list = list(password)
    random.shuffle(password_list)

    password = ''.join(password_list)
    return password
