"""
Test management commands and related functions.
"""

import mock
from django.core.management import get_commands, load_command_class
from django.core.management.base import CommandError, SystemCheckError
from django.test import TestCase
from pytest import mark

from edx_django_utils.data_generation.management.commands.manufacture_data import Command, Node
# We need to import factories even if we don't use them directly, in order for them to be picked up
# by the manufacture_data command's discovery process
# pylint: disable=unused-import
from edx_django_utils.data_generation.tests.factories import (
    TestCompanyFactory,
    TestContactInfoFactory,
    TestModelNonstandardCasingFactory,
    TestNationalIdFactory,
    TestPersonContactPhoneNumberFactory,
    TestPersonFactory
)
from edx_django_utils.data_generation.tests.models import (
    TestCompany,
    TestContactInfo,
    TestNationalId,
    TestPerson,
    TestPersonContactPhoneNumber,
    test_model_nonstandard_casing
)


class TestCommand(Command):
    """
    Class for use in testing manufacture_data command via run_from_argv
    """

    def check(self, *args):
        # Skip checks that aren't needed or configured in test suite
        pass


# Copied from django.core.management.__init__.py, with arg checking disabled given the open-ended nature of the
# model customizations we might need to specify.
# https://github.com/django/django/blob/1ad7761ee616341295f36c80f78b86ff79d5b513/django/core/management/__init__.py#L83
def call_command(command_name, *args, **options):
    """
    Call the given command, with the given options and args/kwargs.

    This is the primary API you should use for calling specific commands.

    `command_name` may be a string or a command object. Using a string is
    preferred unless the command object is required for further processing or
    testing.

    Some examples:
        call_command('migrate')
        call_command('shell', plain=True)
        call_command('sqlmigrate', 'myapp')

        from django.core.management.commands import flush
        cmd = flush.Command()
        call_command(cmd, verbosity=0, interactive=False)
        # Do something with cmd ...
    """
    app_name = get_commands()[command_name]
    command = load_command_class(app_name, command_name)

    # Simulate argument parsing to get the option defaults (see #10080 for details).
    parser = command.create_parser("", command_name)
    # Use the `dest` option name from the parser option
    opt_mapping = {
        min(s_opt.option_strings).lstrip("-").replace("-", "_"): s_opt.dest
        for s_opt in parser._actions  # pylint: disable=protected-access
        if s_opt.option_strings
    }
    arg_options = {opt_mapping.get(key, key): value for key, value in options.items()}
    parse_args = []

    defaults = parser.parse_args(args=parse_args)

    # pylint: disable=protected-access
    defaults = dict(
        defaults._get_kwargs(), **arg_options
    )

    # Move positional args out of options to mimic legacy optparse
    args = defaults.pop("args", ())
    if "skip_checks" not in options:
        defaults["skip_checks"] = True

    return command.execute(*args, **defaults)


@mark.django_db
class ManufactureDataCommandTests(TestCase):
    """
    Test command `manufacture_data`.
    """

    command = "manufacture_data"

    def test_command_requires_model(self):
        """
        Test that the manufacture_data command will raise an error if no model is provided.
        """
        with self.assertRaises(CommandError):
            call_command(self.command)

    def test_command_requires_valid_model(self):
        """
        Test that the manufacture_data command will raise an error if the provided model is invalid.
        """
        with self.assertRaises(CommandError):
            call_command(self.command, model="FakeModel")

    def test_single_object_create_no_customizations(self):
        """
        Test that the manufacture_data command will create a single object with no customizations.
        """
        assert TestPerson.objects.all().count() == 0
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPerson",
        )
        assert TestPerson.objects.all().count() == 1
        assert TestPerson.objects.filter(pk=created_object).exists()

    def test_command_requires_valid_field(self):
        """
        Test that the manufacture_data command will raise an error if the provided field is invalid.
        """
        with self.assertRaises(CommandError):
            call_command(
                self.command,
                model="TestPerson",
                field_customizations={"fake_field": "fake_value"},
            )

    def test_command_can_customize_fields(self):
        """
        Test that the manufacture_data command will create a single object with customizations.
        """
        assert TestPerson.objects.all().count() == 0
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPerson",
            field_customizations={"first_name": "Steve"},
        )
        assert TestPerson.objects.all().count() == 1
        assert TestPerson.objects.filter(pk=created_object).exists()
        assert (
            TestPerson.objects.filter(pk=created_object).first().first_name == "Steve"
        )

    def test_command_can_customize_nested_objects(self):
        """
        Test that the manufacture_data command supports customizing nested objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestContactInfo",
            field_customizations={
                "address": "123 4th st",
                "test_person__first_name": "Joey",
                "test_person__last_name": "Nowhere",
            },
        )
        assert TestPerson.objects.all().count() == 2
        assert TestContactInfo.objects.all().count() == 1
        assert (
            TestContactInfo.objects.filter(pk=created_object)
            .first()
            .test_person.last_name
            == "Nowhere"
        )

    def test_command_can_customize_doubly_nested_objects(self):
        """
        Test that the manufacture_data command supports customizing nested objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPersonContactPhoneNumber",
            field_customizations={
                "phone_number": "(000) 000-0000",
                "test_contact_info__test_person__first_name": "Joey",
                "test_contact_info__test_person__last_name": "Nowhere",
                "test_contact_info__address": "123 4th st",
            },
        )
        assert TestPerson.objects.all().count() == 2
        assert TestContactInfo.objects.all().count() == 1
        assert (
            TestContactInfo.objects.filter(pk=created_object)
            .first()
            .test_person.last_name
            == "Nowhere"
        )

    def test_command_can_customize_multiple_nested_objects(self):
        """
        Test that the manufacture_data command supports customizing nested objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPersonContactPhoneNumber",
            field_customizations={
                "phone_number": "(000) 000-0000",
                "test_contact_info__test_person__first_name": "Joey",
                "test_contact_info__test_company__company_name": "JoeyCo",
                "test_contact_info__address": "123 4th st",
            },
        )
        assert TestPerson.objects.all().count() == 2
        assert TestContactInfo.objects.all().count() == 1
        assert (
            TestContactInfo.objects.filter(pk=created_object)
            .first()
            .test_person.first_name
            == "Joey"
        )
        assert (
            TestCompany.objects.filter(company_name='JoeyCo')
            .count() == 1
        )

    def test_command_can_customize_nested_objects_with_fk(self):
        """
        Test that the manufacture_data command supports customizing nested objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        test_id = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestNationalId",
        )

        call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPersonContactPhoneNumber",
            field_customizations={
                "test_contact_info__test_person__national_id": test_id,
                "test_contact_info__test_company__national_id": test_id,
            },
        )
        assert TestPerson.objects.all().count() == 2
        assert TestCompany.objects.all().count() == 1
        assert TestContactInfo.objects.all().count() == 1
        assert TestNationalId.objects.filter(pk=test_id).count() == 1

    def test_command_builds_chains_of_pk(self):
        """
        Test that the manufacture_data command supports customizing nested objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        joe = TestPersonFactory()

        call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPersonContactPhoneNumber",
            field_customizations={
                "test_contact_info__test_person": f"{joe.pk}",
                "test_contact_info__test_company__ceo": f"{joe.pk}",
            },
        )
        assert TestPerson.objects.all().count() == 1
        assert TestCompany.objects.all().count() == 1
        assert TestContactInfo.objects.all().count() == 1

    def test_command_cannot_edit_created_fk(self):
        """
        Error case: trying to edit foreign key after foreign key object has already been created
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0

        with self.assertRaises(CommandError) as cm:
            call_command(
                self.command,
                model="edx_django_utils.data_generation.tests.models.TestPersonContactPhoneNumber",
                field_customizations={
                    "phone_number": "(000) 000-0000",
                    "test_contact_info__test_person__first_name": "Joey",
                    "test_contact_info__test_person": "0",
                },
            )
        assert str(cm.exception) == 'Provided FK value: 0 does not exist on TestPerson'

    def test_command_cannot_customize_foreign_keys(self):
        """
        Error case: customizing provided objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        test_person = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPerson",
            field_customizations={"first_name": "Steve"},
        )
        with self.assertRaises(CommandError) as cm:
            call_command(
                self.command,
                model="edx_django_utils.data_generation.tests.models.TestContactInfo",
                field_customizations={
                    "address": "123 4th st",
                    "test_person": test_person,
                    "test_person__last_name": "Harvey",
                },
            )
        assert str(cm.exception) == 'This script cannot modify existing objects'

    def test_command_cannot_customize_nested_foreign_keys(self):
        """
        Error case: customizing nested provided objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        test_person = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPerson",
            field_customizations={"first_name": "Steve"},
        )
        with self.assertRaises(CommandError) as cm:
            call_command(
                self.command,
                model="edx_django_utils.data_generation.tests.models.TestPersonContactPhoneNumber",
                field_customizations={
                    "phone_number": "(000) 000-0000",
                    "test_contact_info__test_person__first_name": "Joey",
                    "test_contact_info__test_person": test_person,
                    "test_contact_info__address": "123 4th st",
                },
            )
        assert str(cm.exception) == 'This script does not support customizing provided existing objects'

    def test_command_object_foreign_key(self):
        """
        Test that the manufacture_data command supports creating objects with foreign keys
        """
        assert TestPerson.objects.all().count() == 0
        foreign_key_object_id = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestPerson",
            field_customizations={"first_name": "Steve"},
        )
        assert TestPerson.objects.all().count() == 1
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.TestContactInfo",
            field_customizations={"test_person": foreign_key_object_id},
        )
        assert (
            TestContactInfo.objects.filter(pk=created_object)
            .first()
            .test_person.first_name
            == "Steve"
        )

    def test_argv_command_can_customize_nested_objects(self):
        """
        argv: Test that the manufacture_data command supports customizing nested objects.
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        command = TestCommand()

        command.run_from_argv(
            [
                "manage.py",
                "manufacture_data",
                "--model",
                "edx_django_utils.data_generation.tests.models.TestContactInfo",
                "--test_person__last_name",
                "Nowhere",
            ]
        )
        assert TestPerson.objects.all().count() == 2
        assert TestContactInfo.objects.all().count() == 1
        assert TestContactInfo.objects.first().test_person.last_name == "Nowhere"

    def test_argv_command_error(self):
        """
        argv error: Nested model does not exist
        """
        assert TestPerson.objects.all().count() == 0
        assert TestContactInfo.objects.all().count() == 0
        command = TestCommand()

        with self.assertRaises(SystemExit):
            command.run_from_argv(
                [
                    "manage.py",
                    "manufacture_data",
                    "--model",
                    "edx_django_utils.data_generation.tests.models.ThisModelDoesNotExist",
                ]
            )

    @mock.patch('edx_django_utils.data_generation.management.commands.manufacture_data.Command.handle')
    def test_argv_system_check_error(self, handleMock):
        """
        argv error: SystemCheckError
        """
        handleMock.side_effect = SystemCheckError(mock.Mock('SystemCheckError'))
        command = TestCommand()

        with self.assertRaises(SystemExit):
            command.run_from_argv(
                [
                    "manage.py",
                    "manufacture_data",
                    "--model",
                    "edx_django_utils.data_generation.tests.models.TestPerson",
                ]
            )

    def test_nonstandard_casing(self):
        """
        Test that the manufacture_data command will work with models that use non-standard casing
        """
        assert test_model_nonstandard_casing.objects.all().count() == 0
        created_object = call_command(
            self.command,
            model="edx_django_utils.data_generation.tests.models.test_model_nonstandard_casing",
        )
        assert test_model_nonstandard_casing.objects.all().count() == 1
        assert test_model_nonstandard_casing.objects.filter(pk=created_object).exists()

    def test_command_nested_nonexistent_model(self):
        """
        Error case: Nested model does not exist
        """
        with self.assertRaises(CommandError):
            call_command(
                self.command,
                model="edx_django_utils.data_generation.tests.models.TestContactInfo",
                field_customizations={
                    "address": "123 4th st",
                    "test_nonperson__last_name": "non-name",
                },
            )

    def test_command_nested_nonexistent_attribute(self):
        """
        Error case: Nested model does not exist
        """
        with self.assertRaises(CommandError):
            call_command(
                self.command,
                model="edx_django_utils.data_generation.tests.models.TestContactInfo",
                field_customizations={
                    "address": "123 4th st",
                    "test_person__middle_name": "Milhaus",
                },
            )

    def test_node_no_factory(self):
        """
        Node error case: no factory provided
        """
        node = Node(field_name='field', model_name='model')
        with self.assertRaises(CommandError):
            node.build_records()

    def test_node_str(self):
        """
        Node __str__ test
        """
        node = Node(field_name='model', model_name='model')
        node.add_child(Node(field_name='field', field_path='model.field', model_name='model'))
        assert str(node) == "<Tree Node (model)> fields: {}\n\t<Tree Node model.field(model)> fields: {}\n"
