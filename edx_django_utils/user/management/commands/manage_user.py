"""
Management command `manage_user` is used to idempotently create or remove
Django users, set/unset permission bits, and associate groups by name.
"""


from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher, is_password_usable
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.translation import gettext as _

from edx_django_utils.user import generate_password


def is_valid_django_hash(encoded):
    """
    Starting with django 2.1, the function is_password_usable no longer checks whether encode
    is a valid password created by a django hasher (hasher in  PASSWORD_HASHERS setting)

    Adding this function to create constant behavior as we upgrade django versions
    """
    try:
        identify_hasher(encoded)
    except ValueError:
        return False
    return True


class Command(BaseCommand):
    """Creates the specified user, if it does not exist, and sets its groups."""
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('--remove', dest='is_remove', action='store_true')
        parser.add_argument('--superuser', dest='is_superuser', action='store_true')
        parser.add_argument('--staff', dest='is_staff', action='store_true')
        parser.add_argument('--unusable-password', dest='unusable_password', action='store_true')
        parser.add_argument('--initial-password-hash', dest='initial_password_hash')
        parser.add_argument('-g', '--groups', nargs='*', default=[])

    def _maybe_update(self, user, attribute, new_value):
        """
        DRY helper.  If the specified attribute of the user differs from the
        specified value, it will be updated.
        """
        old_value = getattr(user, attribute)
        if new_value != old_value:
            self.stderr.write(
                _('Setting {attribute} for user "{username}" to "{new_value}"').format(
                    attribute=attribute, username=user.username, new_value=new_value
                )
            )
            setattr(user, attribute, new_value)

    def _check_email_match(self, user, email):
        """
        DRY helper.

        Requiring the user to specify both username and email will help catch
        certain issues, for example if the expected username has already been
        taken by someone else.
        """
        if user.email.lower() != email.lower():
            # The passed email address doesn't match this username's email address.
            # Assume a problem and fail.
            raise CommandError(
                _(
                    'Skipping user "{}" because the specified and existing email '
                    'addresses do not match.'
                ).format(user.username)
            )

    def _handle_remove(self, username, email):
        """
        If a user with the given username and email exists, delete them.
        """
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            self.stderr.write(_('Did not find a user with username "{}" - skipping.').format(username))
            return
        self._check_email_match(user, email)
        self.stderr.write(_('Removing user: "{}"').format(user))
        user.delete()

    @transaction.atomic
    def handle(  # pylint: disable=arguments-differ
        self, username, email, is_remove, is_staff, is_superuser, groups,
        unusable_password, initial_password_hash, *args, **options
    ):

        if is_remove:
            self._handle_remove(username, email)
            return

        old_groups, new_groups = set(), set()
        user, created = get_user_model().objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if created:
            if initial_password_hash:
                if not (is_password_usable(initial_password_hash) and is_valid_django_hash(initial_password_hash)):
                    raise CommandError(f'The password hash provided for user {username} is invalid.')
                user.password = initial_password_hash
            else:
                # Set the password to a random, unknown, but usable password
                # allowing self-service password resetting.  Cases where unusable
                # passwords are required, should be explicit, and will be handled below.
                user.set_password(generate_password(length=25))
            self.stderr.write(_('Created new user: "{}"').format(user))
        else:
            # NOTE, we will not update the email address of an existing user.
            self.stderr.write(_('Found existing user: "{}"').format(user))
            self._check_email_match(user, email)
            old_groups = set(user.groups.all())

        self._maybe_update(user, 'is_staff', is_staff)
        self._maybe_update(user, 'is_superuser', is_superuser)

        # Set unusable password if specified
        if unusable_password and user.has_usable_password():
            self.stderr.write(_('Setting unusable password for user "{}"').format(user))
            user.set_unusable_password()

        # resolve the specified groups
        for group_name in groups or set():

            try:
                group = Group.objects.get(name=group_name)
                new_groups.add(group)
            except Group.DoesNotExist:
                # warn, but move on.
                self.stderr.write(_('Could not find a group named "{}" - skipping.').format(group_name))

        add_groups = new_groups - old_groups
        remove_groups = old_groups - new_groups

        self.stderr.write(
            _(
                'Adding user "{username}" to groups {group_names}'
            ).format(
                username=user.username,
                group_names=[g.name for g in add_groups]
            )
        )
        self.stderr.write(
            _(
                'Removing user "{username}" from groups {group_names}'
            ).format(
                username=user.username,
                group_names=[g.name for g in remove_groups]
            )
        )

        user.groups.set(new_groups)
        user._called_by_management_command = True  # pylint: disable=protected-access
        user.save()
