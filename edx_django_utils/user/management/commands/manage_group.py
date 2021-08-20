"""
Management command `manage_group` is used to idempotently create Django groups
and set their permissions by name.
"""


from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.translation import gettext as _


class Command(BaseCommand):
    """Creates the specified group, if it does not exist, and sets its permissions."""
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('group_name')
        parser.add_argument('--remove', dest='is_remove', action='store_true')
        parser.add_argument('-p', '--permissions', nargs='*', default=[])

    def _handle_remove(self, group_name):
        """
        Remove the group named by the string group_name, if it exists.
        """

        try:
            Group.objects.get(name=group_name).delete()
            self.stderr.write(_('Removed group: "{}"').format(group_name))
        except Group.DoesNotExist:
            self.stderr.write(_('Did not find a group with name "{}" - skipping.').format(group_name))

    @transaction.atomic
    def handle(self, group_name, is_remove, permissions=None, **options):  # pylint: disable=arguments-differ

        if is_remove:
            self._handle_remove(group_name)
            return

        old_permissions = set()
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            try:
                # Needed for sqlite backend (i.e. in tests) because
                # name.max_length won't be enforced by the db.
                # See also http://www.sqlite.org/faq.html#q9
                group.full_clean()
            except ValidationError as exc:
                # give a more helpful error
                raise CommandError(
                    _(
                        'Invalid group name: "{group_name}". {messages}'
                    ).format(
                        group_name=group_name,
                        messages=exc.messages[0]
                    )
                ) from None
            self.stderr.write(_('Created new group: "{}"').format(group_name))
        else:
            self.stderr.write(_('Found existing group: "{}"').format(group_name))
            old_permissions = set(group.permissions.all())

        new_permissions = self._resolve_permissions(permissions or set())

        add_permissions = new_permissions - old_permissions
        remove_permissions = old_permissions - new_permissions

        self.stderr.write(
            _(
                'Adding {codenames} permissions to group "{group}"'
            ).format(
                codenames=[ap.name for ap in add_permissions],
                group=group.name
            )
        )
        self.stderr.write(
            _(
                'Removing {codenames} permissions from group "{group}"'
            ).format(
                codenames=[rp.codename for rp in remove_permissions],
                group=group.name
            )
        )

        group.permissions.set(new_permissions)

        group.save()

    def _resolve_permissions(self, permissions):
        """
        Given a list of permission strings in the format 'app_label:model:codename', return a list
        of Permission model instances.
        """
        new_permissions = set()
        for permission in permissions:
            try:
                app_label, model_name, codename = permission.split(':')
            except ValueError:
                # give a more helpful error
                raise CommandError(_(
                    'Invalid permission option: "{}". Please specify permissions '
                    'using the format: app_label:model_name:permission_codename.'
                ).format(permission)) from None
            # this will raise a LookupError if it fails.
            try:
                model_class = apps.get_model(app_label, model_name)
            except LookupError as exc:
                raise CommandError(str(exc)) from None

            # Fetch content type for model, including proxy models.
            content_type = ContentType.objects.get_for_model(model_class, for_concrete_model=False)
            try:
                new_permission = Permission.objects.get(
                    content_type=content_type,
                    codename=codename,
                )
            except Permission.DoesNotExist:
                # give a more helpful error
                raise CommandError(
                    _(
                        'Invalid permission codename: "{codename}".  No such permission exists '
                        'for the model {module}.{model_name}.'
                    ).format(
                        codename=codename,
                        module=model_class.__module__,
                        model_name=model_class.__name__,
                    )
                ) from None
            new_permissions.add(new_permission)
        return new_permissions
