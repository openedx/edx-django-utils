"""
Models used in testing manufacture_data command
"""
from django.db import models


class TestNationalId(models.Model):
    """
    For use in testing manufacture_data command
    """
    class Meta:
        app_label = 'data_generation_tests'

    id_number = models.CharField(max_length=10)


class TestPerson(models.Model):
    """
    For use in testing manufacture_data command
    """
    class Meta:
        app_label = 'data_generation_tests'

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    national_id = models.ForeignKey(TestNationalId, null=True, on_delete=models.CASCADE)


class TestCompany(models.Model):
    """
    For use in testing manufacture_data command
    """
    class Meta:
        app_label = 'data_generation_tests'
    company_name = models.CharField(max_length=30)
    national_id = models.ForeignKey(TestNationalId, null=True, on_delete=models.CASCADE)
    ceo = models.ForeignKey(TestPerson, null=True, on_delete=models.CASCADE)


class TestContactInfo(models.Model):
    """
    For use in testing manufacture_data command
    """
    class Meta:
        app_label = 'data_generation_tests'
    test_person = models.ForeignKey(TestPerson, null=True, on_delete=models.CASCADE)
    test_company = models.ForeignKey(TestCompany, null=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)


class TestPersonContactPhoneNumber(models.Model):
    """
    For use in testing manufacture_data command
    """
    class Meta:
        app_label = 'data_generation_tests'
    test_contact_info = models.ForeignKey(TestContactInfo, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)


class test_model_nonstandard_casing(models.Model):
    """
    For use in testing manufacture_data command
    """
    class Meta:
        app_label = 'data_generation_tests'
    test_field = models.CharField(max_length=30)
