#!/usr/bin/env python
# Note: pylint disable of useless-suppression is required because the errors
# are different for python 2.7 and python 3.6.
# pylint: disable=C0111,useless-suppression
"""
Package metadata for edx-django-utils.
"""

import os
import re
import sys

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename, encoding="utf8").read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Requirements will include any constraints from files specified
    with -c in the requirements files.
    Returns a list of requirement strings.
    """
    # UPDATED VIA SEMGREP - if you need to remove/modify this method remove this line and add a comment specifying why.

    # e.g. {"django": "Django", "confluent-kafka": "confluent_kafka[avro]"}
    by_canonical_name = {}

    def check_name_consistent(package):
        """
        Raise exception if package is named different ways.

        This ensures that packages are named consistently so we can match
        constraints to packages. It also ensures that if we require a package
        with extras we don't constrain it without mentioning the extras (since
        that too would interfere with matching constraints.)
        """
        canonical = package.lower().replace('_', '-').split('[')[0]
        seen_spelling = by_canonical_name.get(canonical)
        if seen_spelling is None:
            by_canonical_name[canonical] = package
        elif seen_spelling != package:
            raise Exception(
                f'Encountered both "{seen_spelling}" and "{package}" in requirements '
                'and constraints files; please use just one or the other.'
            )

    requirements = {}
    constraint_files = set()

    # groups "pkg<=x.y.z,..." into ("pkg", "<=x.y.z,...")
    re_package_name_base_chars = r"a-zA-Z0-9\-_."  # chars allowed in base package name
    # Two groups: name[maybe,extras], and optionally a constraint
    requirement_line_regex = re.compile(
        r"([%s]+(?:\[[%s,\s]+\])?)([<>=][^#\s]+)?"
        % (re_package_name_base_chars, re_package_name_base_chars)
    )

    def add_version_constraint_or_raise(current_line, current_requirements, add_if_not_present):
        regex_match = requirement_line_regex.match(current_line)
        if regex_match:
            package = regex_match.group(1)
            version_constraints = regex_match.group(2)
            check_name_consistent(package)
            existing_version_constraints = current_requirements.get(package, None)
            # It's fine to add constraints to an unconstrained package,
            # but raise an error if there are already constraints in place.
            if existing_version_constraints and existing_version_constraints != version_constraints:
                raise BaseException(f'Multiple constraint definitions found for {package}:'
                                    f' "{existing_version_constraints}" and "{version_constraints}".'
                                    f'Combine constraints into one location with {package}'
                                    f'{existing_version_constraints},{version_constraints}.')
            if add_if_not_present or package in current_requirements:
                current_requirements[package] = version_constraints

    # Read requirements from .in files and store the path to any
    # constraint files that are pulled in.
    for path in requirements_paths:
        with open(path) as reqs:
            for line in reqs:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, True)
                if line and line.startswith('-c') and not line.startswith('-c http'):
                    constraint_files.add(os.path.dirname(path) + '/' + line.split('#')[0].replace('-c', '').strip())

    # process constraint files: add constraints to existing requirements
    for constraint_file in constraint_files:
        with open(constraint_file) as reader:
            for line in reader:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, False)

    # process back into list of pkg><=constraints strings
    constrained_requirements = [f'{pkg}{version or ""}' for (pkg, version) in sorted(requirements.items())]
    return constrained_requirements


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment,
        a URL, or an included file
    """
    # UPDATED VIA SEMGREP - if you need to remove/modify this method remove this line and add a comment specifying why

    return line and line.strip() and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


VERSION = get_version('edx_django_utils', '__init__.py')

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

README = open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding="utf8").read()
CHANGELOG = open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst'), encoding="utf8").read()

setup(
    name='edx-django-utils',
    version=VERSION,
    description="""EdX utilities for Django Application development.""",
    long_description=README + '\n\n' + CHANGELOG,
    long_description_content_type="text/x-rst",
    author='edX',
    author_email='oscm@edx.org',
    url='https://github.com/openedx/edx-django-utils',
    packages=[
        'edx_django_utils',
    ],
    include_package_data=True,
    install_requires=load_requirements('requirements/base.in'),
    entry_points={
        'console_scripts': [
            'log-sensitive = edx_django_utils.logging.internal.log_sensitive:cli',
        ],
    },
    zip_safe=False,
    keywords='Django edx',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
