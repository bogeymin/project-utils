*********************
Developer's Reference
*********************

New Command Checklist
=====================

1. Create the command in the ``cli.py`` module.
2. Create a corresponding file in the ``sandbox/``.
3. Update ``commands.rst``.
4. Update *The Commands* section of the ``README.markdown``.
5. Add any new modules to ``reference.rst``.

Command Line Module (CLI)
=========================

The ``cli.py`` module contains the entry points for command line utilities. It utilizes resources from the ``library/``
to create useful commands.

Commands
--------

Separation
..........

Commands are separated into different functions in ``cli.py``. The objectives of a command function are:

- Provide the user interface.
- Handle logic that is dependent upon the user, including variables, configuration, etc.
- Avoid logic that is re-usable. This code should be in the library modules.

Naming Convention
.................

Naming is always a challenge, especially on the command line.

- Shorter names are better than longer names. Usually.
- We prefer the convention of action + object. For example, bump + version, or ``bumpversion``.
- It's okay to use short names or abbreviations for the object when the name is idiomatic. For example, random + pw, or
  ``randompw``.
- If the action is something that is already common on most operating systems, use it. For example ls + projects, or
  ``lsprojects``.
- Names can't conflict with existing commands. Obviously.

Entry Points
............

We are using `entry points`_ to make setup possible via ``pip``. New commands must be added to ``entry_points`` in
``setup.py``. See examples there.

.. _entry points: http://stackoverflow.com/a/9615473/241720

Modules
-------

Separation
..........

We maintain a fairly strict separation between re-usable module code and the code in the command line functions.

Module code should capture errors.

Naming Conventions
..................

We use the following conventions when naming modules:

- Module names should be plural.

Library
=======

Library resources are given in alphabetical order.

Colors
------

.. automodule:: library.colors
    :members:

Config
------

.. automodule:: library.config
    :members:

Constants
---------

.. automodule:: library.constants
    :members:

Exceptions
----------

.. automodule:: library.exceptions
    :members:

Issues
------

.. automodule:: library.issues
    :members:

Organizations
-------------

.. automodule:: library.organizations
    :members:

Packaging
---------

.. automodule:: library.packaging
    :members:

Passwords
---------

.. automodule:: library.passwords
    :members:

Projects
--------

.. automodule:: library.projects
    :members:

Releases
--------

.. automodule:: library.releases
    :members:

Repos
-----

.. automodule:: library.repos
    :members:

Shortcuts
---------

.. automodule:: library.shortcuts
    :members:
