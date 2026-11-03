Django Data Generation
######################


Setting up in new repository
============================
* Create management command `manufacture_data` 
    * Command class must inherit from `edx_django_utils.data_generation.management.commands.manufacture_data.Command` as BaseCommand
    * Command class file must import model factory classes

Example from https://github.com/openedx/enterprise-catalog/pull/734

.. code-block:: python

	from edx_django_utils.data_generation.management.commands.manufacture_data import Command as BaseCommand
	from enterprise_catalog.apps.catalog.tests.factories import *
	class Command(BaseCommand):
	# No further code needed

Usage
=====

(Using https://github.com/openedx/edx-enterprise/blob/master/enterprise/models.py through Devstack as an example)

Generating Basic Model
----------------------
Upon invoking the command, supply a model param (--model) that is a complete path to a model that has a corresponding test factory:

`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomer`

This will generate an enterprise customer record with place holder values according to the test factory

Customizing Model Values
------------------------
We can also provide customizations to the record being generated:

`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomer --name "FRED"`
	
	'EnterpriseCustomer' fields: {'name': 'FRED'}

We can supply parent model/subfactory customizations as well (using django ORM query syntax):

`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomerCatalog --enterprise_customer__site__name "Fred" --enterprise_catalog_query__title "JOE SHMO" --title "who?"`
	
	'EnterpriseCustomerCatalog' fields: {'title': 'who?'}
		'EnterpriseCustomer' fields: {}
			'Site' fields: {'name': 'Fred'}

		'EnterpriseCatalogQuery' fields: {'title': 'JOE SHMO'}

Note the non subclass customization --title "who?" is applied to the specified model EnterpriseCustomerCatalog

Customizing Foreign Keys
------------------------
Say we want to supply an existing record as a FK to our object:

`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomerUser --enterprise_customer 994599e6-3787-48ba-a2d1-42d1bdf6c46e`
	
	'EnterpriseCustomerUser' fields: {}
		'EnterpriseCustomer' PK: 994599e6-3787-48ba-a2d1-42d1bdf6c46e

or we can do something like:
`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomerUser --enterprise_customer__site 9 --enterprise_customer__name "joe"`

	'EnterpriseCustomerUser' fields: {}
		'EnterpriseCustomer' fields: {'name': 'joe'}
			'Site' PK: 9

Unsupported Cases
-----------------
One limitation of this script is that it can only customize objects it generates, and cannot customize existing objects specfied with FK:

To illustrate:

`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomerUser --enterprise_customer__site__name "fred" --enterprise_customer 994599e6-3787-48ba-a2d1-42d1bdf6c46e`

would yield 
`CommandError: This script does not support customizing provided existing objects`

Error Cases
-----------

If you try and get something that doesn't exist:

`./manage.py lms manufacture_data --model enterprise.models.EnterpriseCustomerUser --enterprise_customer <invalid uuid>`

we'd get:
`CommandError: Provided FK value: <invalid uuid> does not exist on EnterpriseCustomer`
