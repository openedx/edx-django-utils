"""
Management command for making instances of models with test factories.

Arguments:
    model: complete path to a model that has a corresponding test factory
    {model_attribute}: (Optional) Value of a model's attribute that will override test factory's default value
    {model_foreignkey__foreignkey_attribute}: (Optional) Value of a model's attribute
        that will override test factory's default attribute value
"""

import logging
import sys

import factory
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError, SystemCheckError, handle_default_options
from django.db import connections
from factory.declarations import SubFactory

log = logging.getLogger(__name__)


def is_snake_name(name):
    """
    Helper method to detect if name is snake_case (lowercase separated by underscores).

    Arguments:
        name: word to test if it follows snake_case convention
    """
    return '_' in name or name.islower()


def convert_to_pascal_if_needed(name):
    """
    Helper method to convert snake_cased names to Pascal(CapWords) case.

    Arguments:
        name: word to convert to PascalCase, if it is snake_case
    """
    if not is_snake_name(name):
        return name.replace("_", " ").title().replace(" ", "")
    else:
        return name


def pairwise(iterable):
    """
    Convert a list into a list of tuples of adjacent elements.

    s -> [ (s0, s1), (s2, s3), (s4, s5), ... ]
    Arguments:
        iterable: List to convert
    """
    a = iter(iterable)
    return zip(a, a)


def all_subclasses(cls):
    """
    Recursively get all subclasses of a class

    https://stackoverflow.com/a/3862957
    Arguments:
        cls: class to get subclasses for
    """
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)])


def all_non_abstract_subfactories():
    """
    Get all non-abstract subclasses of DjangoModelFactory
    Based on our operating definition of 'Abstract' (Given there isn't native support for abstract classes in python).
    If a DjangoModelFactory has a meta model defined, we assume it is non-abstract.
    """
    def is_non_abstract_subclass(subclass):
        if subclass._meta:
            f_model = subclass._meta.get_model_class()
            return f_model and f_model.__name__ is not None
        return False
    return filter(is_non_abstract_subclass, all_subclasses(factory.django.DjangoModelFactory))


class Node():
    """
    Non-binary tree node class for building out a dependency tree of objects to create with customizations.
    """
    def __init__(self, model_name, field_name=None, field_path=None):
        """
        Arguments:
            model_name: Name of the model to instantiate (Example: TestPerson)
            field_name: Name of the field to be instantiated (Example: test_person))
            field_path: Full path hierarchy of the field to be instantiated
                (Example: TestPersonContactPhoneNumber.test_contact_info.test_person)
        """
        self.field_name = field_name
        self.field_path = field_path
        self.model_name = model_name
        self.children = []
        self.customizations = {}
        self.factory = None
        self.instance = None

    def set_single_customization(self, field, value):
        """
        Set a single customization value to the current node, overrides existing values under the same key.

        Arguments:
            field: Field for node's model
            value: Value to set field to
        """
        self.customizations[field] = value

    def add_child(self, child_node):
        """
        Add a child to the current node

        Arguments:
            child_node: Child node object to add
        """
        self.children.append(child_node)

    def find_node(self, field_path):
        """
        Find a node in the tree by path

        Arguments:
            field_path: Full path hierarchy of the node to find
                (Example: TestPersonContactPhoneNumber.test_contact_info.test_person)
        """
        if self.field_path == field_path:
            return self
        else:
            for child in self.children:
                found = child.find_node(field_path)
                if found:
                    return found
            return None

    def build_records(self):
        """
        Recursively build out the tree of objects by first dealing with children nodes before getting to the parent.
        """
        built_children = {}
        for child in self.children:
            # if we have an instance, use it instead of creating more objects
            if child.instance:
                built_children.update({child.field_name: child.instance})
            else:
                # Use the output of child ``build_records`` to create the current level.
                built_child = child.build_records()
                built_children.update(built_child)

        # The data factory kwargs are specified custom fields + the PK's of generated child objects
        object_fields = self.customizations.copy()
        object_fields.update(built_children)

        # Some edge case sanity checking
        if not self.factory:
            raise CommandError(f"Cannot build objects as {self} does not have a factory")

        built_object = self.factory(**object_fields)
        object_data = {self.field_name: built_object}
        return object_data

    def __str__(self, level=0):
        """
        Overridden str method to allow for proper tree printing

        Arguments:
            level: Depth of node in the hierarchy, affecting indentation
        """
        if self.instance:
            body = f"PK: {self.instance.pk}"
        else:
            body = f"fields: {self.customizations}"
        ret = ("\t" * level) + f"{repr(self)} {body}" + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

    def __repr__(self):
        """
        Overridden repr
        """
        return f'<Tree Node {self.field_path or ""}({self.model_name})>'


def build_tree_from_field_list(list_of_fields, provided_factory, base_node, customization_value):
    """
    Builds a non-binary tree of nodes based on a list of children nodes, using a base node and its associated data
    factory as the parent node the user provided value as a reference to a potential, existing record.

    Arguments:
        list_of_fields (list of strings): the linked list of associated objects to create. Example-
            ['enterprise_customer_user', 'enterprise_customer', 'site']
        provided_factory (factory.django.DjangoModelFactory): The data factory of the base_node.
        base_node (Node): The parent node of the desired tree to build.
        customization_value (string): The value to be assigned to the object associated with the last value in the
            ``list_of_fields`` param. Can either be a FK if the last value is a subfactory, or alternatively
            a custom value to be assigned to the field. Example-
            list_of_fields = ['enterprise_customer_user', 'enterprise_customer', 'site'],
            customization_value = 9
            or
            list_of_fields = ['enterprise_customer_user', 'enterprise_customer', 'name'],
            customization_value = "FRED"
    """
    current_factory = provided_factory
    current_node = base_node
    current_field_path = ''
    for index, field_name in enumerate(list_of_fields):
        try:
            current_field_path += field_name
            # First we need to figure out if the current field is a sub factory or not
            f = getattr(current_factory, field_name)
            if isinstance(f, SubFactory):
                fk_object = None
                f_model = f.get_factory()._meta.get_model_class()

                # if we're at the end of the list
                if index == len(list_of_fields) - 1:
                    # verify that the provided customization value is a valid pk for the model
                    try:
                        fk_object = f_model.objects.get(pk=customization_value)
                    except f_model.DoesNotExist as exc:
                        raise CommandError(
                            f"Provided FK value: {customization_value} does not exist on {f_model.__name__}"
                        ) from exc

                # Look for the node in the tree
                if node := current_node.find_node(current_field_path):
                    # Not supporting customizations and FK's
                    if (bool(node.customizations) or bool(node.children)) and bool(fk_object):
                        raise CommandError("This script does not support customizing provided existing objects")
                    # Set current node and move on
                    current_node = node
                else:
                    # Create a new node
                    node = Node(
                        field_name=field_name,
                        model_name=f_model.__name__,
                        field_path=current_field_path
                    )
                    node.factory = f.get_factory()
                    # If we found the valid FK earlier, assign it to the node
                    if fk_object:
                        node.instance = fk_object
                    # Add the field to the children of the current node
                    current_node.add_child(node)

                current_node = node
                current_factory = f.get_factory()
            else:
                if current_node.instance:
                    raise CommandError("This script cannot modify existing objects")
                current_node.set_single_customization(field_name, customization_value)
        except AttributeError as exc:
            log.error(f'Could not find field name: {field_name} in factory: {current_factory}')
            raise CommandError(f'Could not find field_name: {field_name} in factory: {current_factory}') from exc
        current_field_path += '.'
    return base_node


class Command(BaseCommand):
    """
    Management command for generating Django records from factories with custom attributes

    Example usage:
        $ ./manage.py manufacture_data --model enterprise.models.enterprise_customer \
            --name "Test Enterprise" --slug "test-enterprise"
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            dest='model',
            help='The model for which the record will be written',
        )

    def run_from_argv(self, argv):
        """
        Re-implemented from https://github.com/django/django/blob/main/django/core/management/base.py#L395 in order to
        support individual field customization. We will need to keep this method up to date with our current version of
        Django BaseCommand.

        Uses ``parse_known_args`` instead of ``parse_args`` to not throw an error when encountering unknown arguments

        https://docs.python.org/3.8/library/argparse.html#argparse.ArgumentParser.parse_known_args
        Arguments:
            argv: list of command line arguments passed to management command
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])
        options, unknown = parser.parse_known_args(argv[2:])

        # Add the unknowns into the options for use of the handle method
        paired_unknowns = pairwise(unknown)
        field_customizations = {}
        for field, value in paired_unknowns:
            field_customizations[field.strip("--")] = value
        options.field_customizations = field_customizations

        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        handle_default_options(options)
        try:
            self.execute(*args, **cmd_options)
        except CommandError as e:
            if options.traceback:
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write("%s: %s" % (e.__class__.__name__, e))
            sys.exit(e.returncode)
        finally:
            try:
                connections.close_all()
            except ImproperlyConfigured:
                # Ignore if connections aren't setup at this point (e.g. no
                # configured settings).
                pass

    def handle(self, *args, **options):
        """
        Entry point for management command execution.

        Arguments:
            args: list of command line arguments passed to management command
            options: dict of command line argument key/values
        """
        if not options.get('model'):
            log.error("Did not receive a model")
            raise CommandError("Did not receive a model")
        # Convert to Pascal case if the provided name is snake case/is all lowercase
        path_of_model = options.get('model').split(".")
        last_path = convert_to_pascal_if_needed(path_of_model[-1])

        provided_model = '.'.join(path_of_model[:-1]) + '.' + last_path
        # Get all installed/imported factories
        factories_list = all_non_abstract_subfactories()
        # Find the factory that matches the provided model
        for potential_factory in factories_list:
            # Fetch the model for the factory
            factory_model = potential_factory._meta.model
            factory_model_name = factory_model.__name__
            # Check if the factories model matches the provided model
            if f"{factory_model.__module__}.{convert_to_pascal_if_needed(factory_model_name)}" == provided_model:
                # Now that we have the right factory, we can build according to the provided custom attributes
                field_customizations = options.get('field_customizations', {})
                base_node = Node(field_name=factory_model_name, model_name=factory_model_name)
                base_node.factory = potential_factory
                # For each provided custom attribute...
                for field, value in field_customizations.items():

                    # We need to build a tree of objects to be created and may be customized by other custom attributes
                    stripped_field = field.strip("--")
                    fk_field_customization_split = stripped_field.split("__")
                    base_node = build_tree_from_field_list(
                        fk_field_customization_split,
                        potential_factory,
                        base_node,
                        value,
                    )

                built_node = base_node.build_records()
                log.info(f"\nGenerated factory data: \n{base_node}")
                return str(list(built_node.values())[0].pk)

        log.error(f"Provided model: {provided_model} does not exist or does not have an associated factory")
        raise CommandError(f"Provided model: {provided_model}'s factory is not imported or does not exist")
