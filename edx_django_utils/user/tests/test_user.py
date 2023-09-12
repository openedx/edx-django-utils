"""Test user functions"""

import string
import unicodedata

import pytest
from django.test import TestCase
from django.test.utils import override_settings

from edx_django_utils.user import generate_password


class GeneratePasswordTest(TestCase):
    """Tests formation of randomly generated passwords."""

    def test_default_args(self):
        password = generate_password()
        assert 12 == len(password)
        assert any(c.isdigit for c in password)
        assert any(c.isalpha for c in password)

    def test_length(self):
        length = 25
        assert length == len(generate_password(length=length))

    def test_chars(self):
        char = '!'
        password = generate_password(length=12, chars=(char,))

        assert any(c.isdigit for c in password)
        assert any(c.isalpha for c in password)
        assert (char * 10) == password[2:]

    def test_min_length(self):
        with pytest.raises(ValueError):
            generate_password(length=7)

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.MinimumLengthValidator",
                "OPTIONS": {"min_length": 2},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.MaximumLengthValidator",
                "OPTIONS": {"max_length": 75},
            },
        ]
    )
    def test_third_party_auth_utils_generate_password_default_validators(self):
        """
        Test the generate_password function using the default openedx edx-platform validators.
        """
        self.assertEqual(len(generate_password(length=12)), 12)

        self.assertEqual(len(generate_password(length=50)), 50)

        with self.assertRaises(ValueError):
            generate_password(length=5)

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.MinimumLengthValidator",
                "OPTIONS": {"min_length": 8},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.MaximumLengthValidator",
                "OPTIONS": {"max_length": 75},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.UppercaseValidator",
                "OPTIONS": {"min_upper": 1},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.LowercaseValidator",
                "OPTIONS": {"min_lower": 1},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.NumericValidator",
                "OPTIONS": {"min_numeric": 1},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.PunctuationValidator",
                "OPTIONS": {"min_punctuation": 1},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.SymbolValidator",
                "OPTIONS": {"min_symbol": 1},
            },
            {
                "NAME": "common.djangoapps.util.password_policy_validators.AlphabeticValidator",
                "OPTIONS": {"min_alphabetic": 3},
            },
        ]
    )
    def test_third_party_auth_utils_generate_password_all(self):
        """
        Test the `generate_password` function using a much stronger security validators.
        It executes the same test multiple times, because of the random logic of the
        generate_password function.
        """
        self.assertEqual(len(generate_password(length=12)), 12)

        self.assertEqual(len(generate_password(length=8)), 8)

        with self.assertRaises(ValueError):
            generate_password(length=5)

        # because of the random logic, we test the same code 10 times
        for _ in range(10):
            password = generate_password(length=12)

            self.assertEqual(len(password), 12)

            self.assertGreaterEqual(
                sum(1 if char in string.ascii_uppercase else 0 for char in password),
                1,
                msg=f"Password '{password}' should have at least 1 upper case character",
            )

            self.assertGreaterEqual(
                sum(1 if char in string.ascii_lowercase else 0 for char in password),
                1,
                msg=f"Password '{password}' should have at least 1 lower case character",
            )

            self.assertGreaterEqual(
                sum(1 if char in string.digits else 0 for char in password),
                1,
                msg=f"Password '{password}' should have at least 1 numeric character",
            )

            self.assertGreaterEqual(
                sum(1 if char in string.punctuation else 0 for char in password),
                1,
                msg=f"Password '{password}' should have at least 1 punctuation character",
            )

            self.assertGreaterEqual(
                sum(1 if 'S' in unicodedata.category(char) else 0 for char in password),
                1,
                msg=f"Password '{password}' should have at least 1 symbol character",
            )
