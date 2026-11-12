Getting Started
===============

If you have not already done so, install `uv`_, then create and activate the project
virtualenv at ``.venv``. ``uv sync`` ignores any other active virtualenv, so run the
commands below with ``.venv`` activated::

    uv venv
    source .venv/bin/activate

.. _uv: https://docs.astral.sh/uv/


Install dependencies
--------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements
