Hooks tooling: pipeline for filters
===================================

Status
------

Draft

Context
-------

Taking into account the design considerations outlined in OEP-50 Hooks extension framework about

1. The order of execution for multiple actions must be respected
2. The result of a previous function must be available to the current one

We must implement a pattern that follows this considerations: a Pipeline for the set of functions, i.e filters,
listening on a trigger.

Checkout https://github.com/edx/open-edx-proposals/pull/184 for more information.

To do this, we considered three similar approaches for the pipeline implementation:

1. Unix-like (how unix pipe operator works): the output of the previous function is the input of the next one. For the first function, includes the initial arguments.
2. Unix-like modified: the output of the previous function is the input of the next one including the initial arguments for all functions.
3. Accumulative: the output of every (i, …, i-n) function is accumulated using a data structure and fed into the next function i-n+1, including the initial arguments. We draw inspiration from
   python-social-auth/social-core, please checkout their repository: https://github.com/python-social-auth/social-core

These approaches follow the pipeline pattern and have as main difference what each function receive as input.

It is important to emphasize that the main objectives with this implementation are: to have function interchangeability and to maintain the signature of the functions across the Hooks Extension Framework.

Decision
--------

We decided to use the accumulative approach as the only pipeline for filters.

Consequences
------------

1. The order of execution is maintained.
2. Given that all pipeline functions will expect the same input arguments, i.e accumulated output plus initial arguments, their signature will stay the same. And for this reason, these functions are interchangeable.
3. For the above reason, filters must have \*args and \*\*kwargs in their signature.
