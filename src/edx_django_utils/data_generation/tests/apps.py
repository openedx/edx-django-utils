"""
Tests for Data Generation
"""


from django.apps import AppConfig


class DataGenerationTestsConfig(AppConfig):
    name = 'edx_django_utils.data_generation.tests'
    label = 'data_generation_tests'  # Needed to avoid App label duplication with other tests modules
