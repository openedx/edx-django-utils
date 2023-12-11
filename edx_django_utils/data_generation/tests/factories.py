"""
Factories for models used in testing manufacture_data command
"""

import factory

from edx_django_utils.data_generation.tests.models import (
    TestCompany,
    TestContactInfo,
    TestNationalId,
    TestPerson,
    TestPersonContactPhoneNumber,
    test_model_nonstandard_casing
)


class TestNationalIdFactory(factory.django.DjangoModelFactory):
    """
    Test Factory for TestNationalId
    """

    class Meta:
        model = TestNationalId

    id_number = "123456789"


class TestPersonFactory(factory.django.DjangoModelFactory):
    """
    Test Factory for TestPerson
    """

    class Meta:
        model = TestPerson

    first_name = "John"
    last_name = "Doe"
    national_id = factory.SubFactory(TestNationalIdFactory)


class TestCompanyFactory(factory.django.DjangoModelFactory):
    """
    Test Factory for TestCompany
    """

    class Meta:
        model = TestCompany

    company_name = "Acme, Inc"
    national_id = factory.SubFactory(TestNationalIdFactory)
    ceo = factory.SubFactory(TestPersonFactory)


class TestContactInfoFactory(factory.django.DjangoModelFactory):
    """
    Test Factory for TestContactInfo
    """

    class Meta:
        model = TestContactInfo

    test_person = factory.SubFactory(TestPersonFactory)
    test_company = factory.SubFactory(TestCompanyFactory)
    address = "123 4th st, Fiveville, AZ, 67890"


class TestPersonContactPhoneNumberFactory(factory.django.DjangoModelFactory):
    """
    Test Factory for TestPersonContactPhoneNumber
    """

    class Meta:
        model = TestPersonContactPhoneNumber

    test_contact_info = factory.SubFactory(TestContactInfoFactory)
    phone_number = "(123) 456-7890"


class TestModelNonstandardCasingFactory(factory.django.DjangoModelFactory):
    """
    Test Factory for test_model_nonstandard_casing
    """

    class Meta:
        model = test_model_nonstandard_casing

    test_field = "TEST"


class AbstractFactory(factory.django.DjangoModelFactory):
    """
    Test factory for making sure our factory discovery doesn't choke on abstract factory classes
    """
