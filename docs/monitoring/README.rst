:orphan:

This README explains the purpose of this directory in the form of a decision document.

Context
-------

At this time, we don't have a standard way to pull in rst docs from outside of the main docs directory. See https://github.com/sphinx-doc/sphinx/issues/701 for details on this issue.

Decision
--------

Copy monitoring/docs files to the main docs directory, and use an include statement as a quick temporary solution to publishing docs with the following benefits:

* Original docs stay close to the code.
* Any old github references to the old locations would still be accurate.
* We may be able to implement a more automated solution in the future that doesn't break the new Readthedoc locations.

Consequences
------------

New docs need to be copied to be included in the index.rst, which is only one minor additional step.

Rejected Alternatives
---------------------

The following alternatives were temporarily rejected for the sake of expediency. The decision could be updated in more time were invested on this issue more globally.

#. Move the monitoring/docs folder under the main docs folder. This would break existing references to github docs. Someone could choose to make this change in the future.
#. Create sphinx plugin to automatically copy docs. This is a potentially good idea, but I am not investing in it at this time.
